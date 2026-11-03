# VALIDATION_SUMMARY.md

**Cycle:** C1  
**Updated:** 2026-08-08

## Free models + Sentry harden (this pass)

| Check | Result | Notes |
|-------|--------|-------|
| `npm run check:frontend` | **PASS** | typecheck + eslint `--max-warnings 0` (re-run pre-commit) |
| `npm run build` | **PASS** | Vite production build (earlier this session) |
| `npm run check:backend` | **PASS** | compileall + ruff + mypy + unittest OK (re-run pre-commit) |
| Live LLM smoke `/ask` | **Skipped** | No automated call; avoid logging keys |
| Sentry no-ops without DSN | **Code path** | `initSentry` returns early when `VITE_SENTRY_DSN` empty |
| Audit vs plan scope | **OK** | No React Query/Redis/auth in scope; Vite SPA state model unchanged |
| Pre-commit re-check (docs pass) | **PASS** | `check:frontend` + `check:backend` OK |

## EvalGate

`eval_gate_status`: **N/A** (not at Human Gate 2).

## Human follow-ups (not validated here)

- Rotate leaked Sentry client DSN in Sentry UI
- Set Vercel `VITE_SENTRY_DSN` + `VITE_APP_ENV=production`
- Spot-check production `/about` and `/chat`

## REQ-0014 — API Status frontend removal (2026-10-12)

- `npm run typecheck` and `npm run build`: blocked by existing TS5103 for `ignoreDeprecations: "6.0"`; left user configuration unchanged.
- `./node_modules/.bin/tsc --noEmit --ignoreDeprecations 5.0`: PASS.
- `npm run lint`: PASS.
- `./node_modules/.bin/vite build`: PASS (Browserslist data-age notice).
- Source and built JavaScript search: no dashboard route, UI, or runtime-summary fetch references remain.
- `git diff --check`: reports pre-existing trailing whitespace on README line 1; preserved.
- Generated tracked TypeScript build info restored to its pre-build contents. Backend tests and browser visual checks not run for this frontend removal.

## REQ-0015 — Application rename (2026-10-12)

- `./node_modules/.bin/tsc --noEmit --ignoreDeprecations 5.0`: PASS; uses the existing configuration workaround without editing tsconfig.
- `npm run lint`: PASS.
- `./node_modules/.bin/vite build`: PASS (Browserslist data-age notice).
- Python AST parsing of the four modified backend files: PASS.
- Search confirms the old display name is absent from frontend source, HTML metadata, and backend application source.
- Storage/session keys, package identifiers, external URLs, and unrelated edits preserved. No runtime backend or visual browser testing for this text-only rename.

## REQ-0016 — Remove frontend API documentation (2026-10-13)

- `./node_modules/.bin/tsc --noEmit --ignoreDeprecations 5.0`: PASS (existing config workaround; tsconfig unchanged).
- `npm run lint`: PASS.
- `./node_modules/.bin/vite build`: PASS (Browserslist data-age notice).
- `git diff --check -- frontend/src/components/layout/header.tsx`: PASS.
- Frontend source/HTML search for API Docs, API documentation, Swagger, ReDoc, OpenAPI, and /docs: no matches.
- No backend changes or browser visual checks.

## REQ-0017 — Light orange frontend theme (2026-10-13)

- `npm run lint`: PASS.
- `npm run typecheck -- --ignoreDeprecations 5.0`: PASS; retains the previously documented workaround for TS5103.
- `./node_modules/.bin/vite build`: PASS (2236 modules). Build needed sandbox escalation to use the installed dependencies; an initial sandboxed attempt did not finish. A config-runner attempt failed because the existing Vite config uses `__dirname`; the standard loader passed.
- Validation used `/tmp/rag-orange.PMzWz8/frontend`, an isolated copy of the frontend with the same installed node_modules; changed source files were copied back byte-for-byte.
- Browser: visually inspected home hero and empty chat at the preview viewport; verified hero CTA navigation to `/chat`. Orange headline, icons, badges, primary button, upload border and chat accents render. Backend upload and streamed answers were not exercised.
- Source review: no blue/purple utility classes remain in rendered frontend components. Spinner retains legacy color prop aliases for compatibility; both use the shared orange palette. Semantic success/error colors remain.

## REQ-0018 — Application presentation (2026-10-13)

- Historical checks: frontend lint, TypeScript with the documented configuration workaround, and Vite production build passed.
- Python syntax parsing passed for the modified backend package metadata.
- Browser checks covered Home, About, and footer presentation. Backend functionality was not exercised.

## REQ-0019 — Responsive header title (2026-10-13)

- `npm run lint`, `npm run typecheck -- --ignoreDeprecations 5.0`, and `./node_modules/.bin/vite build`: PASS.
- Compiled CSS inspected for `@media (width>=480px)` display rules (Vite minifies the minimum-width query to range syntax). Full accessible link name preserved. No browser boundary check performed.

## Documentation scope cleanup — 2026-10-20

- Verified removal of targeted unrelated project/account references, tutorial attribution, and references to the deleted assistant instruction file across the reviewed documentation.
- Checked that relative links in the rewritten model-selection and styling guides resolve to existing files.
- No new trailing whitespace or code-fence imbalance was introduced. The protocol document retains its pre-existing fence-formatting issue.
- Confirmed no tracked application-file changes and no staged changes. No application tests or live provider requests were run for this documentation-only change.

## Documentation consolidation — 2026-10-20

- Verified that the seven selected documents are absent and the project plan is byte-for-byte unchanged.
- Scanned retained project Markdown for references to the deleted document names; none remain.
- Verified the replacement image-component link resolves. No application tests were needed for these documentation changes.

## REQ-0020 — Vercel/Render preparation (2026-11-03)

- Isolated Python 3.12 environment, without project secrets: compileall, Ruff, Mypy (30 modules), and six backend unittest cases PASS.
- Frontend SSE parser regression tests: PASS, including all split points and CRLF/multiline frames. Node 22.23.4 TypeScript/Vite production build and ESLint: PASS.
- Render Blueprint validates against Render's published JSON schema. Runtime pins match installed distributions; PyTorch and sentence-transformers excluded.
- Local macOS health/index/search smoke: 100 chunks, mocked 3072-dimensional embeddings, approximately 135 MiB peak RSS. This does not establish Linux/concurrent/live-provider capacity.
- Linux Docker build blocked because Docker daemon was not running. Hosted upload/answer, real Gemini quota/billing, cold-start and browser checks remain pending.

## Hosted deployment checks and model availability — 2026-11-03

- Render Free Linux Docker build and startup succeeded for `38a5289`. Public `/health`, `/models`, CORS preflight for the assigned Vercel origin, and upload with real Gemini embeddings passed.
- `/ask` failed with provider HTTP 404 for `gemini-2.5-flash-lite`. Google limits that model to previously active projects. Prepared `gemini-3.5-flash-lite` as the deployment default/allowlist and added it to the provider catalog; standard free-tier availability verified in Google pricing.
- Live answers and SSE for the replacement model are pending publication. Vercel production variables are saved and the initial production deployment succeeded. The home page and direct `/chat` route render; the upload UI shows 5 MB.
- Replacement-model configuration: isolated Python 3.12 compileall, Ruff, Mypy (30 modules), and all six backend tests PASS. Regression coverage confirms an explicit request for the older model routes only to the permitted replacement.
