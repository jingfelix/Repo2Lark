import base64
import hashlib
import hmac
import time

import httpx
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.types import Message


def verify_signature(payload_body, secret_token, signature_header) -> None:
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise HTTPException(
            status_code=403, detail="x-hub-signature-256 header is missing!"
        )
    hash_object = hmac.new(
        secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")


def gen_sign(timestamp, secret):
    # 拼接 timestamp 和 secret
    string_to_sign = "{}\n{}".format(timestamp, secret)
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return sign


async def send_to_lark(
    template_id: str, lark_webhook_url: str, lark_webhook_secret: str, variables: dict
) -> None:
    data = {
        "msg_type": "interactive",
        "card": {
            "type": "template",
            "data": {
                "template_id": template_id,
                "template_variable": variables,
            },
        },
    }
    if lark_webhook_secret != "" and lark_webhook_secret is not None:
        timestamp = str(int(time.time()))
        sign = gen_sign(timestamp, lark_webhook_secret)
        data["timestamp"] = timestamp
        data["sign"] = sign

    if lark_webhook_url == "" or lark_webhook_url is None:
        raise HTTPException(status_code=500, detail="lark_webhook_url is empty!")

    # TODO 增加超时和重试
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(lark_webhook_url, json=data)

    if res.status_code != 200 or res.json()["code"] != 0:
        raise HTTPException(status_code=500, detail=res.text)


def truncate(text: str, length: int = 80) -> str:
    """Truncate text to a certain length.

    Args:
        text: text to truncate
        length: length to truncate to

    Returns:
        Truncated text.
    """
    if text is None:
        return ""
    if len(text) > length:
        return text[: length - 3] + "..."
    return text


async def get_body(request: Request) -> bytes:
    async def receive() -> Message:
        return {"type": "http.request", "body": body}

    body = await request.body()
    request._receive = receive
    return body
