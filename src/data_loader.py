from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.preprocess import normalize_qasper_records, write_processed_slice


def load_qasper_records(source: str | Path | None = None, split: str = "train") -> list[dict[str, Any]]:
    """Load QASPER records from local JSON/JSONL or HuggingFace datasets."""
    if source is not None:
        return _load_local_records(Path(source))

    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional 'datasets' dependency to download real QASPER, "
            "or pass --source path/to/qasper.jsonl for an offline run."
        ) from exc

    dataset = load_dataset("allenai/qasper", split=split)
    return [dict(row) for row in dataset]


def build_processed_slice(
    output_dir: str | Path,
    source: str | Path | None = None,
    split: str = "train",
    max_papers: int = 20,
    max_qas: int = 60,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = load_qasper_records(source=source, split=split)
    papers, qas = normalize_qasper_records(records, max_papers=max_papers, max_qas=max_qas)
    write_processed_slice(papers, qas, output_dir)
    return papers, qas


def _load_local_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    raise ValueError(f"Unsupported QASPER source shape: {path}")
