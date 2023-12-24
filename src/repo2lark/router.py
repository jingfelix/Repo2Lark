import json
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Form, Request

from repo2lark.config import settings
from repo2lark.models import BaseEvent, IssueCommentEvent, IssueEvent, PushEvent
from repo2lark.utils import send_to_lark, truncate

router = APIRouter()


@router.post("/webhook")
@router.post("/webhook/urlencoded")
async def webhook_urlencoded(
    request: Request,
    payload: Optional[str] = Form(...),
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
                    "comment_url": params.comment.url,
                },
            )
        case _:
            pass

    return {"message": "recieved"}


@router.post("/webhook/json")
async def webhook_json(
    request: Request,
    params: PushEvent | IssueCommentEvent | IssueEvent | BaseEvent = None,
    background_tasks: BackgroundTasks = None,
):
    # 转发至 webhook_urlencoded
    return await webhook_urlencoded(
        request,
        payload=params.model_dump_json(),
        background_tasks=background_tasks,
    )
