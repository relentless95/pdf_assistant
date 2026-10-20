from fastapi import FastAPI

app = FastAPI(title = "PDF assistant")


@app.get("/health")
def health():
    return {"status": "ok"}
