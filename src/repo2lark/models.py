from typing import Optional

from pydantic import BaseModel


class Repository(BaseModel):
    id: int
    name: str
    full_name: str


class Pusher(BaseModel):
    date: Optional[str] = None
    email: Optional[str] = None
    name: str
    username: Optional[str] = None


Author = Pusher
Committer = Pusher


class HeadCommit(BaseModel):
    author: Author
    committer: Committer
    message: str
    url: str
    timestamp: str


class BaseEvent(BaseModel):
    sender: dict


class PushEvent(BaseEvent):
    ref: str
    repository: Repository
    # commits: list
    head_commit: HeadCommit
    pusher: Pusher


class User(BaseModel):
    id: int
    login: str
    name: Optional[str] = None


class Issue(BaseModel):
    id: int
    number: int
    state: str
    title: str
    body: str | None
    html_url: str
    updated_at: str
    user: User


class IssueEvent(BaseEvent):
    action: str
    issue: Issue
    repository: Repository
