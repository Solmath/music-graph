from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.db import get_session, init_db
from app.models import GraphResponse, Link, Node


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # make sure the tables exist, even before the first seed
    yield


app = FastAPI(title="Band Graph API", lifespan=lifespan)

# The Svelte dev server runs on another origin (Vite's default port), and the
# browser blocks cross-origin requests unless the API allows them.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
)


@app.get("/graph", response_model=GraphResponse)
def get_graph(session: Session = Depends(get_session)) -> GraphResponse:
    """Everything in the DB, in the {nodes, links} shape force-graph expects."""
    nodes = session.exec(select(Node)).all()
    links = session.exec(select(Link)).all()
    return GraphResponse(nodes=nodes, links=links)
