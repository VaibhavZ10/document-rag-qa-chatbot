# RAG PDF Chat — project plan & delivery status

**Last updated:** 2026-04-13

This document tracks what is **done** versus what is **still to implement** for this repo (FastAPI + LangChain RAG backend, React/TypeScript Vite frontend, deployment-oriented layout).

---

## Completed

### Core RAG & API

- [x] PDF upload, chunking (`RecursiveCharacterTextSplitter`), embeddings, **FAISS** vector store
- [x] **FastAPI** modular app: `app/main.py`, routers for health, upload/status, chat (`/ask`)
- [x] **OpenRouter**-compatible LLM path (`ChatOpenAI` + configurable base URL / model IDs)
- [x] **Multi-provider config** in code: OpenRouter, Groq, direct OpenAI, **Gemini**, **HuggingFace** (keys + model lists in `app/config.py`)
- [x] **LCEL-style** RAG answer generation in `LLMService` (prompt → LLM → parser)
- [x] **Pydantic** request/response models; **`pydantic-settings`** for env-based config
- [x] CORS, `.env.example`, default PDF load from `backend/documents/` when present

### Multi-agent pipeline (7 agents)

- [x] **Extractor** → **Analyzer** → **Preprocessor** → **Optimizer** → **Synthesizer** → **Validator** → **Assembler** as separate classes, orchestrated in `AgentPipeline`
- [x] **`GET /pipeline-info`** — JSON description of pipeline stages for UI/docs

### Multi-provider failover

- [x] **5-provider fallback chain** — ordered priority: OpenRouter → Groq → Gemini → HuggingFace → OpenAI
- [x] `_generate_with_failover()` tries user's selected model first, then walks the chain; every failure is logged
- [x] Native **Gemini** provider via Google's OpenAI-compatible endpoint (`gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`)
- [x] Native **HuggingFace** Inference API provider (`Mistral-7B`, `Zephyr-7B`, `Llama-3-8B`)
- [x] `PROVIDER_PRIORITY` list + `get_fallback_chain()` in config

### FAISS persistence

- [x] Vector index **auto-saved to disk** on `create_from_documents()`
- [x] **Auto-loaded on startup** if existing index found — no re-upload needed after restart
- [x] Controlled by `FAISS_PERSIST_DIR` env variable

### SSE streaming

- [x] **`POST /ask/stream`** endpoint emitting `status`, `token`, `done`, `error` SSE events
- [x] Frontend `streamQuestion()` helper + `useChat` streaming mode
- [x] Typing indicator shows **live token-by-token text** with blinking cursor
- [x] **Stream toggle** button + **Stop generating** cancel button

### Frontend (showcase)

- [x] **TypeScript** + **Vite** + **React Router** (Home, Chat, About; catch-all → home for SPA)
- [x] **Tailwind CSS**, **Framer Motion**, **Lucide** icons, **CVA**-style UI primitives (button, glass card, scroll reveal, etc.)
- [x] **max-w-9xl** layout, responsive behavior, **glassmorphism** styling
- [x] Landing sections: hero, features (10), how-it-works, **pipeline**, **models/providers**, tech stack, CTA
- [x] Chat UI: PDF upload (drag/drop), messages, suggestions, toolbar (clear / new PDF / export), typing indicator
- [x] **Model selector** — fetches live `/models` from backend, falls back to static list; shows provider badge
- [x] **Model id wired to `/ask`** — selected model passed through `useChat` → `api.askQuestion(message, model, includeSources)`
- [x] **Include-sources toggle** — collapsible source citations on assistant messages
- [x] **Streaming toggle** — switch between SSE streaming and standard JSON mode
- [x] **Export chat** — download history as `.txt` (also `Ctrl/Cmd+Shift+E`)
- [x] **Health indicator** — green/red/yellow dot in header polling `/health` every 15s
- [x] **`vercel.json`** — SPA rewrites + basic security/cache headers for static assets
- [x] **ESLint 9** (flat config), TypeScript strict build, production **Vite build** passing

### Client-side persistence (IndexedDB + localStorage)

- [x] **localStorage** — persists selected model, include-sources toggle, streaming toggle, banner dismissal
- [x] **IndexedDB** — chat history saved per-PDF (keyed by filename); auto-restored on re-upload of same PDF
- [x] **Saved sessions panel** — list / restore / delete previous chat sessions from IndexedDB
- [x] **Device-local data banner** — dismissible amber notice explaining data stays in this browser
- [x] All storage operations wrapped in try/catch — degrades gracefully in private mode / quota limits

### Deployment & repo hygiene

- [x] **Backend `Dockerfile`** (slim Python, non-root user, healthcheck, `PORT`, `uvicorn app.main:app`)
- [x] **`backend/.dockerignore`**
- [x] **`.gitignore`** coverage for root / backend / frontend (venv, `node_modules`, `.env`, build artifacts, `faiss_index/`, etc.)
- [x] **`sse-starlette`** added to `requirements.txt`

---

## Still to implement (future production)

### Lower priority (referenced in other docs)

1. **Auth & multi-tenant** — user accounts, per-user document isolation, rate limits.
2. **Observability** — Sentry, structured logging, metrics (see [`Redis_Sentry_PostHog_INTEGRATION_GUIDE.md`](./Redis_Sentry_PostHog_INTEGRATION_GUIDE.md)).
3. **Redis / job queue** — async embedding jobs, deduplication, caching.
4. **E2E / API tests** — pytest for agents/routes; Playwright or similar for critical UI flows.

---

## SaaS data-layer strategy (future reference)

### Current approach: device-local (demo / showcase)

IndexedDB + `localStorage` gives each visitor "their own" chat history, preferences, and cached metadata — entirely on that one browser. No server-side user accounts, cookies, or databases involved.

> **Caveat:** this is device-local, not real SaaS isolation. Clearing site data, switching browsers, or opening incognito = fresh state.

### Real SaaS upgrade path

When moving to production multi-tenant:

| Layer | Recommendation | Notes |
|-------|---------------|-------|
| **Primary DB** | **PostgreSQL** | Users, orgs/tenants, subscriptions, audit rows, strict relationships. The standard choice for FastAPI-style APIs. Run on VPS (Coolify) or managed Postgres. |
| **Alternative** | **MongoDB** | Valid if guides already standardize on it or you prefer a document model. Less "default" than Postgres for classic auth + billing + tenancy. |
| **Cache / helpers** | **Redis** | Rate limits, short-lived sessions, job queues, caching. Use **alongside** Postgres (or Mongo), not as a replacement for durable data. |
| **Auth** | Session/JWT/cookies | Tie every API request to a verified user/tenant. Even magic-link or OAuth counts — the point is server-enforced identity. |

**Short rule:** Postgres (primary) + Redis (optional helpers) is the usual "real SaaS" combo. Mongo instead of Postgres is OK. Redis alone is not sufficient for accounts/documents.

Browser storage (IndexedDB + localStorage) can still serve as a **UX cache** on top of server state — not the source of truth.
