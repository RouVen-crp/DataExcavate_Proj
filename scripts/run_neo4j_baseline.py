from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluate import evaluate_predictions, write_json
from src.neo4j_graph import Neo4jGraphStore, run_neo4j_graph_rag
from src.preprocess import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Neo4j-backed GraphRAG and export metrics.")
    parser.add_argument(
        "--papers",
        default="results/midterm/processed/papers.jsonl",
        help="Processed papers.jsonl path.",
    )
    parser.add_argument(
        "--qas",
        default="results/midterm/processed/qas.jsonl",
        help="Processed qas.jsonl path.",
    )
    parser.add_argument("--output-dir", default="results/neo4j_compare", help="Output directory.")
    parser.add_argument("--top-k", type=int, default=5, help="Top-k evidence paragraphs.")
    parser.add_argument("--max-hops", type=int, default=1, help="Neo4j CO_OCCURS expansion hops.")
    args = parser.parse_args()

    papers = read_jsonl(args.papers)
    qas = read_jsonl(args.qas)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    store = Neo4jGraphStore()
    try:
        predictions = run_neo4j_graph_rag(
            papers,
            qas,
            store,
            top_k=args.top_k,
            max_hops=args.max_hops,
        )
    finally:
        store.close()

    metrics = evaluate_predictions(qas, predictions, top_k=args.top_k)
    write_json(output_dir / "neo4j_predictions.json", predictions)
    write_json(output_dir / "neo4j_metrics.json", metrics)
    print(
        f"recall@{args.top_k}={metrics['evidence_recall_at_k']:.3f} "
        f"f1={metrics['answer_token_f1']:.3f} "
        f"refusal={metrics['refusal_accuracy']:.3f} "
        f"latency={metrics['average_latency_ms']:.2f}ms"
    )
    print(f"output_dir={output_dir}")


if __name__ == "__main__":
    main()
