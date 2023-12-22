from fastapi import APIRouter, BackgroundTasks, Request

from repo2lark.config import settings
from repo2lark.models import BaseEvent, PushEvent
from repo2lark.utils import send_to_lark, truncate

router = APIRouter()


@router.post("/webhook")
async def webhook(
    request: Request,
    params: PushEvent | BaseEvent,
    background_tasks: BackgroundTasks = None,
):
    headers = request.headers

    x_github_event = headers.get("X-GitHub-Event", None)
    if x_github_event is None:
        return {"message": "X-GitHub-Event is None"}

    match x_github_event:
        case "push":
            background_tasks.add_task(
                send_to_lark,
                settings.push_template_id,
                variables={
                    "commiter": params.pusher.name,
                    "repository": params.repository.full_name,
                    "author": params.head_commit.author.name,
                    "branch": params.ref,
                    "time": params.head_commit.timestamp,
                    "commit_url": params.head_commit.url,
                    "message": truncate(params.head_commit.message),
                },
            )
        case _:
            pass

    return {"message": "recieved"}
