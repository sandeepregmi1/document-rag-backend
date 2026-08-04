from fastapi import FastAPI

app = FastAPI(
    title="Document RAG Backend",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "Document RAG Backend is running"
    }