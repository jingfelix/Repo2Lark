from fastapi import APIRouter, Request

from repo2lark.config import settings
from repo2lark.models import BaseEvent, PushEvent
from repo2lark.utils import send_to_lark

router = APIRouter()


@router.post("/webhook")
async def webhook(request: Request, params: PushEvent | BaseEvent):
    headers = request.headers

    x_github_event = headers.get("X-GitHub-Event", None)
    if x_github_event is None:
        return {"message": "X-GitHub-Event is None"}

    match x_github_event:
        case "push":
            await send_to_lark(
                settings.push_template_id,
                variables={
                    "commiter": params.pusher.name,
                    "repository": params.repository.full_name,
                    "author": params.head_commit.author.name,
                    "branch": params.ref,
                    "time": params.head_commit.timestamp,
                    "commit_url": params.head_commit.url,
                    "message": params.head_commit.message,
                },
            )

    return {"message": "ok"}
