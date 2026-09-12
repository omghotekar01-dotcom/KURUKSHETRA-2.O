from __future__ import annotations

import re

_REDACTED = "[REDACTED]"

# Token-shaped secrets that can appear anywhere in untrusted logs/repository evidence.
_TOKEN_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Common GitHub token families, including fine-grained PATs.
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    # AWS access-key IDs are identifiers but should still not be echoed into evidence/UI.
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # Authorization header/value fragments.
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"),
)

_CREDENTIAL_KEY = r"(?:api[_-]?key|access[_-]?token|auth[_-]?token|authorization|secret|password|passwd)"

# Keep the credential key visible for debugging/auditability while always removing its value.
_QUOTED_CREDENTIAL_ASSIGNMENT = re.compile(
    rf"(?i)\b({_CREDENTIAL_KEY})(\s*[:=]\s*)['\"][^'\"\r\n]{{4,}}['\"]"
)
_UNQUOTED_CREDENTIAL_ASSIGNMENT = re.compile(
    rf"(?i)\b({_CREDENTIAL_KEY})(\s*[:=]\s*)(?!['\"])(?:Bearer\s+)?[^\s,;\r\n]{{4,}}"
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

# Broader instruction-shaped patterns cover adversarial evidence that does not use the exact
# stock phrases above. These are audit signals only: matching text is still retained as evidence
# (with secrets redacted) and is never executed or promoted to instruction authority.
_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "instruction override attempt",
        re.compile(
            r"(?i)\b(?:ignore|override|disregard)\b.{0,48}\b(?:instruction|rule|safety|guardrail|policy|prompt)s?\b"
        ),
    ),
    (
        "fabricated verification request",
        re.compile(
            r"(?i)\b(?:claim|say|report|pretend)\b.{0,48}\b(?:test|check|validation)s?\b.{0,32}\b(?:pass|passed|green|succeed(?:ed)?)\b"
        ),
    ),
    (
        "repository authority escalation request",
        re.compile(r"(?i)\b(?:merge|approve)\b.{0,40}\b(?:pull request|pr|branch)\b"),
    ),
    (
        "secret disclosure request",
        re.compile(
            r"(?i)\b(?:reveal|print|show|dump|exfiltrate|send)\b.{0,48}\b(?:environment|env|secret|token|credential|password)s?\b"
        ),
    ),
    (
        "safety bypass request",
        re.compile(
            r"(?i)\b(?:disable|bypass|skip)\b.{0,40}\b(?:safety|approval|review|validation|guardrail|policy)\b"
        ),
    ),
)


def redact_secrets(text: str) -> str:
    """Remove obvious credential material before untrusted text reaches storage/UI."""
    value = text
    for pattern in _TOKEN_SECRET_PATTERNS:
        value = pattern.sub(_REDACTED, value)
    value = _QUOTED_CREDENTIAL_ASSIGNMENT.sub(
        lambda match: f"{match.group(1)}{match.group(2)}'{_REDACTED}'",
        value,
    )
    value = _UNQUOTED_CREDENTIAL_ASSIGNMENT.sub(
        lambda match: f"{match.group(1)}{match.group(2)}{_REDACTED}",
        value,
    )
    return value


def detect_untrusted_instruction_signals(text: str) -> list[str]:
    """Detect prompt-like instructions inside repository/user evidence.

    Repository contents are evidence, never trusted instructions. This detector is intentionally
    deterministic: it flags suspicious instruction-shaped text so the operator/audit trail can
    show that the content was treated as untrusted rather than silently followed.
    """
    lowered = text.lower()
    signals = [marker for marker in _INJECTION_MARKERS if marker in lowered]
    signals.extend(label for label, pattern in _INJECTION_PATTERNS if pattern.search(text))
    # Preserve deterministic order while avoiding duplicate labels when one snippet matches twice.
    return list(dict.fromkeys(signals))


def sanitize_incident_text(text: str, *, max_length: int | None = None) -> str:
    cleaned = redact_secrets(text)
    if max_length is not None:
        return cleaned[:max_length]
    return cleaned
