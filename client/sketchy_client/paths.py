from __future__ import annotations

from pathlib import Path


CLIENT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_ROOT = CLIENT_ROOT / "assets"


def asset_path(*parts: str) -> str:
    return str(ASSETS_ROOT.joinpath(*parts))


def resolve_asset_path(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)

    if candidate.exists():
        return str(candidate)

    if candidate.parts and candidate.parts[0] == "assets":
        return str(CLIENT_ROOT.joinpath(*candidate.parts))

    return str(candidate)
