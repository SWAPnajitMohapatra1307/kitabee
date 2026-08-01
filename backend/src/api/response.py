"""Standard response envelope helpers.

Every API response follows the envelope contract defined in RULES §12.
This module is the single source of truth for that shape.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional


API_VERSION = "v1"


# Public API

def success_envelope(data: Any) -> dict[str, Any]:
    """Wrap a payload in the standard success envelope.

    Args:
        data: The response payload (any JSON-serializable value).

    Returns:
        Envelope with success=True, data, and meta block.
    """
    return {
        "success": True,
        "data": data,
        "meta": _meta(),
    }


def error_envelope(
    code: str,
    message: str,
    details: Optional[Any] = None,
) -> dict[str, Any]:
    """Wrap an error in the standard error envelope.

    Args:
        code: Machine-readable error code (e.g. "UPSTREAM_UNAVAILABLE").
        message: Human-readable error message.
        details: Optional structured extra information.

    Returns:
        Envelope with success=False, error block, and meta block.
    """
    error_block: dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if details is not None:
        error_block["details"] = details

    return {
        "success": False,
        "error": error_block,
        "meta": _meta(),
    }


# Private helpers

def _meta() -> dict[str, Any]:
    """Build the meta block attached to every response."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": API_VERSION,
    }