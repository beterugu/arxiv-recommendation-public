from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .dataset import DatasetCache

mcp = FastMCP("arxiv-recommendation")
cache = DatasetCache()


@mcp.tool()
def get_metadata() -> dict[str, Any]:
    """Return public dataset metadata."""
    return cache.get_metadata()


@mcp.tool()
def latest_papers(limit: int = 10) -> dict[str, Any]:
    """Return the latest daily recommended papers."""
    papers = cache.latest_papers(limit=limit)
    return {"count": len(papers), "papers": papers}


@mcp.tool()
def search_papers(query: str, limit: int = 10, domain: str | None = None) -> dict[str, Any]:
    """Search papers by keywords across title, abstract, summaries, tags, and application ideas."""
    papers = cache.search_papers(query=query, limit=limit, domain=domain)
    return {"query": query, "domain": domain, "count": len(papers), "papers": papers}


@mcp.tool()
def get_paper(arxiv_id: str) -> dict[str, Any]:
    """Return one paper by arXiv ID. Version suffix is optional."""
    paper = cache.get_paper(arxiv_id)
    if paper is None:
        return {"found": False, "arxiv_id": arxiv_id, "message": "paper not found"}
    return {"found": True, "paper": paper}


@mcp.tool()
def recommend_papers_for_usecase(
    usecase: str,
    limit: int = 10,
    domain: str | None = None,
) -> dict[str, Any]:
    """Recommend papers for a natural-language use case."""
    papers = cache.recommend_papers_for_usecase(usecase=usecase, limit=limit, domain=domain)
    return {"usecase": usecase, "domain": domain, "count": len(papers), "papers": papers}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
