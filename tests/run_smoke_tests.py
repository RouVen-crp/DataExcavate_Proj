from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_midterm import run_pipeline
from src.audit import audit_processed_slice
from src.answering import answer_from_evidence
from src.evaluate import evaluate_predictions, select_failure_cases
from src.graph_rag import GraphRagRetriever
from src.preprocess import normalize_qasper_records
from src.retrieval import TfidfRetriever


def main() -> None:
    raw_records = [
        {
            "id": "p1",
            "title": "Graph retrieval",
            "full_text": [
                {
                    "section_name": "Intro",
                    "paragraphs": [
                        "Graph retrieval connects evidence terms.",
                        "Entity expansion improves evidence coverage.",
                        " ".join(["long"] * 260),
                    ],
                }
            ],
            "qas": [
                {
                    "question_id": "q1",
                    "question": "What connects evidence terms?",
                    "answers": [
                        {
                            "answer": {
                                "extractive_spans": ["Graph retrieval"],
                                "evidence": ["Graph retrieval connects evidence terms."],
                                "unanswerable": False,
                            }
                        }
                    ],
                },
                {
                    "question_id": "q2",
                    "question": "What is not in the paper?",
                    "answers": [{"answer": {"extractive_spans": [], "evidence": [], "unanswerable": True}}],
                },
            ],
        }
    ]

    papers, qas = normalize_qasper_records(raw_records)
    audit = audit_processed_slice(papers, qas)
    assert audit["long_paragraphs"]["count"] == 1
    assert audit["unanswerable"]["count"] == 1

    tfidf = TfidfRetriever.from_papers(papers)
    evidence = tfidf.retrieve(qas[0]["question"], paper_id="p1", top_k=2)
    assert evidence[0]["paragraph_id"] == "p1::p0000"
    answer = answer_from_evidence(qas[0]["question"], evidence)
    assert not answer["refused"]

    graph = GraphRagRetriever.from_papers(papers, tfidf)
    graph_ids = [item["paragraph_id"] for item in graph.retrieve("How does entity expansion improve coverage?", "p1", 3)]
    assert "p1::p0001" in graph_ids

    predictions = [
        {
            "question_id": qas[0]["question_id"],
            "predicted_answer": answer["answer"],
            "retrieved_evidence_ids": [item["paragraph_id"] for item in evidence],
            "refused": False,
            "latency_ms": 1.0,
        },
        {
            "question_id": qas[1]["question_id"],
            "predicted_answer": "INSUFFICIENT_EVIDENCE",
            "retrieved_evidence_ids": [],
            "refused": True,
            "latency_ms": 1.0,
        },
    ]
    metrics = evaluate_predictions(qas, predictions)
    assert metrics["evidence_recall_at_5"] == 1.0
    assert metrics["refusal_accuracy"] == 1.0
    assert select_failure_cases(qas, predictions) == []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "fixture.jsonl"
        source.write_text(json.dumps(raw_records[0]), encoding="utf-8")
        summary = run_pipeline(source=source, output_dir=tmp_path / "out", max_papers=1, max_qas=2, top_k=2)
        assert summary["qas"] == 2
        assert (tmp_path / "out" / "graphrag_metrics.json").exists()

    print("smoke tests passed")


if __name__ == "__main__":
    main()
