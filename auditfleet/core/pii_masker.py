from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MaskResult:
    text: str
    counts: dict[str, int]


_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "credit_card": re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)"),
    "taiwan_id": re.compile(r"\b[A-Z][12]\d{8}\b", re.IGNORECASE),
    "us_ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"(?<!\d)(?:\+?886[- ]?)?0?9\d{2}[- ]?\d{3}[- ]?\d{3}(?!\d)"),
}


def _mask_credit_card(match: re.Match[str]) -> str:
    digits = re.sub(r"\D", "", match.group(0))
    if not 13 <= len(digits) <= 19:
        return match.group(0)
    return "[REDACTED:CREDIT_CARD]"


def mask_pii(text: str) -> MaskResult:
    """Mask common PII before audit content is sent to any model."""
    counts: dict[str, int] = {key: 0 for key in _PATTERNS}
    masked = text

    for key, pattern in _PATTERNS.items():
        if key == "credit_card":
            def repl(match: re.Match[str]) -> str:
                replacement = _mask_credit_card(match)
                if replacement != match.group(0):
                    counts[key] += 1
                return replacement
        else:
            def repl(match: re.Match[str], label: str = key) -> str:
                counts[label] += 1
                return f"[REDACTED:{label.upper()}]"

        masked = pattern.sub(repl, masked)

    return MaskResult(text=masked, counts={k: v for k, v in counts.items() if v})
