from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from run_midterm import parse_optional_limit, run_pipeline
from src.evaluate import write_json


def parse_scale(value: str) -> tuple[int | None, int | None]:
    """Parse PAPER_CAP:QA_CAP, where either cap may be 'all'."""
    parts = value.split(":")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("scale must use PAPER_CAP:QA_CAP, for example 20:60 or all:all")
    return parse_optional_limit(parts[0]), parse_optional_limit(parts[1])


def scale_name(max_papers: int | None, max_qas: int | None) -> str:
    paper_label = "all" if max_papers is None else str(max_papers)
    qa_label = "all" if max_qas is None else str(max_qas)
    return f"papers-{paper_label}_qas-{qa_label}"


def run_scale_experiments(
    scales: list[tuple[int | None, int | None]],
    output_dir: str | Path = "results/scale_experiments",
    source: str | Path | None = None,
    split: str = "train",
    top_k: int = 5,
) -> list[dict[str, Any]]:
    output_path = Path(output_dir)
    comparisons: list[dict[str, Any]] = []
    for max_papers, max_qas in scales:
        name = scale_name(max_papers, max_qas)
        summary = run_pipeline(
            source=source,
            output_dir=output_path / name,
            max_papers=max_papers,
            max_qas=max_qas,
            top_k=top_k,
            split=split,
        )
        comparisons.append(
            {
                "scale": name,
                "papers": summary["papers"],
                "qas": summary["qas"],
                "full_dataset": summary["full_dataset"],
                "baseline": summary["baseline"],
                "graphrag": summary["graphrag"],
            }
        )
    write_json(output_path / "comparison.json", comparisons)
    return comparisons


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TF-IDF and GraphRAG comparisons at one or more dataset scales.")
    parser.add_argument(
        "--scale",
        action="append",
        type=parse_scale,
        dest="scales",
        help="Repeatable PAPER_CAP:QA_CAP value, for example --scale 20:60 --scale all:all.",
    )
    parser.add_argument("--source", default=None, help="Optional local QASPER JSON/JSONL source.")
    parser.add_argument("--output-dir", default="results/scale_experiments", help="Artifact output directory.")
    parser.add_argument("--split", default="train", help="Official QASPER split: train, validation, or test.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of evidence paragraphs to retrieve.")
    args = parser.parse_args()

    comparisons = run_scale_experiments(
        scales=args.scales or [(20, 60), (None, None)],
        output_dir=args.output_dir,
        source=args.source,
        split=args.split,
        top_k=args.top_k,
    )
    for result in comparisons:
        print(
            f"scale={result['scale']} papers={result['papers']} qas={result['qas']} "
            f"baseline_recall@{args.top_k}={result['baseline']['evidence_recall_at_k']:.3f} "
            f"graphrag_recall@{args.top_k}={result['graphrag']['evidence_recall_at_k']:.3f}"
        )
    print(f"comparison={Path(args.output_dir) / 'comparison.json'}")


if __name__ == "__main__":
    main()
