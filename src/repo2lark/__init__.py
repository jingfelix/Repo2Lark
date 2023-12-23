from fastapi import FastAPI

app = FastAPI(docs_url=None)

from repo2lark.middleware import VerifySignatureMiddleware
from repo2lark.router import router

app.include_router(router)
app.add_middleware(VerifySignatureMiddleware)


def run():
    import uvicorn

    uvicorn.run("repo2lark:app", host="0.0.0.0", port=3030, reload=True)
