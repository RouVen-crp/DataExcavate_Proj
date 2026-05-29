from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.answering import INSUFFICIENT_EVIDENCE
from src.retrieval import TOKEN_RE


def evaluate_predictions(
    qas: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    top_k: int = 5,
) -> dict[str, Any]:
    prediction_by_id = {prediction.get("question_id"): prediction for prediction in predictions}
    recall_hits = 0
    recall_total = 0
    f1_values: list[float] = []
    refusal_hits = 0
    refusal_total = 0
    latencies: list[float] = []

    for qa in qas:
        prediction = prediction_by_id.get(qa.get("question_id"), {})
        retrieved_ids = prediction.get("retrieved_evidence_ids", [])[:top_k]
        gold_ids = qa.get("evidence_ids", [])
        if gold_ids:
            recall_total += 1
            if set(gold_ids) & set(retrieved_ids):
                recall_hits += 1

        if qa.get("answers"):
            f1_values.append(_best_answer_f1(str(prediction.get("predicted_answer", "")), qa.get("answers", [])))

        if qa.get("unanswerable"):
            refusal_total += 1
            if prediction.get("refused") or prediction.get("predicted_answer") == INSUFFICIENT_EVIDENCE:
                refusal_hits += 1

        if prediction.get("latency_ms") is not None:
            latencies.append(float(prediction["latency_ms"]))

    return {
        "questions": len(qas),
        "evidence_recall_at_5": recall_hits / recall_total if recall_total else 0.0,
        "answer_token_f1": sum(f1_values) / len(f1_values) if f1_values else 0.0,
        "refusal_accuracy": refusal_hits / refusal_total if refusal_total else 0.0,
        "average_latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
    }


def write_json(path: str | Path, payload: Any) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def _best_answer_f1(predicted: str, answers: list[str]) -> float:
    return max((_token_f1(predicted, answer) for answer in answers), default=0.0)


def _token_f1(predicted: str, reference: str) -> float:
    predicted_tokens = [token.lower() for token in TOKEN_RE.findall(predicted)]
    reference_tokens = [token.lower() for token in TOKEN_RE.findall(reference)]
    if not predicted_tokens or not reference_tokens:
        return 0.0
    overlap = 0
    remaining = reference_tokens.copy()
    for token in predicted_tokens:
        if token in remaining:
            overlap += 1
            remaining.remove(token)
    if overlap == 0:
        return 0.0
    precision = overlap / len(predicted_tokens)
    recall = overlap / len(reference_tokens)
    return 2 * precision * recall / (precision + recall)
