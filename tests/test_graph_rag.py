from src.graph_rag import GraphRagRetriever
from src.retrieval import TfidfRetriever


def test_graph_rag_expands_from_seed_terms_to_related_evidence():
    papers = [
        {
            "paper_id": "p1",
            "paragraphs": [
                {
                    "paragraph_id": "p1::p0000",
                    "paper_id": "p1",
                    "section": "Method",
                    "text": "Graph retrieval uses entity expansion.",
                },
                {
                    "paragraph_id": "p1::p0001",
                    "paper_id": "p1",
                    "section": "Method",
                    "text": "Entity expansion improves evidence coverage.",
                },
                {
                    "paragraph_id": "p1::p0002",
                    "paper_id": "p1",
                    "section": "Background",
                    "text": "Unrelated optimizer schedule.",
                },
            ],
        }
    ]

    graph_retriever = GraphRagRetriever.from_papers(papers, TfidfRetriever.from_papers(papers))
    results = graph_retriever.retrieve("How does graph retrieval improve coverage?", paper_id="p1", top_k=3)

    result_ids = [item["paragraph_id"] for item in results]
    assert "p1::p0000" in result_ids
    assert "p1::p0001" in result_ids
    assert results[0]["score"] >= results[1]["score"]
