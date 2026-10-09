"""Seed the local SQLite DB from MusicBrainz.

Usage (from the backend/ folder):
    uv run python -m app.seed search "Dark Tranquillity"
    uv run python -m app.seed fetch <MBID> --depth 1
"""

import argparse
from datetime import UTC, datetime

import musicbrainzngs
from sqlmodel import Session, select

from app.db import engine, init_db
from app.models import FetchLog, Link, Node

# MusicBrainz asks for a User-Agent that says who you are and how to reach you.
musicbrainzngs.set_useragent("MusicGraph", "0.1", "github.com/solmath/music-graph")

# MusicBrainz relationship names -> our link types. Everything else is ignored.
RELATION_TYPES = {
    "member of band": "member",
    "collaboration": "collaboration",
}

# Safety net: each fetch costs about one second (the rate limit).
MAX_FETCHES = 600


def year(value: str | None) -> int | None:
    """MusicBrainz dates look like '1989', '1989-03' or '1989-03-12', or are missing."""
    if not value:
        return None
    try:
        return int(value[:4])
    except ValueError:
        return None


def node_type(mb_type: str | None) -> str:
    return "musician" if mb_type == "Person" else "band"


def make_link_id(
    source: str, target: str, link_type: str, start: int | None, end: int | None
) -> str:
    return f"{source}|{target}|{link_type}|{start}|{end}"


def fetch_and_store(session: Session, mbid: str) -> set[str]:
    """Look up one artist, store it and its relationships, return the neighbor IDs."""
    artist = musicbrainzngs.get_artist_by_id(mbid, includes=["artist-rels"])["artist"]
    life = artist.get("life-span", {})
    session.merge(
        Node(
            id=mbid,
            name=artist["name"],
            type=node_type(artist.get("type")),
            start=year(life.get("begin")),
            end=year(life.get("end")),
        )
    )
    session.flush()

    neighbors: set[str] = set()
    for rel in artist.get("artist-relation-list", []):
        link_type = RELATION_TYPES.get(rel["type"])
        if link_type is None:
            continue

        other = rel["artist"]
        other_id = other["id"]
        neighbors.add(other_id)

        # Only add the neighbor if we don't know it yet. Merging would overwrite
        # a fully fetched node with this thinner version (no life-span).
        if session.get(Node, other_id) is None:
            session.add(
                Node(id=other_id, name=other["name"], type=node_type(other.get("type")))
            )
            session.flush()

        # "forward": the artist we looked up is the relationship's subject
        # (musician -> band). "backward": the other artist is.
        if rel.get("direction") == "forward":
            source, target = mbid, other_id
        else:
            source, target = other_id, mbid

        start, end = year(rel.get("begin")), year(rel.get("end"))
        session.merge(
            Link(
                id=make_link_id(source, target, link_type, start, end),
                source=source,
                target=target,
                type=link_type,
                attributes=rel.get("attribute-list", []),
                start=start,
                end=end,
            )
        )

    session.merge(FetchLog(mbid=mbid, fetched_at=datetime.now(UTC)))
    session.commit()
    return neighbors


def neighbors_of(session: Session, mbid: str) -> set[str]:
    """Neighbors of an already fetched artist, read from our own DB."""
    links = session.exec(
        select(Link).where((Link.source == mbid) | (Link.target == mbid))
    ).all()
    return {link.target if link.source == mbid else link.source for link in links}


def walk(session: Session, start_mbid: str, depth: int) -> None:
    """Breadth-first walk. depth=1 fetches the artist itself (its neighbors become
    nodes), depth=2 also fetches every neighbor, and so on."""
    seen = {start_mbid}
    frontier = [start_mbid]
    fetches = 0

    for level in range(1, depth + 1):
        next_frontier: list[str] = []
        for mbid in frontier:
            if session.get(FetchLog, mbid) is not None:
                neighbors = neighbors_of(session, mbid)
                print(f"[level {level}] cached  {mbid}")
            else:
                if fetches >= MAX_FETCHES:
                    print(
                        f"Stopped: reached MAX_FETCHES ({MAX_FETCHES}). Raise it in seed.py if you mean it."
                    )
                    return
                fetches += 1
                neighbors = fetch_and_store(session, mbid)
                name = session.get(Node, mbid).name
                print(f"[level {level}] fetched {name} ({len(neighbors)} neighbors)")
            for n in neighbors:
                if n not in seen:
                    seen.add(n)
                    next_frontier.append(n)
        frontier = next_frontier


def search(name: str) -> None:
    result = musicbrainzngs.search_artists(artist=name, limit=10)
    for a in result["artist-list"]:
        print(
            a["id"],
            a["name"],
            a.get("type", "?"),
            a.get("country", ""),
            a.get("disambiguation", ""),
            sep=" | ",
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="find the MBID of an artist")
    p_search.add_argument("name")

    p_fetch = sub.add_parser("fetch", help="fetch an artist and walk its relationships")
    p_fetch.add_argument("mbid")
    p_fetch.add_argument("--depth", type=int, default=1)

    args = parser.parse_args()
    if args.command == "search":
        search(args.name)
    else:
        init_db()
        with Session(engine) as session:
            walk(session, args.mbid, args.depth)


if __name__ == "__main__":
    main()
