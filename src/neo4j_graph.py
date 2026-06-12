from __future__ import annotations

import os
import time
from typing import Any

from src.answering import answer_from_evidence
from src.graph_rag import extract_terms
from src.retrieval import TfidfRetriever


DEFAULT_URI = "bolt://localhost:7687"
DEFAULT_USER = "neo4j"
DEFAULT_PASSWORD = "graphrag123"


class Neo4jGraphStore:
    """Persist paper paragraphs and term co-occurrence in Neo4j for subgraph retrieval."""

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:
            raise RuntimeError(
                "Neo4j driver not installed. Run: pip install -r requirements-neo4j.txt"
            ) from exc

        self._uri = uri or os.environ.get("NEO4J_URI", DEFAULT_URI)
        self._user = user or os.environ.get("NEO4J_USER", DEFAULT_USER)
        self._password = password or os.environ.get("NEO4J_PASSWORD", DEFAULT_PASSWORD)
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def close(self) -> None:
        self._driver.close()

    def clear(self) -> None:
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def ingest_papers(self, papers: list[dict[str, Any]]) -> dict[str, int]:
        stats = {"papers": 0, "paragraphs": 0, "terms": 0, "mentions": 0}
        with self._driver.session() as session:
            for paper in papers:
                paper_id = str(paper.get("paper_id", ""))
                if not paper_id:
                    continue
                session.run(
                    """
                    MERGE (paper:Paper {paper_id: $paper_id})
                    SET paper.title = $title
                    """,
                    paper_id=paper_id,
                    title=str(paper.get("title", "")),
                )
                stats["papers"] += 1

                for paragraph in paper.get("paragraphs", []):
                    paragraph_id = str(paragraph.get("paragraph_id", ""))
                    text = str(paragraph.get("text", ""))
                    if not paragraph_id or not text.strip():
                        continue
                    terms = sorted(extract_terms(text))
                    session.run(
                        """
                        MERGE (para:Paragraph {paragraph_id: $paragraph_id})
                        SET para.paper_id = $paper_id,
                            para.section = $section,
                            para.text = $text
                        WITH para
                        MATCH (paper:Paper {paper_id: $paper_id})
                        MERGE (para)-[:IN_PAPER]->(paper)
                        WITH para
                        UNWIND $terms AS name
                        MERGE (term:Term {paper_id: $paper_id, name: name})
                        MERGE (para)-[:MENTIONS]->(term)
                        """,
                        paragraph_id=paragraph_id,
                        paper_id=paper_id,
                        section=str(paragraph.get("section", "")),
                        text=text,
                        terms=terms,
                    )
                    stats["paragraphs"] += 1
                    stats["terms"] += len(terms)
                    stats["mentions"] += len(terms)
        return stats

    def retrieve_paragraph_candidates(
        self,
        query: str,
        paper_id: str,
        max_hops: int = 1,
        limit: int = 80,
    ) -> list[dict[str, Any]]:
        query_terms = sorted(extract_terms(query))
        if not query_terms:
            return []

        cypher = f"""
        MATCH (seed:Term {{paper_id: $paper_id}})
        WHERE seed.name IN $query_terms
        MATCH (seed_para:Paragraph {{paper_id: $paper_id}})-[:MENTIONS]->(seed)
        WITH collect(DISTINCT seed_para) AS seed_paragraphs
        UNWIND seed_paragraphs AS seed_para
        OPTIONAL MATCH (seed_para)-[:MENTIONS]->(bridge:Term {{paper_id: $paper_id}})
        OPTIONAL MATCH (expanded:Paragraph {{paper_id: $paper_id}})-[:MENTIONS]->(bridge)
        WITH collect(DISTINCT seed_para) + collect(DISTINCT expanded) AS paragraphs
        UNWIND paragraphs AS para
        WITH DISTINCT para
        WHERE para IS NOT NULL
        RETURN para.paragraph_id AS paragraph_id,
               para.section AS section,
               para.text AS text
        LIMIT $limit
        """
        with self._driver.session() as session:
            rows = session.run(
                cypher,
                paper_id=paper_id,
                query_terms=query_terms,
                limit=limit,
            )
            return [dict(row) for row in rows]

    def retrieve_with_trace(
        self,
        query: str,
        paper_id: str,
        tfidf: TfidfRetriever,
        top_k: int = 5,
        graph_bonus: float = 0.15,
        max_hops: int = 1,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        query_terms = extract_terms(query)
        candidates = self.retrieve_paragraph_candidates(
            query=query,
            paper_id=paper_id,
            max_hops=max_hops,
        )
        candidate_ids = {item["paragraph_id"] for item in candidates}
        seeds = tfidf.retrieve(query, paper_id=paper_id, top_k=2)
        seed_ids = {seed["paragraph_id"] for seed in seeds}
        candidate_ids.update(seed_ids)

        lexical_scores = {
            item["paragraph_id"]: item["score"]
            for item in tfidf.retrieve(query, paper_id=paper_id, top_k=len(tfidf.documents))
        }
        documents = {doc["paragraph_id"]: doc for doc in tfidf.documents}

        scored: list[dict[str, Any]] = []
        for paragraph_id in candidate_ids:
            document = documents.get(paragraph_id)
            if not document:
                continue
            paragraph_terms = extract_terms(document.get("text", ""))
            query_matches = len(query_terms & paragraph_terms)
            graph_score = float(query_matches)
            lexical_score = lexical_scores.get(paragraph_id, 0.0)
            score = lexical_score + graph_bonus * graph_score
            scored.append(
                {
                    **document,
                    "score": score,
                    "lexical_score": lexical_score,
                    "graph_matches": query_matches,
                    "graph_score": graph_score,
                }
            )

        scored.sort(key=lambda item: (-item["score"], str(item["paragraph_id"])))
        evidence = scored[:top_k]
        trace = {
            "backend": "neo4j",
            "query_terms": sorted(query_terms),
            "seed_evidence_ids": sorted(seed_ids),
            "candidate_evidence_ids": sorted(candidate_ids),
            "candidate_evidence_count": len(candidate_ids),
            "returned_evidence_ids": [item["paragraph_id"] for item in evidence],
            "graph_bonus": graph_bonus,
            "max_hops": max_hops,
        }
        return evidence, trace


def run_neo4j_graph_rag(
    papers: list[dict[str, Any]],
    qas: list[dict[str, Any]],
    store: Neo4jGraphStore,
    top_k: int = 5,
    graph_bonus: float = 0.15,
    max_hops: int = 1,
) -> list[dict[str, Any]]:
    tfidf = TfidfRetriever.from_papers(papers)
    predictions: list[dict[str, Any]] = []
    for qa in qas:
        started = time.perf_counter()
        evidence, trace = store.retrieve_with_trace(
            query=qa.get("question", ""),
            paper_id=str(qa.get("paper_id", "")),
            tfidf=tfidf,
            top_k=top_k,
            graph_bonus=graph_bonus,
            max_hops=max_hops,
        )
        latency_ms = (time.perf_counter() - started) * 1000
        query_terms = extract_terms(qa.get("question", ""))
        top_terms = extract_terms(evidence[0].get("text", "")) if evidence else set()
        query_overlap = len(query_terms & top_terms)
        graph_match = query_overlap > 0
        answer = answer_from_evidence(
            qa.get("question", ""),
            evidence,
            has_graph_match=graph_match,
            query_term_overlap=query_overlap,
        )
        predictions.append(
            {
                "question_id": qa.get("question_id"),
                "paper_id": qa.get("paper_id"),
                "question": qa.get("question", ""),
                "predicted_answer": answer["answer"],
                "retrieved_evidence_ids": [item["paragraph_id"] for item in evidence],
                "retrieved_evidence": evidence,
                "scores": [item["score"] for item in evidence],
                "latency_ms": latency_ms,
                "refused": answer["refused"],
                "graph_match": graph_match,
                "graph_trace": trace,
            }
        )
    return predictions
