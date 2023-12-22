import base64
import hashlib
import hmac
import time

import httpx
from starlette.exceptions import HTTPException

from repo2lark.config import settings


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
    # 拼接timestamp和secret
    string_to_sign = "{}\n{}".format(timestamp, secret)
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return sign


async def send_to_lark(template_id: str, variables: dict) -> None:
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
    if settings.webhook_secret != "" and settings.webhook_secret is not None:
        timestamp = str(int(time.time()))
        sign = gen_sign(timestamp, settings.webhook_secret)
        data["timestamp"] = timestamp
        data["sign"] = sign

    if settings.webhook_url == "" or settings.webhook_url is None:
        raise HTTPException(status_code=500, detail="webhook_url is empty!")

    # TODO 增加超时和重试
    async with httpx.AsyncClient() as client:
        res = await client.post(settings.webhook_url, json=data)

    if res.status_code != 200:
        raise HTTPException(status_code=500, detail=res.text)