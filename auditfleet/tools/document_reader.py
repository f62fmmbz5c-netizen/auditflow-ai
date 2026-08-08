from pathlib import Path


def read_text_document(path: str) -> str:
    file_path = Path(path)
    if file_path.suffix.lower() not in {".txt", ".md", ".log", ".csv", ".json"}:
        raise ValueError("Phase 1 deterministic reader supports TXT/MD/LOG/CSV/JSON. PDF parsing is Phase 2.")
    return file_path.read_text(encoding="utf-8")
