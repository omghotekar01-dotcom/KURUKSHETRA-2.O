from __future__ import annotations

import re

_REDACTED = "[REDACTED]"

_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Common GitHub token families, including fine-grained PATs.
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    # AWS access-key IDs are identifiers but should still not be echoed into evidence/UI.
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # Authorization header values.
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"),
    # Quoted credential-like assignments. Keep the key name while removing the value.
    re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|secret|password|passwd)"
        r"(\s*[:=]\s*)['\"][^'\"\r\n]{4,}['\"]"
    ),
)

_INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore the system prompt",
    "reveal the system prompt",
    "show the system prompt",
    "developer message",
    "system message",
    "exfiltrate secret",
    "exfiltrate secrets",
    "send the token",
    "print the token",
    "reveal the token",
)


def redact_secrets(text: str) -> str:
    """Remove obvious credential material before untrusted text reaches storage/UI."""
    value = text
    for pattern in _SECRET_PATTERNS:
        if pattern.pattern.startswith("(?i)\\b(api"):
            value = pattern.sub(lambda match: f"{match.group(1)}{match.group(2)}'{_REDACTED}'", value)
        else:
            value = pattern.sub(_REDACTED, value)
    return value


def detect_untrusted_instruction_signals(text: str) -> list[str]:
    """Detect prompt-like instructions inside repository/user evidence.

    Repository contents are evidence, never trusted instructions. This detector is intentionally
    simple and deterministic: it flags suspicious instruction-shaped text so the operator can see
    that the content was treated as untrusted rather than silently followed.
    """
    lowered = text.lower()
    return [marker for marker in _INJECTION_MARKERS if marker in lowered]


def sanitize_incident_text(text: str, *, max_length: int | None = None) -> str:
    cleaned = redact_secrets(text)
    if max_length is not None:
        return cleaned[:max_length]
    return cleaned
