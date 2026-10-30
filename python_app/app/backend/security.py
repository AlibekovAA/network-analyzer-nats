from collections import deque
from time import monotonic

from starlette.datastructures import MutableHeaders
from starlette.formparsers import MultiPartException
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.backend.config import (
    ANALYSIS_REQUEST_LIMIT,
    ANALYSIS_REQUEST_WINDOW_SECONDS,
    MAX_FILE_SIZE,
    MULTIPART_OVERHEAD_LIMIT,
)


class SecurityMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app: ASGIApp = app
        self._analysis_requests: deque[float] = deque()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        upload = scope["method"] == "POST" and scope["path"] == "/analyze-network"
        received_bytes = 0
        oversized = False
        rejection_body = b'{"detail":"Upload exceeds the size limit"}'

        async def receive_upload() -> Message:
            nonlocal received_bytes, oversized
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > MAX_FILE_SIZE + MULTIPART_OVERHEAD_LIMIT:
                    oversized = True
                    raise MultiPartException("Upload exceeds the size limit")
            return message

        async def send_response(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                policy = "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
                if scope["path"] not in {"/docs", "/redoc", "/docs/oauth2-redirect"}:
                    policy += "; default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
                headers["Content-Security-Policy"] = policy
                headers["X-Frame-Options"] = "DENY"
                headers["X-Content-Type-Options"] = "nosniff"
                headers["Referrer-Policy"] = "no-referrer"
                if oversized:
                    message["status"] = 413
                    headers["Content-Length"] = str(len(rejection_body))
                    headers["Content-Type"] = "application/json"
            elif message["type"] == "http.response.body" and oversized:
                message["body"] = rejection_body
                message["more_body"] = False
            await send(message)

        if upload:
            now = monotonic()
            while self._analysis_requests and now - self._analysis_requests[0] >= ANALYSIS_REQUEST_WINDOW_SECONDS:
                self._analysis_requests.popleft()
            if len(self._analysis_requests) >= ANALYSIS_REQUEST_LIMIT:
                response = JSONResponse(
                    {"detail": "Too many analysis requests"},
                    status_code=429,
                    headers={"Retry-After": str(ANALYSIS_REQUEST_WINDOW_SECONDS)},
                )
                await response(scope, receive, send_response)
                return
            self._analysis_requests.append(now)

        await self.app(scope, receive_upload if upload else receive, send_response)
