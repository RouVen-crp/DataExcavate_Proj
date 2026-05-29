from __future__ import annotations

import re
from typing import Any

from src.retrieval import TOKEN_RE


INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


def answer_from_evidence(
    question: str,
    evidence: list[dict[str, Any]],
    min_score: float = 0.05,
) -> dict[str, Any]:
    if not evidence or float(evidence[0].get("score", 0.0)) < min_score:
        return {"answer": INSUFFICIENT_EVIDENCE, "evidence_ids": [], "refused": True}

    sentence = _best_sentence(question, str(evidence[0].get("text", "")))
    return {
        "answer": sentence,
        "evidence_ids": [evidence[0].get("paragraph_id")],
        "refused": False,
    }


def _best_sentence(question: str, text: str) -> str:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    if not sentences:
        return text.strip()
    query_terms = {token.lower() for token in TOKEN_RE.findall(question)}
    return max(
        sentences,
        key=lambda sentence: (
            len(query_terms & {token.lower() for token in TOKEN_RE.findall(sentence)}),
            -len(sentence),
        ),
    )
