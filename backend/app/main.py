from contextlib import asynccontextmanager

from app.api.agents import router as agents_router
from app.core.database import create_schema
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_schema()
    yield


app = FastAPI(title="AgentIA", version="0.0.0", lifespan=lifespan)
app.include_router(agents_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}