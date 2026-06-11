"""Kanonikus tár (SQLite): az igazságforrás, idempotens upserttel."""

from ingest.storage.sqlite_store import CanonicalStore

__all__ = ["CanonicalStore"]
