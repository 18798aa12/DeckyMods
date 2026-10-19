"""Errors whose text is safe to display without credentials or private URLs."""


class ModsError(Exception):
    """An actionable, sanitized user-facing failure."""
