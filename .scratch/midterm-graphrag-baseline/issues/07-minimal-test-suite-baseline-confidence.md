# Minimal test suite for baseline confidence

Status: ready-for-agent

## Parent

.scratch/midterm-graphrag-baseline/PRD.md

## What to build

Add a lightweight pytest suite that protects the external behavior of the Minimum Runnable GraphRAG Baseline. Tests should use tiny fixtures only and cover the data contract, audit calculations, TF-IDF retrieval, graph expansion, answer/refusal behavior, metrics, and one integration smoke run.

## Acceptance criteria

- [ ] Tests use local tiny fixtures and do not require network access.
- [ ] Data normalization tests verify paper and QA records are emitted correctly.
- [ ] Audit tests verify long-text, missing-evidence, and unanswerable counts.
- [ ] Retrieval tests verify relevant paragraphs rank above unrelated paragraphs.
- [ ] Graph tests verify co-occurrence links and one-hop expansion behavior.
- [ ] Answer/refusal tests verify extractive answer and insufficient-evidence behavior.
- [ ] Evaluation tests verify Evidence Recall@5, Answer Token F1, Refusal Accuracy, latency aggregation, and Failure Case selection.
- [ ] An integration smoke test runs the tiny fixture pipeline end to end.

## Blocked by

- .scratch/midterm-graphrag-baseline/issues/01-processed-qasper-slice-smoke-path.md
- .scratch/midterm-graphrag-baseline/issues/03-tfidf-rag-baseline-end-to-end.md
- .scratch/midterm-graphrag-baseline/issues/04-rule-based-co-occurrence-graphrag-path.md
- .scratch/midterm-graphrag-baseline/issues/05-retrieval-based-refusal-failure-cases.md
