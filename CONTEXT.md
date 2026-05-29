# DataExcavate GraphRAG

This project is a course baseline for evidence-constrained question answering over computer science papers.

## Language

**Evidence-Constrained GraphRAG QA System**:
A question answering system that retrieves paper evidence through both text retrieval and graph structure, then answers only from retrieved evidence.
_Avoid_: Full research-grade GraphRAG, production QA system

**Minimum Runnable GraphRAG Baseline**:
The smallest end-to-end GraphRAG-shaped system that can load a tiny data subset, retrieve evidence, produce answers, and output evaluation results.
_Avoid_: Optimized model, final system, advanced model

**Minimum Runnable Subset**:
A deliberately small slice of the dataset used to prove the pipeline runs end to end.
_Avoid_: Full dataset, large benchmark

**Midterm Dataset Slice**:
The project's minimum runnable subset for midterm work, capped at about 20 papers and 60 question-answer examples.
_Avoid_: Complete QASPER benchmark, full evaluation corpus

**Evidence-Constrained Extractive Answer**:
An answer formed directly from retrieved evidence text or gold answer fields, used as the default reproducible behavior.
_Avoid_: Mandatory LLM generation, unconstrained free-form answer

**Optional LLM Enhancement**:
A non-default answer generation path that can rewrite retrieved evidence into natural language when an API key is available.
_Avoid_: Required dependency, core baseline requirement

**Rule-Based Co-Occurrence Graph**:
A lightweight paper graph where extracted terms become nodes and terms appearing in the same paragraph or section become connected evidence-bearing nodes.
_Avoid_: Neo4j production graph, LLM-extracted knowledge graph

**Evidence Recall@5**:
The share of questions whose annotated evidence appears among the top five retrieved evidence candidates.
_Avoid_: General recall, model accuracy

**Answer Token F1**:
A coarse overlap score between predicted answer tokens and reference answer tokens.
_Avoid_: Exact semantic correctness, human judgment

**Refusal Accuracy**:
The share of unanswerable questions for which the system correctly returns insufficient evidence.
_Avoid_: General accuracy

**Data Audit Finding**:
A measured data quality or task difficulty issue from the midterm dataset slice that affects retrieval, answering, or evaluation.
_Avoid_: Speculation, unverified challenge

**Failure Case**:
A real evaluated question where retrieval, answering, or refusal behavior fails under the current baseline.
_Avoid_: Hypothetical example, invented error

**Processed QASPER Slice**:
A cached local subset of QASPER transformed into paper and question-answer JSONL files for repeatable midterm runs.
_Avoid_: Synthetic report data, full raw dataset checkout

**TF-IDF RAG Baseline**:
A lexical retrieval baseline that ranks paper paragraphs by TF-IDF similarity to the question before producing an evidence-constrained answer.
_Avoid_: Dense vector baseline, neural retriever

**Retrieval-Based Refusal**:
A refusal decision made when retrieved evidence is too weak and the graph has no useful entity match.
_Avoid_: LLM self-judged refusal, manual refusal label

**Top Evidence Sentence Answer**:
An extractive answer made from the most question-relevant sentence or sentences in the retrieved evidence set.
_Avoid_: Free-form generated answer, unsupported summary
