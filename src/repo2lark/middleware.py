from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from repo2lark.config import settings
from repo2lark.utils import get_body, verify_signature


class VerifySignatureMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        signature_header = request.headers.get("x-hub-signature-256", None)
        if not signature_header:
            return await call_next(request)
        payload_body = await get_body(request)

        verify_signature(payload_body, settings.github_webhook_secret, signature_header)

        return await call_next(request)
