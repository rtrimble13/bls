"""Fuzzy search over surveys and series using RapidFuzz.

Scores are 0-100. An exact (case-insensitive) match on a series id or survey
abbreviation scores 100; otherwise the best of a few RapidFuzz scorers is used
so that both typos (``unemploymnt``) and word-order differences (``rate
unemployment``) are tolerated. See ``docs/adr/0005-fuzzy-search.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz, utils

from bls.catalog import CatalogEntry
from bls.models import Survey


@dataclass(frozen=True)
class SearchHit:
    kind: str  # "series" | "survey"
    id: str
    title: str
    score: float
    survey: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        rec: dict[str, Any] = {
            "kind": self.kind,
            "id": self.id,
            "title": self.title,
            "survey": self.survey,
            "score": round(self.score, 1),
        }
        rec.update(self.extra)
        return rec


_FUZZY_FLOOR = 72.0  # minimum RapidFuzz ratio for a token to earn fuzzy credit


def score_text(query: str, text: str, tags: Sequence[str] = ()) -> float:
    """Return a 0-100 relevance score of ``text`` (plus optional ``tags``) for ``query``.

    Each query token earns a credit, and the score is the mean credit:

    * 1.00 - the token equals a tag, or the whole query equals a tag/the text
    * 0.95 - the token is a whole word of the text or of a tag
    * 0.75 - the token is a substring of a word (``employ`` in ``employment``)
    * 0.8 x ratio - the closest word is a fuzzy match (typos), ratio >= 0.72
    * 0.00 - no match

    Exact tag hits therefore outrank incidental word hits, and ties are left to
    the caller (which keeps the curated catalog order).
    """
    q = utils.default_process(query)
    t = utils.default_process(text)
    if not q or not t:
        return 0.0
    norm_tags = [utils.default_process(tag) for tag in tags]
    if q == t or q in norm_tags:
        return 100.0
    words = set(t.split())
    tag_words = {w for tag in norm_tags for w in tag.split()}
    credits: list[float] = []
    for tok in q.split():
        if tok in norm_tags:
            credits.append(1.0)
        elif tok in words or tok in tag_words:
            credits.append(0.95)
        elif any(tok in w for w in words | tag_words):
            credits.append(0.75)
        else:
            best = max((fuzz.ratio(tok, w) for w in words | tag_words), default=0.0)
            credits.append(0.8 * best / 100.0 if best >= _FUZZY_FLOOR else 0.0)
    if not credits:
        return 0.0
    return round(100.0 * sum(credits) / len(credits), 1)


def search_series(
    query: str,
    entries: Iterable[CatalogEntry],
    *,
    survey: str | None = None,
    limit: int = 20,
    min_score: float = 55.0,
) -> list[SearchHit]:
    hits: list[SearchHit] = []
    survey = survey.upper() if survey else None
    q_upper = query.strip().upper()
    for entry in entries:  # catalog order breaks ties: national/headline series come first
        if survey and entry.survey != survey:
            continue
        exact = entry.series_id == q_upper
        score = 100.0 if exact else score_text(query, entry.title, entry.tags)
        if score >= min_score:
            hits.append(
                SearchHit(
                    kind="series",
                    id=entry.series_id,
                    title=entry.title,
                    score=score,
                    survey=entry.survey,
                    extra={
                        "frequency": entry.frequency,
                        "seasonal": entry.seasonal,
                        "units": entry.units,
                    },
                )
            )
    return _top(hits, limit)


def search_surveys(
    query: str,
    surveys: Iterable[Survey],
    *,
    limit: int = 20,
    min_score: float = 55.0,
) -> list[SearchHit]:
    hits: list[SearchHit] = []
    q_upper = query.strip().upper()
    for s in surveys:
        exact = s.abbreviation == q_upper
        score = 100.0 if exact else score_text(query, s.name, (s.abbreviation,))
        if score >= min_score:
            hits.append(
                SearchHit(kind="survey", id=s.abbreviation, title=s.name, score=score, survey=None)
            )
    return _top(hits, limit)


def search_rows(
    query: str,
    rows: Iterable[dict[str, Any]],
    *,
    text_of: Callable[[dict[str, Any]], str],
    id_of: Callable[[dict[str, Any]], str],
    limit: int = 20,
    min_score: float = 55.0,
) -> list[tuple[float, dict[str, Any]]]:
    """Generic fuzzy search over arbitrary dict rows (used for flat-file series lists)."""
    scored: list[tuple[float, dict[str, Any]]] = []
    q_upper = query.strip().upper()
    for row in rows:
        score = 100.0 if id_of(row).upper() == q_upper else score_text(query, text_of(row))
        if score >= min_score:
            scored.append((score, row))
    scored.sort(key=lambda t: -t[0])  # sort() is stable: file order breaks ties
    return scored[:limit] if limit else scored


def _top(hits: Sequence[SearchHit], limit: int) -> list[SearchHit]:
    ordered = sorted(enumerate(hits), key=lambda ih: (-ih[1].score, ih[0]))  # stable on input order
    chosen = [h for _, h in ordered]
    return chosen[:limit] if limit else chosen
