# REQUIREMENTS.md — Cycle C1

Baseline requirements derived from **existing product behavior** and **documented gaps**.  
Status: `baseline` = already expected of current system; `proposed` = remediation/improvement pending Gate 1.

| ID | Statement | Status | Priority | Evidence / notes |
|----|-----------|--------|----------|------------------|
| REQ-0001 | User can upload a PDF and receive chunked embeddings into a session-scoped FAISS index | baseline | P0 | `POST /upload`, `SessionVectorRegistry` |
| REQ-0002 | User can ask questions with grounded answers from retrieved chunks | baseline | P0 | `POST /ask`, agent pipeline |
| REQ-0003 | User can stream answers via SSE and cancel in-flight streams | baseline | P0 | `POST /ask/stream`, `streamQuestion`, abort/generation guards |
| REQ-0004 | Anonymous browsers are isolated via `X-Chat-Session-Id` with LRU/age cleanup | baseline | P0 | chat-session.ts, FAISS session dirs |
| REQ-0005 | Model selection supports multi-provider failover when keys configured | baseline | P1 | `LLMService`, config providers |
| REQ-0006 | Optional source snippets can be shown on assistant messages | baseline | P2 | include-sources toggle |
| REQ-0007 | Chat history and prefs persist device-locally (IndexedDB / localStorage) | baseline | P1 | `storage.ts`, sessions panel |
| REQ-0008 | Frontend observability must not ship personal/demo secrets as hardcoded source defaults; DSN via env | **done** | P0 | Env-only DSN + drop localhost/dev in `sentry.ts` (2026-08-08) |
| REQ-0009 | Sentry client config must minimize unnecessary PII/replay exposure for a PDF-chat demo | **done** | P0 | `sendDefaultPii: false`, masked replay (2026-08-08) |
| REQ-0010 | Single chat-state implementation for `/chat` (no divergent parallel upload/ask logic) | proposed | P1 | `use-chat.ts` vs `chat-context.tsx` duplication |
| REQ-0011 | Planning docs match code (PROJECT_PLAN observability section; broken Redis guide link) | proposed | P1 | `docs/PROJECT_PLAN.md`, deleted guide |
| REQ-0012 | Critical API paths have automated regression tests beyond SSE happy-path stub | proposed | P2 | only `tests/test_chat_stream_sse.py` |
| REQ-0013 | Free-tier-first model catalogs (OpenRouter `:free`, Groq gpt-oss/Qwen, Gemini Flash) stay aligned with live providers + `docs/LLM_MODEL_SELECTION.md` | **done** | P0 | `config.py` + `AI_MODELS` updated 2026-08-08 |

### Explicitly deferred (not C1 Wave 1 unless approved)

- Auth / multi-tenant SaaS accounts
- Redis job queue / server-side history
- Playwright E2E suite
- PostHog / Redis observability stack

## Frontend refactoring — 2026-10-12

- REQ-0014: Remove the API Status dashboard from frontend display, including its route and desktop/mobile links. User authorized this scoped removal. Keep API Docs, the header health indicator, and backend endpoints. Done; validation recorded in VALIDATION_SUMMARY.md.

- REQ-0015: Rename the displayed application to Document RAG Chatbot across frontend branding, HTML metadata, backend API naming, and README title. Preserve storage/session identifiers and repository URLs. Done; validation recorded in VALIDATION_SUMMARY.md.

- REQ-0016 (2026-10-13): Remove API documentation navigation from the frontend, including desktop/mobile API Docs links, the mobile API section heading, and unused imports. User authorized. Supersedes REQ-0014's retention of the frontend API Docs link; backend docs endpoints remain outside this UI scope. Done; validation recorded in VALIDATION_SUMMARY.md.

- REQ-0017 (2026-10-13): Replace the frontend blue/purple theme accents with light orange/peach across highlighted text, buttons, navigation, badges, inputs, upload and chat controls. User explicitly confirmed document-rag-qa-chatbot as the target. Keep existing dark backgrounds, layout, animation and functionality. Done; validation recorded in VALIDATION_SUMMARY.md.

- REQ-0018 (2026-10-13): Simplify header, footer, About page, and metadata to focus on the application. Done; validation recorded in VALIDATION_SUMMARY.md.

- REQ-0019 (2026-10-13): Header title displays DRC below 480px and the full application name at 480px and above. Accessible home-link label remains the full name. Done.
