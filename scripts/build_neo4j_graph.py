from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.neo4j_graph import Neo4jGraphStore
from src.preprocess import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Neo4j graph from processed papers.jsonl.")
    parser.add_argument(
        "--papers",
        default="results/midterm/processed/papers.jsonl",
        help="Path to processed papers.jsonl.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing Neo4j database before ingest.",
    )
    args = parser.parse_args()

    papers = read_jsonl(args.papers)
    store = Neo4jGraphStore()
    try:
        if args.clear:
            store.clear()
            print("neo4j database cleared")
        stats = store.ingest_papers(papers)
        print(json.dumps({"papers_loaded": len(papers), "ingest_stats": stats}, ensure_ascii=False, indent=2))
    finally:
        store.close()


if __name__ == "__main__":
    main()
