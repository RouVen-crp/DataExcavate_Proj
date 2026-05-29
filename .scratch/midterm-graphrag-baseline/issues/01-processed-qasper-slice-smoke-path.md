# Processed QASPER Slice smoke path

Status: ready-for-agent

## Parent

.scratch/midterm-graphrag-baseline/PRD.md

## What to build

Create the first runnable path for the Minimum Runnable GraphRAG Baseline: load a tiny QASPER-like fixture, normalize it into paper and question-answer records, and write a Processed QASPER Slice shape that later real-data code can reuse. This slice proves the repo has a working data contract before touching network downloads.

## Acceptance criteria

- [ ] A tiny local fixture can be normalized into paper records and QA records.
- [ ] Processed outputs are written as JSONL with stable identifiers for papers, paragraphs, questions, answers, and evidence.
- [ ] The normalization behavior is deterministic across repeated runs.
- [ ] Generated processed data remains ignored by git.
- [ ] A smoke command can run without network access.

## Blocked by

None - can start immediately
