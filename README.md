# PDF Assistant: build and learning roadmap

A practical project for Marc: build a PDF question-answering app from scratch, understand the code, and deploy a small demonstration. Focus on backend and cloud skills while using your existing React, TypeScript and testing experience.

## What you will build

A user uploads a text-based PDF, asks a question, and receives an answer supported by excerpts and page numbers. When the document does not contain enough information, the app should say so. Start with one document at a time and a simple interface.

Final demonstration: PDF upload → extract pages → split text into chunks → retrieve relevant chunks → generate an answer with page references → display sources.

Start with the backend. FastAPI provides an interactive `/docs` page, so you can exercise endpoints before building a React interface. Add the interface once uploading and searching work.

## Start here: your first session

Goal today: run a small API locally and understand what happens when the browser calls an endpoint. Do not try to finish RAG or deployment today.

Prerequisites:

- uv installed and available in your terminal. Check with `uv --version`. See https://docs.astral.sh/uv/getting-started/installation/ if needed. uv can install Python for you.
- VS Code or your preferred editor, with Python support.
- Git. Node.js and Docker are only needed in later stages.

Open this folder in your editor and open a PowerShell terminal. Run:

```powershell
cd "$env:USERPROFILE\Documents\projects\pdf_assistant"
uv --version
uv python install 3.12
uv init --bare --python 3.12
uv add fastapi "uvicorn[standard]"
```

Run `uv init` only once, before a `pyproject.toml` exists. The `--bare` option keeps initialization minimal; write `main.py` in the next step. `uv add` records dependencies in `pyproject.toml`, creates `.venv`, and manages `uv.lock`. `uv run` uses that environment without activation or PowerShell policy changes. Select `.venv\Scripts\python.exe` in your editor. If `uv` is not recognized after installation, reopen your terminal.

Create a file named `main.py` yourself:

```python
from fastapi import FastAPI

app = FastAPI(title="PDF Assistant")


@app.get("/health")
def health():
    return {"status": "ok"}
```

Run it from this project folder:

```powershell
uv run uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/health`, then `http://127.0.0.1:8000/docs`. Use Ctrl+C in the terminal to stop the server.

Done when:

- [ ] `/health` returns `{"status":"ok"}`.
- [ ] You can explain GET, endpoint, request, response, JSON and HTTP status code.
- [ ] You can explain `main:app`: file/module `main`, object `app`.
- [ ] You add a second endpoint yourself and try it through `/docs`.

## Packages: install only as you reach each stage

| Stage | Package | Purpose |
| --- | --- | --- |
| 1: API | `fastapi` | Routes, request validation and API documentation; installs its core dependencies, including Pydantic. |
| 1: API | `uvicorn[standard]` | Runs the API server; development reload support. |
| 2: PDFs | `python-multipart` | Parses multipart file uploads. |
| 2: PDFs | `pypdf` | Extracts text from PDFs, keeping page numbers. |
| 3: search | `scikit-learn` | An understandable TF-IDF retrieval baseline and cosine similarity. |
| 4: tests | `pytest`, `httpx` | Tests and FastAPI test-client support. |
| 5: semantic search | `sentence-transformers` | Local embeddings; model weights download separately and use disk/memory. |
| 6: AI answers | One provider's SDK, chosen later | Calls the answer model; install only after choosing local or hosted inference. |
| 6: configuration | `pydantic-settings` | Reads typed application configuration and secrets from environment variables. |
| 7: frontend | React, TypeScript, Vite | Build the interface when the backend works. |

No LangChain, vector database, Redis, Celery or Kubernetes is required for the first version. Use Python's built-in `sqlite3`, `pathlib`, `uuid` and `logging` when needed. Add dependencies to solve a specific problem, rather than installing a complete AI stack first.

## Stage 2: upload and read one PDF

Install:

```powershell
uv add python-multipart pypdf
```

Learn `UploadFile`, POST requests, multipart forms, exception handling and basic validation.

Build:

- `POST /documents`: accept a PDF, create a document ID, extract text per page and return its ID, page count and a short preview.
- `GET /documents/{document_id}`: return document information.
- Keep one small test PDF in memory initially. Persistence can follow after extraction works.
- Reject empty, malformed or encrypted PDFs with a useful error. Limit upload size, for example to 10 MB. An extension alone is not sufficient validation.
- Preserve page numbers from the start. Use generated IDs rather than supplied filenames for stored files.

Done when you can upload your own small, non-sensitive PDF through `/docs` and inspect text from different pages. Scanned image PDFs may have no extractable text: report this clearly. OCR is a later extension.

## Stage 3: search before adding an LLM

Install:

```powershell
uv add scikit-learn
```

Learn text chunking, overlap, retrieval and similarity scoring.

Build a function that splits each page into chunks. A reasonable first experiment is around 800–1,200 characters with 150–200 characters of overlap; adjust using real examples. Store each chunk with a document ID, page number and chunk ID.

Use TF-IDF and cosine similarity to return the most relevant chunks for a question. Add `POST /documents/{document_id}/search` with a validated JSON body containing `question`. Return the best three to five excerpts with their pages.

Done when relevant questions return useful passages and searching one document cannot accidentally return another document's text. Keep a short list of questions and expected source pages so you can compare later changes.

## Stage 4: tests and a maintainable backend

Install:

```powershell
uv add --dev pytest httpx
uv run pytest
```

Test the behavior that matters: upload rejection, extraction with page numbers, document isolation, useful retrieval, unknown document IDs and empty questions. Use a tiny PDF you are allowed to include in the repository.

Once `main.py` becomes hard to read, move extraction, chunking and retrieval into separate modules. Add SQLite metadata and a local data folder to preserve documents across restarts. Add a deletion endpoint that removes the document and its chunks.

