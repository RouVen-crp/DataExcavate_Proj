# TF-IDF RAG Baseline end-to-end

Status: ready-for-agent

## Parent

.scratch/midterm-graphrag-baseline/PRD.md

## What to build

Build the TF-IDF RAG Baseline as a complete end-to-end path: index processed paragraphs, retrieve top evidence for each question, produce a Top Evidence Sentence Answer, attach evidence identifiers, and write predictions plus baseline metrics.

## Acceptance criteria

- [ ] Processed paper paragraphs can be indexed with TF-IDF.
- [ ] Each QA example can retrieve top-k evidence candidates.
- [ ] Non-refusal answers are formed as Evidence-Constrained Extractive Answers.
- [ ] Predictions include question id, predicted answer, retrieved evidence ids, scores, and latency.
- [ ] Evidence Recall@5, Answer Token F1, and average latency are computed.
- [ ] Baseline predictions and metrics are saved as report-ready artifacts.

## Blocked by

- .scratch/midterm-graphrag-baseline/issues/01-processed-qasper-slice-smoke-path.md
