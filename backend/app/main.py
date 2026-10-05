from contextlib import asynccontextmanager

from app.api.agents import router as agents_router
from app.api.catalog import router as catalog_router
from app.api.chat import router as chat_router
from app.api.evaluations import router as evaluations_router
from app.api.lifecycle import router as lifecycle_router
from app.api.missions import router as missions_router
from app.api.recommendations import router as recommendations_router
from app.api.runtime import router as runtime_router
from app.api.tool_registry import router as tool_registry_router
from app.api.tools import router as tools_router
from app.core.database import create_schema
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_schema()
    yield


app = FastAPI(title="AgentIA", version="0.0.0", lifespan=lifespan)
app.include_router(agents_router)
app.include_router(catalog_router)
app.include_router(chat_router)
app.include_router(evaluations_router)
app.include_router(lifecycle_router)
app.include_router(tools_router)
app.include_router(tool_registry_router)
app.include_router(runtime_router)
app.include_router(missions_router)
app.include_router(recommendations_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}