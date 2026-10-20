# API requests — one endpoint per file

These are the six endpoints called by the current frontend, including optional Sentry telemetry. Each `.http` file is self-contained: purpose, frontend caller, URL, headers, body, and a commented mock response. There is exactly one request per file.

| File | Method and endpoint | Used for |
| --- | --- | --- |
| [01-health.http](01-health.http) | GET `/health` | Header connection indicator |
| [02-models.http](02-models.http) | GET `/models` | Model selector |
| [03-upload.http](03-upload.http) | POST `/upload` | PDF upload and indexing |
| [04-ask.http](04-ask.http) | POST `/ask` | Complete JSON answer |
| [05-ask-stream.http](05-ask-stream.http) | POST `/ask/stream` | Streaming answer |
| [06-sentry-tunnel.http](06-sentry-tunnel.http) | POST `/api/oversight` | Optional frontend error monitoring |

## Run

1. Start your configured FastAPI backend.
2. Open a file in VS Code REST Client or another compatible `.http` client and use its Send Request action. These files are plain HTTP examples, not Postman collection JSON.
3. Set `@base_url` in each file to the direct backend origin (default `http://127.0.0.1:8000`), without a trailing slash. Proxy deployments may have different prefixes.
4. Replace the example UUID with your own UUID v4 in files 03, 04, and 05. Keep it identical in all three. There is no bearer authentication; this header selects the document session.
5. In file 03, replace `/absolute/path/to/your/sample.pdf` with a real PDF path. Wait for upload success before running file 04 or 05.
6. File 06 is separate from the chat workflow. Its dummy envelope expects HTTP 403 without contacting Sentry.

The sample bodies use the server's default model. To choose one, add `"model": "<id returned by /models>"` to the question JSON. AI-provider credentials stay in backend configuration.

## Scope

Omitted `/`, `/status`, `/pipeline-info`, and `/runtime-summary` because no current frontend feature calls them. The frontend still defines helper methods for `/` and `/status`, but those methods have no callers. These backend routes have not been deleted or disabled.

The combined Postman collection, environment, combined request file, and separate payload fixtures were replaced by these individual files. Expected responses are illustrative mocks. Route/method coverage for these six endpoints, headers, request JSON/envelope syntax, and multipart formatting were checked locally; no live API requests were made.
