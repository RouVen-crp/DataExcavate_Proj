# PRD: Midterm Minimum Runnable GraphRAG Baseline

Status: ready-for-agent

## Problem Statement

The team needs a Minimum Runnable GraphRAG Baseline for a course midterm submission. The priority is not optimized accuracy, model quality, or system performance; the priority is having an end-to-end Evidence-Constrained GraphRAG QA System that can run on a small QASPER slice, produce measurable results, and provide enough concrete outputs to fill the midterm report.

The current repo contains project documents, agent setup, a domain glossary, and one ADR, but no runnable code yet. The midterm template requires data preprocessing and audit results, a baseline model that runs and outputs metrics, progress on the graph-based core algorithm, failure cases, a clear repo structure, and reproducible commands. The user wants to pass the course requirement with minimum reliable implementation effort.

## Solution

Build a small CPU-runnable pipeline around a Processed QASPER Slice. The pipeline downloads or loads QASPER, keeps only the Midterm Dataset Slice, audits the data, builds a TF-IDF RAG Baseline, builds a lightweight Rule-Based Co-Occurrence Graph, runs a graph-augmented retriever, produces Evidence-Constrained Extractive Answers, evaluates both methods, and writes report-ready JSON outputs.

The system should default to offline, reproducible behavior. Optional LLM Enhancement may exist later, but the baseline must not require API keys, GPU, Neo4j, dense embeddings, or large model downloads.

## User Stories

1. As a student contributor, I want one command to run the full midterm pipeline, so that I can prove the baseline works without manual steps.
2. As a student contributor, I want the pipeline to use a small QASPER subset, so that local runs stay fast and cheap.
3. As a student contributor, I want the data slice capped around 20 papers and 60 QA examples, so that the project stays within the minimum runnable scope.
4. As a student contributor, I want processed paper and QA records cached locally, so that repeated experiments do not redownload or reparse everything.
5. As a student contributor, I want raw full QASPER data excluded from git, so that the GitHub repo remains lightweight.
6. As a student contributor, I want clear setup instructions, so that reviewers and teammates can reproduce the baseline.
7. As a student contributor, I want the system to run on CPU, so that no GPU dependency blocks the midterm.
8. As a student contributor, I want a TF-IDF RAG Baseline, so that there is a simple comparison point against graph-augmented retrieval.
9. As a student contributor, I want a Rule-Based Co-Occurrence Graph, so that the project has a GraphRAG-shaped core without Neo4j or LLM relation extraction.
10. As a student contributor, I want graph expansion from TF-IDF seed evidence, so that the proposed method visibly differs from plain lexical retrieval.
11. As a student contributor, I want top-k retrieved evidence saved per question, so that I can inspect retrieval behavior.
12. As a student contributor, I want Evidence-Constrained Extractive Answers, so that answers remain tied to retrieved evidence.
13. As a student contributor, I want Retrieval-Based Refusal, so that unanswerable questions can be handled in a simple measurable way.
14. As a student contributor, I want output evidence identifiers attached to answers, so that the report can discuss traceability.
15. As a student contributor, I want Evidence Recall@5 computed, so that retrieval quality can be reported quantitatively.
16. As a student contributor, I want Answer Token F1 computed, so that answer quality has at least one automatic metric.
17. As a student contributor, I want Refusal Accuracy computed, so that refusal behavior is visible for unanswerable questions.
18. As a student contributor, I want average latency computed, so that the report can include a usability metric.
19. As a student contributor, I want baseline and GraphRAG metrics in separate files, so that the report table is easy to fill.
20. As a student contributor, I want at least two Failure Cases exported from real evaluation results, so that the report does not rely on invented examples.
21. As a student contributor, I want data audit outputs, so that the report can list measured Data Audit Findings.
22. As a student contributor, I want audit results for long document or long paragraph behavior, so that the need for retrieval is justified.
23. As a student contributor, I want audit results for missing or incomplete evidence, so that evaluation limits are documented.
24. As a student contributor, I want audit results for unanswerable questions, so that refusal support is justified.
25. As a student contributor, I want deterministic outputs where practical, so that repeated runs do not confuse the report.
26. As a teammate, I want modules with small public interfaces, so that future group members can replace pieces without rewriting everything.
27. As a teammate, I want the optional LLM path kept separate from the baseline, so that API failures do not block reproducibility.
28. As a teammate, I want future improvements documented as out of scope, so that unfinished optimization work can be assigned later.
29. As a reviewer, I want a README with environment setup and commands, so that I can run the baseline independently.
30. As a reviewer, I want real outputs from real QASPER examples, so that the project is not synthetic or toy-only.
31. As a reviewer, I want a visible comparison between TF-IDF RAG and graph-augmented retrieval, so that the core project idea is represented.
32. As a reviewer, I want failure analysis backed by saved predictions, so that the report diagnosis is credible.
33. As a reviewer, I want the repo structure to match the midterm template expectations, so that project progress is easy to audit.
34. As a future implementer, I want entity extraction to be rule-based and testable, so that graph construction can be debugged without model calls.
35. As a future implementer, I want retrieval scoring separated from answer extraction, so that each piece can be changed independently.
36. As a future implementer, I want evaluation separated from model execution, so that saved predictions can be re-evaluated if metrics change.

