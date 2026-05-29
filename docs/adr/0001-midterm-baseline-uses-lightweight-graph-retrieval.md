# Midterm baseline uses lightweight graph retrieval

For the midterm baseline, we use TF-IDF seed retrieval plus one-hop rule-based co-occurrence graph expansion instead of Neo4j, dense embeddings, or LLM-based relation extraction. This keeps the evidence-constrained GraphRAG pipeline runnable on a small QASPER slice with CPU-only resources while still preserving the core comparison between lexical RAG and graph-augmented retrieval.
