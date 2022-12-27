import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.api.middlewares import CustomRequestMiddleware
from src.api.v1 import films
from src.core.config import settings
from src.core.http import http_session
from src.core.tracer import configure_tracer


configure_tracer()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

FastAPIInstrumentor.instrument_app(app)


app.add_middleware(CustomRequestMiddleware)


@app.middleware("http")
async def check_request_id_header(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        error = {"error": "B001", "message": "X-Request-Id header is required"}
        return JSONResponse(content=jsonable_encoder(error))

    response = await call_next(request)
    return response


@app.on_event("shutdown")
async def shutdown():
    await http_session.shutdown()


app.include_router(films.router, prefix="/api/v1/films", tags=["Фильмы"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
    )
