import json
import urllib.parse as urlparse

from fastapi import APIRouter, BackgroundTasks, Request

from repo2lark.config import settings
from repo2lark.models import IssueCommentEvent, IssueEvent, PushEvent
from repo2lark.utils import send_to_lark, truncate

router = APIRouter()


@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks = None):
    headers = request.headers

    if headers.get("content-type", None) == "application/json":
        body = await request.body()
        return await webhook_urlencoded(
            request,
            payload=body.decode("utf-8"),
            background_tasks=background_tasks,
        )
    elif headers.get("content-type", None) == "application/x-www-form-urlencoded":
        # decode from urlencoded
        body = await request.body()
        payload = dict(urlparse.parse_qsl(body.decode("utf-8")))
        return await webhook_urlencoded(
            request,
            payload=payload.get("payload", None),
            background_tasks=background_tasks,
        )


async def webhook_urlencoded(
    request: Request,
    payload: str = None,
    background_tasks: BackgroundTasks = None,
):
    headers = request.headers

    x_github_event = headers.get("X-GitHub-Event", None)
    if x_github_event is None:
        return {"message": "X-GitHub-Event is None"}

    match x_github_event:
        case "push":
            params = PushEvent(**json.loads(payload))

            background_tasks.add_task(
                send_to_lark,
                settings.push_template_id,
                variables={
                    "commiter": params.pusher.name,
                    "repository": params.repository.full_name,
                    "author": params.head_commit.author.name,
                    "branch": params.ref,
                    "time": params.head_commit.timestamp.split("T")[0].replace(
                        "-", "/"
                    ),
                    "commit_url": params.head_commit.url,
                    "message": truncate(params.head_commit.message),
                },
            )
        case "issues":
            params = IssueEvent(**json.loads(payload))

            background_tasks.add_task(
                send_to_lark,
                settings.issue_template_id,
                variables={
                    "action": params.action.capitalize(),
                    "repository": params.repository.full_name,
                    "title": params.issue.title,
                    "message": truncate(params.issue.body),
                    "issue_url": params.issue.html_url,
                    "state": params.issue.state,
                    "time": params.issue.updated_at.split("T")[0].replace("-", "/"),
                    "user": params.issue.user.login,
                    "number": params.issue.number,
                },
            )
        case "issue_comment":
            params = IssueCommentEvent(**json.loads(payload))

            background_tasks.add_task(
                send_to_lark,
                settings.issue_comment_template_id,
                variables={
                    "action": params.action.capitalize(),
                    "user": params.comment.user.login,
                    "number": params.issue.number,
                    "repository": params.repository.full_name,
                    "state": params.issue.state,
                    "time": params.comment.created_at.split("T")[0].replace("-", "/"),
                    "title": params.issue.title,
                    "message": truncate(params.comment.body),
                    "comment_url": params.comment.html_url,
                },
            )
        case _:
            pass

    return {"message": "recieved"}
