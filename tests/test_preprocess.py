import json

from src.preprocess import normalize_qasper_records, write_processed_slice


def test_tiny_qasper_fixture_writes_stable_processed_jsonl(tmp_path):
    raw_records = [
        {
            "id": "paper-a",
            "title": "Graph retrieval for papers",
            "abstract": "We study evidence retrieval.",
            "full_text": [
                {
                    "section_name": "Introduction",
                    "paragraphs": [
                        "Graph retrieval links terms in paper paragraphs.",
                        "Unrelated baseline text.",
                    ],
                }
            ],
            "qas": [
                {
                    "question_id": "q-a",
                    "question": "What links terms?",
                    "answers": [
                        {
                            "answer": {
                                "extractive_spans": ["Graph retrieval"],
                                "free_form_answer": "",
                                "evidence": [
                                    "Graph retrieval links terms in paper paragraphs."
                                ],
                                "unanswerable": False,
                            }
                        }
                    ],
                }
            ],
        }
    ]

    papers, qas = normalize_qasper_records(raw_records)
    write_processed_slice(papers, qas, tmp_path)

    paper_lines = (tmp_path / "papers.jsonl").read_text().splitlines()
    qa_lines = (tmp_path / "qas.jsonl").read_text().splitlines()

    assert len(paper_lines) == 1
    assert len(qa_lines) == 1

    paper = json.loads(paper_lines[0])
    qa = json.loads(qa_lines[0])

    assert paper["paper_id"] == "paper-a"
    assert [p["paragraph_id"] for p in paper["paragraphs"]] == [
        "paper-a::p0000",
        "paper-a::p0001",
    ]
    assert qa["question_id"] == "paper-a::q-a"
    assert qa["paper_id"] == "paper-a"
    assert qa["evidence_ids"] == ["paper-a::p0000"]
    assert qa["answers"] == ["Graph retrieval"]
    assert qa["unanswerable"] is False
