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


Assignee = User


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


class Comment(BaseModel):
    body: str
    created_at: str
    html_url: str
    user: User


class IssueCommentEvent(IssueEvent):
    comment: Comment


class Head(BaseModel):
    ref: str
    repo: Repository
    sha: str
    user: User


Base = Head


class PullRequest(BaseModel):
    html_url: str
    state: str
    user: User
    title: str
    body: str | None
    base: Base
    head: Head
    updated_at: str
    assignee: Optional[Assignee] = None


class PREvent(BaseEvent):
    action: str
    number: int
    pull_request: PullRequest
    repository: Repository
