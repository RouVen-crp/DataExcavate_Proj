from __future__ import annotations

import json
import os
import tarfile
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from src.preprocess import normalize_qasper_records, write_processed_slice


QASPER_ARCHIVES = {
    "train": (
        "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz",
        "qasper-train-v0.3.json",
    ),
    "validation": (
        "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz",
        "qasper-dev-v0.3.json",
    ),
    "test": (
        "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-test-and-evaluator-v0.3.tgz",
        "qasper-test-v0.3.json",
    ),
}


def load_qasper_records(source: str | Path | None = None, split: str = "train") -> list[dict[str, Any]]:
    """Load local QASPER-like data or cache the official QASPER v0.3 JSON."""
    if source is not None:
        return _load_local_records(Path(source))
    return _load_official_qasper_records(split)


def _load_official_qasper_records(split: str) -> list[dict[str, Any]]:
    if split not in QASPER_ARCHIVES:
        supported = ", ".join(sorted(QASPER_ARCHIVES))
        raise ValueError(f"Unsupported QASPER split '{split}'. Choose one of: {supported}")

    archive_url, filename = QASPER_ARCHIVES[split]
    cache_root = Path(os.environ.get("QASPER_CACHE_DIR", "data/raw/qasper"))
    cache_path = cache_root / filename
    if cache_path.exists():
        return _load_local_records(cache_path)

    cache_root.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(archive_url) as response:
            archive_bytes = response.read()
    except OSError as exc:
        raise RuntimeError(
            f"Could not download official QASPER split '{split}' from {archive_url}. "
            "Pass --source path/to/qasper.json for an offline run."
        ) from exc

    with tarfile.open(fileobj=BytesIO(archive_bytes), mode="r:gz") as archive:
        member = next((item for item in archive.getmembers() if Path(item.name).name == filename), None)
        if member is None:
            raise RuntimeError(f"Official QASPER archive did not contain {filename}")
        handle = archive.extractfile(member)
        if handle is None:
            raise RuntimeError(f"Could not read {filename} from the official QASPER archive")
        payload = json.loads(handle.read().decode("utf-8"))

    cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return _records_from_payload(payload, cache_path)


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
    return _records_from_payload(payload, path)


def _records_from_payload(payload: Any, path: Path) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    if isinstance(payload, dict) and all(isinstance(value, dict) for value in payload.values()):
        return [{"id": paper_id, **record} for paper_id, record in payload.items()]
    raise ValueError(f"Unsupported QASPER source shape: {path}")