Suggested eventual layout; create it as you need it:

```text
pdf_assistant/
  README.md
  backend/
    app/
      main.py
      schemas.py
      services/
        extraction.py
        chunking.py
        retrieval.py
        answering.py
    tests/
  frontend/
  .gitignore
  .env.example
```

If you move files, update your server command to match the new module path. Add `.venv/`, `.env`, `__pycache__/`, `.pytest_cache/`, local uploads and downloaded models to `.gitignore` before committing. Commit `pyproject.toml`, `uv.lock` and `.python-version` if present. Keep `.venv/` out of Git. Use `uv add` for runtime packages and `uv add --dev` for test tools. On another machine, `uv sync --locked` recreates the environment. Keep the uv project files at the repository root even if Python modules move into `backend/`; run uv commands from the root.

## Stage 5: improve retrieval with embeddings

Install only now:

```powershell
uv add sentence-transformers
```

Learn what embeddings represent and how cosine similarity ranks vectors. Choose one small English embedding model after checking its model card, license and resource needs. Embed chunks once, cache them, and embed each question at query time. For a small collection, an in-memory vector matrix is enough.

Compare semantic retrieval against your TF-IDF baseline using the same questions. Record whether the correct page appears among the top results. Keep TF-IDF if it works better on a particular example; the comparison is part of the project evidence.

## Stage 6: answer questions using retrieved evidence

First choose a model route:

- Local inference: no per-request API charge, but requires a separately installed model runner and sufficient hardware.
- Hosted API: easier on local hardware, but usage may cost money and retrieved document excerpts leave your machine. Choose a provider and budget before installing its SDK or using private documents.

Start with public sample PDFs. Add only the selected provider's SDK using `uv add <sdk-package>` (replace the placeholder with the real package name), and add configuration support with `uv add pydantic-settings` if useful. Never put API keys in frontend code or Git.

Add `POST /documents/{document_id}/ask`:

1. Retrieve passages from the selected document.
2. Send the question and those passages to the model.
3. Ask it to answer from the supplied evidence and say when evidence is missing.
4. Return the answer plus source chunk IDs and page numbers.

Treat instructions inside PDFs as document content, not instructions for the application. Check that returned references correspond to retrieved chunks. References help users inspect answers; they do not guarantee that every generated claim is correct.

Done when supported questions include useful sources, unsupported questions are handled sensibly, and timeouts/provider failures produce understandable errors. Keep a small evaluation set including answerable and unanswerable questions. This retrieval-plus-generation pipeline is RAG.

## Stage 7: build a small React interface

Install Node.js LTS first. From the project root:

```powershell
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm run dev
```

Learn file input, `FormData`, `fetch`, loading/error states and the frontend/backend request flow. Allow only your actual frontend origin in backend CORS configuration during development.

Build an upload panel, selected-document label, question input, answer area and source excerpts with page numbers. Start with normal request/response; streaming can wait. Add Playwright later to verify one complete upload → question → source-display flow. Your React experience should make this stage more familiar.

## Stage 8: package and deploy

Learn Docker images/containers, environment variables, ports, HTTPS, health checks, persistent storage, logs and CI. Create a Dockerfile after the app works locally. Containerize the API first and verify it can start without your local virtual environment.

Choose one hosting provider together when you reach this stage; check current pricing and limits then. Free hosting is not guaranteed, and local model inference may not fit small hosted services.

Before a public demo:

- Configure secrets on the host, disable development reload and restrict CORS.
- Decide how files survive restarts; ephemeral container storage is not durable storage.
- Isolate users' documents, add authentication or limit the demo to public sample PDFs.
- Add upload, request and model-spending limits plus a deletion/retention policy.
- Do not log document contents or secrets. Log request IDs, durations and failures.
- Run backend tests in GitHub Actions on pull requests using `uv sync --locked` followed by `uv run pytest`.
- Check upload, restart/persistence, question answering and source links on the deployed app.

## Stage 9: make the project useful for applications

Include a live demo or recorded walkthrough, an architecture diagram, setup instructions, automated checks, retrieval/answer evaluation results and honest limitations. Explain decisions you made: why backend first, why start with TF-IDF, how page references work, and how deployment stores files and protects costs.

Only describe features on your CV after building and verifying them. A small deployed app you can explain is useful evidence for backend/cloud roles.

## How to learn without buying a course

Work one stage at a time. Watch a short lesson, rebuild the example yourself, then adapt it to this project. You can continue the FastAPI video you already opened. Stop after routes, request bodies and validation; build Stage 1 before consuming the whole series.

Useful YouTube search phrases (these are search topics, not verified course endorsements):

- `FastAPI Python beginner routes Pydantic request body`
- `FastAPI UploadFile python multipart PDF`
- `Python TF-IDF cosine similarity document search`
- `RAG embeddings retrieval citations explained`
- `React TypeScript file upload FormData fetch`
- `Docker FastAPI deployment environment variables`

Official references checked while preparing this guide:

- [uv project workflow](https://docs.astral.sh/uv/guides/projects/)
- [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI file uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [pypdf text extraction and limitations](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)

Ask for help with the smallest step you are currently building. A useful prompt: “I am on Stage 2. Explain the upload flow, give me a small task, and review my code without completing the entire feature for me.”

## Progress

- [ ] Stage 1: API runs and routes make sense.
- [ ] Stage 2: upload and extract PDF pages.
- [ ] Stage 3: retrieve relevant excerpts.
- [ ] Stage 4: tests, structure and persistence.
- [ ] Stage 5: compare semantic search.
- [ ] Stage 6: grounded answers and evaluation.
- [ ] Stage 7: React interface.
- [ ] Stage 8: Docker, CI and deployment.
- [ ] Stage 9: demo and portfolio documentation.#   p d f _ a s s i s t a n t  
 