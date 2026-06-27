from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

DEFAULT_API_BASE_URL = "https://beterugu.github.io/arxiv-recommendation-public/api"
SEARCH_FIELDS = (
    "title",
    "abstract",
    "headline",
    "one_liner",
    "key_points",
    "tags",
    "application_ideas",
)


class DatasetError(RuntimeError):
    """Raised when the public JSON API cannot be read."""


def _normalize_api_base_url(api_base_url: str | None = None) -> str:
    return (api_base_url or os.environ.get("ARXIV_RECOMMENDATION_API_BASE_URL") or DEFAULT_API_BASE_URL).rstrip("/")


def _fetch_json(url: str, timeout: float = 20.0) -> dict[str, Any]:
    try:
        with urlopen(url, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return json.loads(response.read().decode(charset))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise DatasetError(f"failed to fetch JSON: {url}: {exc}") from exc


def _as_text(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(_as_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_as_text(item) for item in value.values())
    if value is None:
        return ""
    return str(value)


def _query_terms(query: str) -> list[str]:
    return [term for term in re.split(r"\s+", query.lower().strip()) if term]


def _paper_search_text(paper: dict[str, Any]) -> str:
    return " ".join(_as_text(paper.get(field)) for field in SEARCH_FIELDS).lower()


def _matches_domain(paper: dict[str, Any], domain: str | None) -> bool:
    if not domain:
        return True
    domain_relevance = paper.get("domain_relevance")
    if not isinstance(domain_relevance, dict):
        return False
    value = domain_relevance.get(domain)
    return value not in (None, "", "なし")


def _rank_paper(paper: dict[str, Any], terms: list[str]) -> float:
    text = _paper_search_text(paper)
    keyword_score = sum(text.count(term) for term in terms)
    relevance = paper.get("relevance_score")
    practicality = paper.get("practicality_score")
    if not isinstance(relevance, (int, float)):
        relevance = 0.0
    if not isinstance(practicality, (int, float)):
        practicality = 0.0
    return float(keyword_score * 1000) + float(relevance) + float(practicality) / 10.0


def _limit(value: int, default: int = 10, maximum: int = 50) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(1, min(parsed, maximum))


@dataclass
class DatasetCache:
    api_base_url: str | None = None
    timeout: float = 20.0
    _metadata: dict[str, Any] | None = field(default=None, init=False)
    _all_papers: list[dict[str, Any]] | None = field(default=None, init=False)
    _source_last_updated: str | None = field(default=None, init=False)

    @property
    def base_url(self) -> str:
        return _normalize_api_base_url(self.api_base_url)

    def fetch_json(self, file_name: str) -> dict[str, Any]:
        return _fetch_json(f"{self.base_url}/{file_name}", timeout=self.timeout)

    def get_metadata(self) -> dict[str, Any]:
        self._metadata = self.fetch_json("metadata.json")
        return self._metadata

    def get_all_papers(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        metadata = self.get_metadata()
        source_last_updated = metadata.get("source_last_updated")
        cache_stale = source_last_updated != self._source_last_updated
        if force_refresh or self._all_papers is None or cache_stale:
            payload = self.fetch_json("all_papers.json")
            papers = payload.get("papers", [])
            if not isinstance(papers, list):
                raise DatasetError("all_papers.json does not contain a papers list")
            self._all_papers = papers
            self._source_last_updated = source_last_updated
        return self._all_papers

    def latest_papers(self, limit: int = 10) -> list[dict[str, Any]]:
        payload = self.fetch_json("latest.json")
        papers = payload.get("papers", [])
        if not isinstance(papers, list):
            raise DatasetError("latest.json does not contain a papers list")
        return papers[: _limit(limit)]

    def search_papers(self, query: str, limit: int = 10, domain: str | None = None) -> list[dict[str, Any]]:
        return self._ranked_matches(query=query, limit=limit, domain=domain, require_all_terms=True)

    def _ranked_matches(
        self,
        query: str,
        limit: int = 10,
        domain: str | None = None,
        require_all_terms: bool = True,
    ) -> list[dict[str, Any]]:
        terms = _query_terms(query)
        if not terms:
            return []
        matches = []
        for paper in self.get_all_papers():
            if not _matches_domain(paper, domain):
                continue
            text = _paper_search_text(paper)
            term_matches = [term in text for term in terms]
            if (require_all_terms and all(term_matches)) or (not require_all_terms and any(term_matches)):
                matches.append((_rank_paper(paper, terms), paper))
        matches.sort(key=lambda item: item[0], reverse=True)
        return [paper for _, paper in matches[: _limit(limit)]]

    def get_paper(self, arxiv_id: str) -> dict[str, Any] | None:
        target = arxiv_id.strip()
        target_base = target.split("v")[0] if "v" in target else target
        for paper in self.get_all_papers():
            paper_id = str(paper.get("arxiv_id", ""))
            paper_base = paper_id.split("v")[0] if "v" in paper_id else paper_id
            if paper_id == target or paper_base == target_base:
                return paper
        return None

    def recommend_papers_for_usecase(
        self,
        usecase: str,
        limit: int = 10,
        domain: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._ranked_matches(
            query=usecase,
            limit=limit,
            domain=domain,
            require_all_terms=False,
        )
