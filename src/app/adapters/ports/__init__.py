"""Ports (interfaces) for outbound operations. Implemented by adapters."""

from .database import DatabaseSessionPort

__all__ = ["DatabaseSessionPort"]
