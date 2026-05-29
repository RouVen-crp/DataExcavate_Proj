from src.answering import answer_from_evidence
from src.evaluate import evaluate_predictions
from src.retrieval import TfidfRetriever


def test_tfidf_baseline_retrieves_answers_and_scores_predictions():
    papers = [
        {
            "paper_id": "p1",
            "paragraphs": [
                {
                    "paragraph_id": "p1::p0000",
                    "paper_id": "p1",
                    "section": "Intro",
                    "text": "Graph retrieval connects evidence terms for question answering.",
                },
                {
                    "paragraph_id": "p1::p0001",
                    "paper_id": "p1",
                    "section": "Intro",
                    "text": "The training loop uses unrelated optimizer details.",
                },
            ],
        }
    ]
    qas = [
        {
            "question_id": "p1::q1",
            "paper_id": "p1",
            "question": "What connects evidence terms?",
            "answers": ["Graph retrieval"],
            "evidence_ids": ["p1::p0000"],
            "unanswerable": False,
        }
    ]

    retriever = TfidfRetriever.from_papers(papers)
    evidence = retriever.retrieve(qas[0]["question"], paper_id="p1", top_k=2)
    answer = answer_from_evidence(qas[0]["question"], evidence)
    prediction = {
        "question_id": qas[0]["question_id"],
        "predicted_answer": answer["answer"],
        "retrieved_evidence_ids": [item["paragraph_id"] for item in evidence],
        "scores": [item["score"] for item in evidence],
        "latency_ms": 1.0,
        "refused": answer["refused"],
    }
    metrics = evaluate_predictions(qas, [prediction], top_k=5)

    assert evidence[0]["paragraph_id"] == "p1::p0000"
    assert answer["answer"] == "Graph retrieval connects evidence terms for question answering."
    assert metrics["evidence_recall_at_5"] == 1.0
    assert metrics["answer_token_f1"] > 0
    assert metrics["average_latency_ms"] == 1.0
