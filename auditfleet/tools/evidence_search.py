def search_evidence(text: str, term: str) -> list[dict[str, str | int]]:
    """Return simple line-level evidence matches for deterministic audit tracing."""
    results: list[dict[str, str | int]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if term.lower() in line.lower():
            results.append({"line": number, "text": line.strip()})
    return results
