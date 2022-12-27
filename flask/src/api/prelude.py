"""Создание ответов API в формате JSON на невалидные запросы"""

import json

from flask import Request, _request_ctx_stack, request
from werkzeug.exceptions import BadRequest


class JSONBadRequest(BadRequest):
    def get_body(self, *args, **kwargs) -> str:
        """Get the JSON body."""
        return json.dumps(
            {
                "error": "B001",
                "message": self.description,
            }
        )

    def get_headers(self, *args, **kwargs) -> list[tuple[str, str]]:
        """Get a list of headers."""
        return [("Content-Type", "application/json")]


def on_json_loading_failed(self, e: str):
    ctx = _request_ctx_stack.top
    if ctx is not None and ctx.app.config.get("DEBUG", False):
        raise JSONBadRequest("Failed to decode JSON object: {0}".format(e))
    raise JSONBadRequest()


def init_api(app):
    Request.on_json_loading_failed = on_json_loading_failed

    @app.before_request
    def before_request():
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            raise JSONBadRequest("X-Request-Id header is required")
