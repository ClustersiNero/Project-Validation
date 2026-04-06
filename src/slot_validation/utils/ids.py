from __future__ import annotations

import hashlib


def build_run_id(game_id: str, seed: int, mode_id: int, spins: int) -> str:
	"""Build stable short id for a simulation run."""
	raw = f"{game_id}:{seed}:{mode_id}:{spins}".encode("utf-8")
	return hashlib.sha1(raw).hexdigest()[:12]
