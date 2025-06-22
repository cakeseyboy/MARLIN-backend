from fastapi import FastAPI

app = FastAPI(title="MARLIN API", version="0.1.0")

@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"} 