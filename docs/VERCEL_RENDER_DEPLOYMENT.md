# Vercel + Render deployment

## Release configuration

- Frontend: Vercel Hobby, Vite, Node 22.x, root directory `frontend`.
- Backend: Render Free Docker web service, `backend/Dockerfile.render`, Python 3.12, one Uvicorn worker.
- Chat: `gemini-2.5-flash-lite`. Embeddings: `gemini-embedding-001`.
- The Render profile permits only these models and Gemini. It disables local embedding models and excludes PyTorch/sentence-transformers from the image.
- Upload limit: 5 MiB; at most four cached vector sessions; per-IP limits: two uploads and ten questions per minute. These controls do not guarantee capacity under concurrent traffic or highly compressed PDFs.
- The existing `backend/Dockerfile` and `requirements.txt` remain available for installations that need local embedding fallback.

## Cost and availability

Use a Gemini API project on the free tier. A model allowlist does not make a billing-enabled API key free. Google AI Pro subscriptions are separate from direct API billing. Do not add paid provider keys, enable paid compute, or attach paid disks for this release. Account quotas and terms must be checked in the dashboards.

Render Free sleeps after inactivity, and its filesystem is ephemeral. Uploaded indexes can disappear on sleep, restart, or redeployment. The user must re-upload the PDF; browser transcripts are separate and cannot restore the server index. Vercel Hobby is for eligible personal, non-commercial use. Use the supplied hosting subdomains; no purchased domain is required.

Google lists free-tier pricing for the selected models; availability and remaining quota still require testing with the actual API project. Free-tier content may be used to improve Google's products; use a non-sensitive PDF for verification.

Sources checked 2026-11-03:
- [Render free-service limits](https://render.com/docs/free)
- [Render Blueprint schema](https://render.com/docs/blueprint-spec)
- [Vercel Hobby](https://vercel.com/docs/plans/hobby)
- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini model lifecycle](https://ai.google.dev/gemini-api/docs/deprecations)

## 1. Publish the prepared release

Review and commit the deployment changes on `develop`, then push the branch and merge the tested release into `main`. Hosting services need the new files on GitHub. Staging and committing this release have been authorized; pushing and merging remain manual steps.

Validation commands (Python 3.12 and Node 22):

```bash
cd frontend
npm ci
npm run test
npm run lint
npm run build
cd ../backend
python3.12 -m venv .venv-render
.venv-render/bin/pip install -r requirements-render.txt ruff mypy
BACKEND_PYTHON="$PWD/.venv-render/bin/python" bash ../scripts/check-backend.sh
```

`requirements-render.in` lists direct runtime dependencies; `requirements-render.txt` pins the tested dependency set. Re-resolve and retest pins when upgrading. Never copy local `.env` files into the deployment image.

## 2. Create the Vercel project

Import `VaibhavZ10/document-rag-qa-chatbot` using the GitHub integration.

| Setting | Value |
| --- | --- |
| Framework | Vite |
| Root directory | `frontend` |
| Production branch | `main` |
| Node | 22.x |
| Install | `npm ci` |
| Build | `npm run build` |
| Output | `dist` |
| `VITE_APP_ENV` | `production` |
| `VITE_MAX_FILE_SIZE_MB` | `5` |
| `VITE_API_BASE_URL` | Actual Render HTTPS origin, set after backend creation |

Record the assigned stable Vercel project URL. An initial frontend deployment without the backend URL is only a setup deployment; do not treat it as ready. Leave Sentry disabled initially. Never put API keys into `VITE_*` variables; those are public browser configuration.

## 3. Create the Render backend

In Render choose **New → Blueprint**, connect the same repository, select `main`, and use the root `render.yaml`.

At creation enter these prompted variables:

| Setting | Value |
| --- | --- |
| `GOOGLE_API_KEY` | Enter your key directly into Render's secret/environment field |
| `CORS_ORIGINS` | Exact stable Vercel origin, such as `https://your-project.vercel.app`, without a path or trailing slash |

Confirm the service plan is **Free** before creation. The Blueprint selects root `backend`, Dockerfile `./Dockerfile.render`, context `.`, and health path `/health`. The start command is provided by the image and binds to Render's `PORT`. No persistent disk or database is requested. Automatic deployment is initially off so releases remain deliberate.

Record the public `https://...onrender.com` URL after the service is created. Inspect the first build/start logs; verify `/health` and `/models`. A healthy process does not prove the API key works; real upload and answer calls are required below.

## 4. Connect both deployments

Set Vercel `VITE_API_BASE_URL` to the Render HTTPS origin, with no `/api` suffix and no trailing slash. Redeploy the frontend: Vite embeds public environment variables at build time.

Keep Render `CORS_ORIGINS` aligned with the exact frontend origin. If testing a Vercel preview deployment, explicitly add that preview origin as a comma-separated entry. Production CORS does not automatically permit all preview URLs.

## 5. Acceptance checks

- Refresh `/`, `/chat`, and `/about` directly on Vercel.
- Wake the backend, confirm `/health`, and verify `/models` lists the allowed model.
- Upload a small text PDF; ask a question with a known answer using JSON and streaming modes.
- Verify source references, stream cancellation, and a second question.
- Open a separate browser profile: it must not inherit the first profile's document.
- Reject non-PDF and oversized files; confirm the UI and server agree on the 5 MiB limit.
- Restore a saved transcript and check that it does not claim to restore a missing PDF index.
- Restart the backend and verify that re-upload recovers a lost index.
- Inspect Render memory during upload and concurrent requests. Local macOS measurements are not proof of Linux instance capacity.
- Confirm quota errors produce a clear failure instead of a paid-provider fallback. A partial stream failure now ends with an error; retrying starts a new attempt rather than mixing providers in one answer.

Only mark the release ready after these hosted checks. If a deployment fails, redeploy the previous known-good commit on both hosts; temporary indexes may be lost.

## Current verification

Local validation uses an isolated repository copy without real API keys. Backend syntax, Ruff, Mypy and six unit/integration tests passed. Tests cover real PDF parsing and FAISS indexing with mocked embeddings/answers, session isolation, CORS, upload-size rejection, provider/model restrictions, disabled local embeddings, and streaming failure behavior. Frontend Node 22.23.4 build, ESLint and two parser tests passed; parser cases cover every split point across event/data boundaries.

A macOS smoke run with 100 chunks and mocked 3072-dimensional embeddings peaked at approximately 135 MiB RSS and did not load PyTorch. This is not a concurrent-load or live-provider benchmark.

Docker is installed but its daemon was not running during preparation. The Linux image build, live Gemini calls, and hosted end-to-end checks remain required on Render/Vercel.
