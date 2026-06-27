from arxiv_recommendation_mcp.dataset import DatasetCache


class FakeDatasetCache(DatasetCache):
    def __init__(self, payloads):
        super().__init__(api_base_url="https://example.test/api")
        self.payloads = payloads

    def fetch_json(self, file_name):
        return self.payloads[file_name]


def test_search_papers_matches_all_terms_and_domain():
    cache = FakeDatasetCache(
        {
            "metadata.json": {"source_last_updated": "2026-06-28T00:00:00+00:00"},
            "all_papers.json": {
                "papers": [
                    {
                        "arxiv_id": "2601.00001v1",
                        "title": "BIM point cloud retrieval",
                        "abstract": "construction model search",
                        "relevance_score": 8.0,
                        "domain_relevance": {"bim_cim": "高"},
                    },
                    {
                        "arxiv_id": "2601.00002v1",
                        "title": "Prompt optimization",
                        "abstract": "LLM workflow",
                        "relevance_score": 9.0,
                        "domain_relevance": {"ai_knowhow": "高"},
                    },
                ]
            },
        }
    )

    results = cache.search_papers("BIM point", domain="bim_cim")

    assert [paper["arxiv_id"] for paper in results] == ["2601.00001v1"]


def test_get_paper_accepts_base_arxiv_id():
    cache = FakeDatasetCache(
        {
            "metadata.json": {"source_last_updated": "2026-06-28T00:00:00+00:00"},
            "all_papers.json": {"papers": [{"arxiv_id": "2601.00001v2", "title": "Test"}]},
        }
    )

    assert cache.get_paper("2601.00001")["title"] == "Test"


def test_latest_papers_respects_limit():
    cache = FakeDatasetCache(
        {
            "latest.json": {
                "papers": [
                    {"arxiv_id": "2601.00001v1"},
                    {"arxiv_id": "2601.00002v1"},
                ]
            }
        }
    )

    assert len(cache.latest_papers(limit=1)) == 1


def test_recommend_papers_for_usecase_allows_partial_term_matches():
    cache = FakeDatasetCache(
        {
            "metadata.json": {"source_last_updated": "2026-06-28T00:00:00+00:00"},
            "all_papers.json": {
                "papers": [
                    {
                        "arxiv_id": "2601.00001v1",
                        "title": "BIM point cloud retrieval",
                        "abstract": "construction model search",
                        "domain_relevance": {"bim_cim": "高"},
                    }
                ]
            },
        }
    )

    results = cache.recommend_papers_for_usecase("BIM robot", domain="bim_cim")

    assert [paper["arxiv_id"] for paper in results] == ["2601.00001v1"]
