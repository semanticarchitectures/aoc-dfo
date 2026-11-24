"""Corpus ingest (Phase 1): turn registered public sources into anchored, hash-pinned text and
element tables. Each ingester records what it read (commit or URL, SHA-256, retrieval date) so the
output can be reproduced and every row cited with an anchor (R1.2, R5.4)."""
