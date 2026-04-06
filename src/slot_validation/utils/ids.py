from __future__ import annotations

import hashlib


def build_run_id(config_id: str, seed: int, total_wagers: int) -> str:
	raw = f"{config_id}:{seed}:{total_wagers}".encode("utf-8")
	return hashlib.sha1(raw).hexdigest()[:16]
