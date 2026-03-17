from __future__ import annotations

from pathlib import Path


def ensure_user_pack_dir(packs_dir: Path, user_id: int) -> Path:
    user_dir = packs_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir
