# PDF Assistant frontend

This is the React and TypeScript interface exported from v0. It uses Vite and
local mock data. It does not call FastAPI or OpenRouter, and it does not need an
API key or a running backend.

## Run locally

From this directory:

```powershell
npm install
npm run dev
```

Open http://127.0.0.1:5173. If that port is occupied, use the address printed in
the terminal. Stop the development server with Ctrl+C.

## Demo behavior

- Document selection and deletion update browser memory only.
- Choosing a PDF adds a local demo entry; its text is not extracted.
- Asking a question returns the sample answer and expandable source excerpts.
- Refreshing resets the demo documents and answers.

The placeholder operations are in `src/lib/mock-pdf-operations.ts`. The screen and
its state are in `src/components/pdf-workspace.tsx`. These are the starting points
for connecting the existing FastAPI endpoints yourself.

## Checks

```powershell
npm run build
```

The production build also checks TypeScript. Generated dependency and build
folders are ignored by Git. Backend secrets belong in the repository root's
ignored `.env`, never in browser code.

## Backend commands

From the repository root, use a separate terminal:

```powershell
uv run python -m backend.storage
uv run uvicorn backend.main:app --reload
uv run python -m pytest -v
```

The database remains in the root `data/` folder. Moving the Python modules has
not relocated or reset existing document data.
