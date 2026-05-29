from __future__ import annotations

import math
import re
import time
from collections import Counter, defaultdict
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


class TfidfRetriever:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = documents
        self._term_freqs = [_token_counts(doc["text"]) for doc in documents]
        document_frequency: Counter[str] = Counter()
        for counts in self._term_freqs:
            document_frequency.update(counts.keys())
        total_documents = max(len(documents), 1)
        self._idf = {
            term: math.log((1 + total_documents) / (1 + frequency)) + 1.0
            for term, frequency in document_frequency.items()
        }
        self._doc_norms = [self._vector_norm(counts) for counts in self._term_freqs]

    @classmethod
    def from_papers(cls, papers: list[dict[str, Any]]) -> "TfidfRetriever":
        documents: list[dict[str, Any]] = []
        for paper in papers:
            for paragraph in paper.get("paragraphs", []):
                documents.append(
                    {
                        "paper_id": paragraph.get("paper_id") or paper.get("paper_id"),
                        "paragraph_id": paragraph.get("paragraph_id"),
                        "section": paragraph.get("section", ""),
                        "text": paragraph.get("text", ""),
                    }
                )
        return cls(documents)

    def retrieve(
        self,
        query: str,
        paper_id: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        query_counts = _token_counts(query)
        query_norm = self._vector_norm(query_counts)
        scored: list[dict[str, Any]] = []

        for index, document in enumerate(self.documents):
            if paper_id is not None and document.get("paper_id") != paper_id:
                continue
            score = self._cosine(query_counts, query_norm, self._term_freqs[index], self._doc_norms[index])
            scored.append({**document, "score": score})

        scored.sort(key=lambda item: (-item["score"], str(item["paragraph_id"])))
        return scored[:top_k]

    def retrieve_with_latency(
        self,
        query: str,
        paper_id: str | None = None,
        top_k: int = 5,
    ) -> tuple[list[dict[str, Any]], float]:
        started = time.perf_counter()
        evidence = self.retrieve(query=query, paper_id=paper_id, top_k=top_k)
        return evidence, (time.perf_counter() - started) * 1000

    def _vector_norm(self, counts: Counter[str]) -> float:
        return math.sqrt(sum((count * self._idf.get(term, 1.0)) ** 2 for term, count in counts.items()))

    def _cosine(
        self,
        query_counts: Counter[str],
        query_norm: float,
        document_counts: Counter[str],
        document_norm: float,
    ) -> float:
        if query_norm == 0 or document_norm == 0:
            return 0.0
        dot = 0.0
        for term, query_count in query_counts.items():
            dot += query_count * self._idf.get(term, 1.0) * document_counts.get(term, 0) * self._idf.get(term, 1.0)
        return dot / (query_norm * document_norm)


def run_tfidf_baseline(
    papers: list[dict[str, Any]],
    qas: list[dict[str, Any]],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    from src.answering import answer_from_evidence

    retriever = TfidfRetriever.from_papers(papers)
    predictions: list[dict[str, Any]] = []
    for qa in qas:
        evidence, latency_ms = retriever.retrieve_with_latency(
            qa.get("question", ""),
            paper_id=qa.get("paper_id"),
            top_k=top_k,
        )
        answer = answer_from_evidence(qa.get("question", ""), evidence)
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
            }
        )
    return predictions


def _token_counts(text: Any) -> Counter[str]:
    return Counter(token.lower() for token in TOKEN_RE.findall(str(text)))
