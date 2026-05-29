# Midterm Dataset Slice and Data Audit Findings

Status: ready-for-agent

## Parent

.scratch/midterm-graphrag-baseline/PRD.md

## What to build

Extend the processed-data path to use real QASPER data with a Midterm Dataset Slice capped around 20 papers and 60 QA examples, then produce report-ready Data Audit Findings. The audit should quantify long document or paragraph behavior, missing or incomplete evidence, and unanswerable question share.

## Acceptance criteria

- [ ] Real QASPER data can be loaded and capped by maximum papers and maximum QA examples.
- [ ] The resulting Processed QASPER Slice is cached locally as JSONL.
- [ ] The audit output includes document/paragraph length statistics.
- [ ] The audit output includes missing or incomplete evidence statistics.
- [ ] The audit output includes unanswerable question statistics.
- [ ] The audit output is saved as report-ready JSON.

## Blocked by

- .scratch/midterm-graphrag-baseline/issues/01-processed-qasper-slice-smoke-path.md
