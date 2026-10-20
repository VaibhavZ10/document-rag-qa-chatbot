# Model selection and provider fallback

The backend provider registry is defined in [`config.py`](../backend/app/config.py). Model IDs in that registry describe configured choices; they do not establish current provider availability, pricing, or account quotas.

## Chat providers

| Provider | Credential environment variable | Global fallback position |
| --- | --- | --- |
| OpenRouter | `OPENROUTER_API_KEY` | 1 |
| Groq | `GROQ_API_KEY` | 2 |
| Google Gemini | `GOOGLE_API_KEY` | 3 |
| Hugging Face | `HF_API_KEY` | 4 |
| Direct OpenAI | `OPENAI_DIRECT_API_KEY` | 5 |

The default model is `openai/gpt-oss-20b:free`, configurable through `DEFAULT_MODEL`. OpenRouter also accepts the legacy `OPENAI_API_KEY` credential alias. Credential presence determines eligibility; it is not a successful connectivity check.

## Model selector

The frontend model selector requests `GET /models`. Its static fallback catalog is `AI_MODELS` in [`types/index.ts`](../frontend/src/types/index.ts). The selected model ID accompanies requests to `POST /ask` and `POST /ask/stream`.

## Answer generation

[`LLMService`](../backend/app/services/llm_service.py) builds the attempt sequence:

1. Try the requested model if it belongs to a configured, credentialed provider.
2. Try the remaining models from that provider.
3. Append other credentialed models in `PROVIDER_PRIORITY` order, skipping duplicates.
4. Return the first successful answer, or raise an error when all attempts fail.

Each attempt combines the retrieved document context and question with the RAG prompt, a `ChatOpenAI` client, and `StrOutputParser`. Standard responses use `chain.invoke`; streaming uses `chain.astream`. The response identifies the model that completed generation.

## Embeddings

Upload-time embeddings use a separate sequence defined by `get_embedding_fallback_chain()` and executed by [`VectorStoreService`](../backend/app/services/vector_store.py).

- The configured default provider is considered first when eligible and equipped with an embedding model, followed by the provider priority list.
- OpenRouter and direct OpenAI use `OpenAIEmbeddings` with their respective base URLs.
- Gemini uses the custom client in [`embedding_clients.py`](../backend/app/services/embedding_clients.py).
- Hugging Face embeddings run locally on CPU through `HuggingFaceEmbeddings`.
- Groq is skipped by the current configuration because its `embedding_model` is `None`.
- Direct OpenAI embeddings require `EMBEDDING_OPENAI_DIRECT=true` and credentials.
- An additional Gemini embedding candidate is appended when Gemini is eligible.
- If configured indexing attempts fail, local MiniLM is attempted. An empty candidate list raises before this fallback is reached.

FAISS stores and searches the resulting vectors; it does not generate embeddings.

## Current limitations

- Generation catches exceptions and advances through the sequence; it does not implement detailed failure classification or a provider-wide rate-limit circuit breaker.
- Streaming failover after partial output can append text from a different attempt without resetting the earlier text.
- Persisted indexes do not record enough embedding-model identity information to guarantee compatible restoration.
- Provider catalogs and credentials must be maintained separately from application deployment. Configured models can become unavailable.