## Implementation Decisions

- Build a Minimum Runnable GraphRAG Baseline, not a full research-grade GraphRAG system.
- Use a Midterm Dataset Slice capped around 20 papers and 60 QA examples.
- Use real QASPER data for report metrics; do not fabricate report data.
- Cache the Processed QASPER Slice as local JSONL artifacts.
- Keep full raw datasets, generated processed data, and result outputs out of git.
- Use a TF-IDF RAG Baseline as the plain retrieval comparison.
- Use a Rule-Based Co-Occurrence Graph for the proposed graph-augmented retrieval method.
- Follow ADR-0001: use TF-IDF seed retrieval plus one-hop rule-based graph expansion instead of Neo4j, dense embeddings, or LLM-based relation extraction.
- GraphRAG retrieval should use TF-IDF top seed paragraphs, extract query and seed terms, expand through one-hop graph neighbors, collect candidate evidence paragraphs, and rerank using lexical score plus graph bonus.
- Use Evidence-Constrained Extractive Answers as default output.
- Use Top Evidence Sentence Answer for non-refusal answers.
- Use Retrieval-Based Refusal when retrieved evidence is weak and graph matches are absent.
- Treat Optional LLM Enhancement as non-default and out of the core baseline path.
- Produce report-ready artifacts for audit, baseline metrics, GraphRAG metrics, predictions, and failure cases.
- Keep module boundaries deep and stable:
  - Data slice module: loads QASPER and emits normalized paper/QA records.
  - Audit module: computes Data Audit Findings from normalized records.
  - Lexical retrieval module: owns TF-IDF indexing and top-k paragraph retrieval.
  - Graph module: owns rule-based term extraction, co-occurrence graph construction, and graph expansion.
  - Answer module: owns refusal and extractive answer selection.
  - Evaluation module: owns Evidence Recall@5, Answer Token F1, Refusal Accuracy, latency aggregation, and Failure Case selection.
  - Runner module: orchestrates end-to-end execution and writes artifacts.
- Write README instructions around one-command reproduction and a minimal example run.
- Keep CLI options for maximum papers, maximum QA examples, top-k, and output directory.

## Testing Decisions

- Tests should verify external behavior and saved outputs, not private implementation details.
- Use tiny local fixtures for tests only; do not use synthetic data for report metrics.
- Test the data slice module with a tiny QASPER-like record to ensure normalized paper and QA records are produced.
- Test the audit module by checking that known long paragraphs, missing evidence, and unanswerable examples produce expected counts.
- Test the lexical retrieval module by checking that a query ranks the paragraph containing matching terms above unrelated paragraphs.
- Test the graph module by checking that co-occurring terms create graph links and that one-hop expansion returns related evidence candidates.
- Test the answer module by checking refusal behavior when retrieval is weak and extractive answer behavior when evidence is strong.
- Test the evaluation module by checking Evidence Recall@5, Answer Token F1, Refusal Accuracy, latency aggregation, and Failure Case selection on controlled predictions.
- Add one integration smoke test for the full tiny fixture pipeline.
- Current repo has no prior test suite; use lightweight pytest tests as the initial testing pattern.

## Out of Scope

- Full QASPER benchmark evaluation.
- Dense vector retrieval and FAISS embeddings.
- Neo4j setup, graph database persistence, or graph visualization tooling.
- LLM-based entity and relation extraction.
- Mandatory DeepSeek or other LLM answer generation.
- RAGAS, NLI faithfulness scoring, or human evaluation.
- Performance optimization beyond keeping the small baseline runnable.
- Large-scale ablation experiments.
- High-quality entity normalization or alias resolution.
- Final report writing beyond producing report-ready artifacts.
- Multi-user collaboration workflow beyond basic GitHub repo synchronization.

## Further Notes

- The PRD is scoped for passing the midterm with the lowest reliable implementation effort.
- The project should preserve the language in the domain glossary: Minimum Runnable GraphRAG Baseline, Midterm Dataset Slice, Processed QASPER Slice, TF-IDF RAG Baseline, Rule-Based Co-Occurrence Graph, Evidence-Constrained Extractive Answer, Retrieval-Based Refusal, and Failure Case.
- The main risk is overbuilding. Any change that adds a hard dependency, large download, GPU need, API key requirement, or complex service should be deferred unless it directly helps the midterm minimum.
- Future teammates can improve dense retrieval, LLM generation, Neo4j persistence, graph schema quality, and richer evaluation after this baseline exists.
