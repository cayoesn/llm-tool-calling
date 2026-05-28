from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from app.tools import register_all_tools
from app.telemetry.setup import setup_telemetry
from prometheus_client import make_asgi_app

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Setup telemetry (OpenTelemetry, Logging)
setup_telemetry(app)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup_event():
    register_all_tools()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
