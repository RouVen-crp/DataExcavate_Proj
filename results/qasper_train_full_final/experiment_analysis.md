# Experiment Analysis

## Dataset Audit

- Papers: 888
- QA examples: 2593
- Paragraphs: 46882
- Long documents: 312
- Long paragraphs: 501
- Missing/incomplete evidence questions: 373
- Unanswerable questions: 278

## Method Comparison

| Method | Recall@5 | Evidence F1 | EM | Answer F1 | Refusal Acc | Unsupported Claim Rate | Latency ms |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| TF-IDF RAG Baseline | 0.511 | 0.169 | 0.003 | 0.081 | 0.266 | 0.000 | 2.249 |
| BM25-RAG Baseline | 0.532 | 0.178 | 0.004 | 0.099 | 0.014 | 0.000 | 2.105 |
| Dense Hash Vector RAG Baseline | 0.410 | 0.133 | 0.002 | 0.083 | 0.072 | 0.011 | 2.789 |
| Rule-Based Co-Occurrence GraphRAG | 0.549 | 0.184 | 0.002 | 0.084 | 0.284 | 0.000 | 100.214 |
| GraphRAG ablation: no graph edges | 0.537 | 0.188 | 0.003 | 0.086 | 0.273 | 0.000 | 6.009 |
| GraphRAG ablation: no refusal | 0.549 | 0.184 | 0.003 | 0.101 | 0.000 | 0.000 | 101.122 |
| HGESQA | 0.549 | 0.184 | 0.003 | 0.101 | 0.284 | 0.000 | 100.214 |
| HGESQA ablation: no graph edges | 0.537 | 0.188 | 0.003 | 0.086 | 0.273 | 0.000 | 6.009 |
| HGESQA ablation: no adaptive graph selection | 0.549 | 0.184 | 0.002 | 0.084 | 0.284 | 0.000 | 100.214 |
| HGESQA ablation: no answer calibration | 0.549 | 0.184 | 0.002 | 0.084 | 0.284 | 0.000 | 100.214 |
| HGESQA ablation: no refusal | 0.549 | 0.184 | 0.003 | 0.101 | 0.000 | 0.000 | 101.122 |

## Initial Diagnosis

- Best evidence recall: Rule-Based Co-Occurrence GraphRAG.
- Best answer token F1: GraphRAG ablation: no refusal.
- BM25 and dense-hash baselines cover the proposal's lexical and vector retrieval comparisons without requiring external services.
- GraphRAG ablations test whether graph edges and refusal logic contribute beyond the seed retriever.
- Unsupported Claim Rate is a deterministic proxy: a non-refusal answer is unsupported when its content tokens do not overlap retrieved evidence text.
