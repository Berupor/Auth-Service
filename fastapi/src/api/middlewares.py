from contextvars import ContextVar

from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send


REQUEST_ID_CTX_KEY = "request_var"

_request_id_ctx_var: ContextVar[str] = ContextVar(
    REQUEST_ID_CTX_KEY, default=None
)


def get_request_var() -> str:
    return _request_id_ctx_var.get()


class CustomRequestMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        request_var = _request_id_ctx_var.set(request)

        await self.app(scope, receive, send)

        _request_id_ctx_var.reset(request_var)
