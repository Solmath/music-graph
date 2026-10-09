from datetime import datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Node(SQLModel, table=True):
    """A musician or a band (later: a song)."""

    id: str = Field(primary_key=True)  # the MusicBrainz ID (MBID)
    name: str
    type: str  # "musician" | "band" | "song"
    start: int | None = None  # year; bands: formation
    end: int | None = None  # year; bands: dissolution (None = still active / unknown)


class Link(SQLModel, table=True):
    """An edge between two nodes."""

    # Natural key "source|target|type|start|end". The same relationship shows up
    # when you fetch either artist, and this key makes the second insert a no-op
    # instead of a duplicate. See make_link_id() in seed.py.
    id: str = Field(primary_key=True)
    source: str = Field(foreign_key="node.id", index=True)
    target: str = Field(foreign_key="node.id", index=True)
    type: str  # "member" | "collaboration" (later: "guest", "original", "cover")
    # Raw attribute list from MusicBrainz: instruments, vocals, and other flags.
    attributes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    start: int | None = None  # year
    end: int | None = None  # year; None = ongoing or unknown
    date_source: str | None = "musicbrainz"


class FetchLog(SQLModel, table=True):
    """Which artists we have already looked up (our cache bookkeeping).

    A node can exist only as the neighbor of a fetched artist. Its own
    relationships are unknown until it appears here.
    """

    mbid: str = Field(primary_key=True)
    fetched_at: datetime


class GraphResponse(SQLModel):
    """Shape of the JSON that force-graph consumes."""

    nodes: list[Node]
    links: list[Link]
