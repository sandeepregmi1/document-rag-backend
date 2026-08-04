from fastapi import APIRouter
from fastapi import Request

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/")
async def health(
    request: Request,
):

    status = {
        "status": "healthy",
        "database": "connected",
    }

    try:
        request.app.state.redis.ping()

        status["redis"] = "connected"

    except Exception:

        status["redis"] = "disconnected"

    try:

        request.app.state.vector_store.client.get_collections()

        status["qdrant"] = "connected"

    except Exception:

        status["qdrant"] = "disconnected"

    try:

        request.app.state.embedding

        status["embedding_model"] = "loaded"

    except Exception:

        status["embedding_model"] = "not_loaded"

    return status