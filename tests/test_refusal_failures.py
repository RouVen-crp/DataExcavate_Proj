from src.answering import INSUFFICIENT_EVIDENCE, answer_from_evidence
from src.evaluate import evaluate_predictions, select_failure_cases


def test_weak_retrieval_refuses_and_failure_cases_are_report_ready():
    evidence = [{"paragraph_id": "p1::p0000", "text": "unrelated text", "score": 0.0}]
    answer = answer_from_evidence("What is GraphRAG?", evidence, min_score=0.05)
    qas = [
        {
            "question_id": "p1::q1",
            "question": "What is GraphRAG?",
            "answers": ["GraphRAG uses graph expansion"],
            "evidence_ids": ["p1::p0001"],
            "unanswerable": False,
        },
        {
            "question_id": "p1::q2",
            "question": "What is missing?",
            "answers": [],
            "evidence_ids": [],
            "unanswerable": True,
        },
    ]
    predictions = [
        {
            "question_id": "p1::q1",
            "question": "What is GraphRAG?",
            "predicted_answer": INSUFFICIENT_EVIDENCE,
            "retrieved_evidence_ids": ["p1::p0000"],
            "refused": True,
            "latency_ms": 1,
        },
        {
            "question_id": "p1::q2",
            "question": "What is missing?",
            "predicted_answer": INSUFFICIENT_EVIDENCE,
            "retrieved_evidence_ids": [],
            "refused": True,
            "latency_ms": 1,
        },
    ]

    metrics = evaluate_predictions(qas, predictions)
    failures = select_failure_cases(qas, predictions, limit=2)

    assert answer["refused"] is True
    assert metrics["refusal_accuracy"] == 1.0
    assert failures[0]["question_id"] == "p1::q1"
    assert failures[0]["failure_reason"] == "retrieval_miss"
    assert failures[0]["improvement_direction"]
