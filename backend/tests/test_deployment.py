import asyncio
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableLambda
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.config import AI_PROVIDERS, Settings, get_embedding_fallback_chain
from app.main import create_app
from app.services.llm_service import LLMService
from app.services.vector_store import VectorStoreService


class FakeEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[1.0, float(len(t) % 7), 0.0] for t in texts]

    def embed_query(self, text):
        return [1.0, float(len(text) % 7), 0.0]


def pdf_bytes():
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=200)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
    )
    stream = DecodedStreamObject()
    stream.set_data(
        b"BT /F1 12 Tf 20 100 Td (The project supports PDF upload and document questions. The project name is Document RAG Chatbot.) Tj ET"
    )
    page[NameObject("/Contents")] = stream
    result = io.BytesIO()
    writer.write(result)
    return result.getvalue()


class DeploymentTests(unittest.TestCase):
    def settings(self, **kw):
        return Settings(
            _env_file=None,
            google_api_key="test-placeholder",
            enabled_providers="gemini",
            allowed_chat_models="gemini-2.5-flash-lite",
            allowed_embedding_models="gemini-embedding-001",
            local_embeddings_enabled=False,
            default_provider="gemini",
            default_model="gemini-2.5-flash-lite",
            **kw,
        )

    def test_allowlists_restrict_catalog_attempts_and_embeddings(self):
        settings = self.settings(
            openai_direct_api_key="test-placeholder", embedding_openai_direct=True
        )
        with (
            patch("app.config.get_settings", return_value=settings),
            patch("app.services.llm_service.get_settings", return_value=settings),
        ):
            llm = LLMService()
            self.assertEqual(
                [(p.name, m) for p, m in llm._llm_attempt_sequence("gpt-4o")],
                [("gemini", "gemini-2.5-flash-lite")],
            )
            self.assertEqual(
                [m["id"] for m in llm.get_available_models()], ["gemini-2.5-flash-lite"]
            )
            self.assertEqual(
                [(p.name, m) for p, m in get_embedding_fallback_chain()],
                [("gemini", "gemini-embedding-001")],
            )

    def test_remote_failure_never_loads_local_model(self):
        with tempfile.TemporaryDirectory() as temp:
            settings = self.settings(faiss_persist_dir=temp)
            with (
                patch("app.config.get_settings", return_value=settings),
                patch("app.services.vector_store.get_settings", return_value=settings),
            ):
                store = VectorStoreService("test-session")
                with (
                    patch.object(store, "_make_embeddings", side_effect=RuntimeError("offline")),
                    patch.object(store, "_make_local_cpu_embeddings") as local,
                ):
                    with self.assertRaises(RuntimeError):
                        store.create_from_documents([Document(page_content="test")])
                    local.assert_not_called()
                    path = Path(store._persist_path())
                    path.mkdir(parents=True)
                    (path / "index.faiss").touch()
                    store._try_load_from_disk()
                    local.assert_not_called()

    def test_stream_failure_after_output_does_not_mix_models(self):
        async def broken(_):
            yield "partial"
            raise RuntimeError("connection lost")

        async def run():
            llm = LLMService()
            tokens = []
            attempts = [(AI_PROVIDERS["gemini"], "first"), (AI_PROVIDERS["gemini"], "second")]
            with (
                patch.object(llm, "_llm_attempt_sequence", return_value=attempts),
                patch.object(llm, "_build_llm", return_value=RunnableLambda(broken)) as build,
            ):
                with self.assertRaisesRegex(RuntimeError, "interrupted"):
                    async for event in llm.stream_answer_with_failover("question", []):
                        tokens.append(event)
                self.assertEqual(build.call_count, 1)
                self.assertEqual([e["content"] for e in tokens], ["partial"])

        asyncio.run(run())

    def test_stream_can_fail_over_before_output(self):
        async def working(_):
            yield "complete answer"

        async def run():
            llm = LLMService()
            attempts = [(AI_PROVIDERS["gemini"], "first"), (AI_PROVIDERS["gemini"], "second")]
            with (
                patch.object(llm, "_llm_attempt_sequence", return_value=attempts),
                patch.object(
                    llm,
                    "_build_llm",
                    side_effect=[RuntimeError("offline"), RunnableLambda(working)],
                ),
            ):
                events = [e async for e in llm.stream_answer_with_failover("question", [])]
            self.assertEqual(events[-1], {"type": "complete", "model_used": "second"})

        asyncio.run(run())

    def test_health_cors_upload_session_isolation_and_answer(self):
        from contextlib import ExitStack

        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            settings = self.settings(
                faiss_persist_dir=temp,
                max_file_size=4096,
                CORS_ORIGINS="https://test.vercel.app",
                rate_limit_ask_per_minute=0,
                rate_limit_upload_per_minute=0,
            )
            for module in [
                "app.config",
                "app.main",
                "app.routes.health",
                "app.routes.upload",
                "app.services.vector_store",
                "app.services.llm_service",
                "app.services.pdf_processor",
                "app.services.faiss_session_cleanup",
                "app.services.ip_rate_limit",
            ]:
                stack.enter_context(patch(module + ".get_settings", return_value=settings))
            stack.enter_context(
                patch.object(VectorStoreService, "_make_embeddings", return_value=FakeEmbeddings())
            )
            stack.enter_context(
                patch.object(
                    LLMService,
                    "_generate_with_failover",
                    return_value=(
                        "The project name is Document RAG Chatbot.",
                        "gemini-2.5-flash-lite",
                    ),
                )
            )
            with TestClient(create_app()) as client:
                sid = {"X-Chat-Session-Id": "11111111-2222-4333-8444-555555555555"}
                other = {"X-Chat-Session-Id": "22222222-2222-4333-8444-555555555555"}
                self.assertEqual(client.get("/health").status_code, 200)
                cors = client.options(
                    "/upload",
                    headers={
                        "Origin": "https://test.vercel.app",
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "X-Chat-Session-Id",
                    },
                )
                self.assertEqual(
                    cors.headers["access-control-allow-origin"], "https://test.vercel.app"
                )
                self.assertEqual(
                    client.options(
                        "/upload",
                        headers={
                            "Origin": "https://untrusted.invalid",
                            "Access-Control-Request-Method": "POST",
                        },
                    ).status_code,
                    400,
                )
                self.assertEqual(
                    client.post(
                        "/upload", headers=sid, files={"file": ("large.pdf", b"x" * 4097)}
                    ).status_code,
                    400,
                )
                upload = client.post(
                    "/upload",
                    headers=sid,
                    files={"file": ("test.pdf", pdf_bytes(), "application/pdf")},
                )
                self.assertEqual(upload.status_code, 200, upload.text)
                self.assertTrue(client.get("/status", headers=sid).json()["pdf_loaded"])
                self.assertFalse(client.get("/status", headers=other).json()["pdf_loaded"])
                answer = client.post(
                    "/ask", headers=sid, json={"question": "What is the project name?"}
                )
                self.assertEqual(answer.status_code, 200, answer.text)
                self.assertIn("Document RAG Chatbot", answer.json()["answer"])
                self.assertEqual(
                    client.post(
                        "/ask", headers=other, json={"question": "What is the name?"}
                    ).status_code,
                    400,
                )
