"""多角色档案地基：当前默认伊得；后续恋爱对象可切换精灵包 / 语音 / 羁绊键。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_CHARACTER_ID = "eiden"

CHARACTER_PROFILES: dict[str, dict[str, Any]] = {
    "eiden": {
        "id": "eiden",
        "display_name": "伊得",
        "sprite_pack": "eiden",
        "voice_dir": "Vpetvoice",
        "bond_key": "owner_bond",
        "date_scripts": ("park_evening",),
        "romance_enabled": True,
    },
    # 预留第二角色槽（素材就绪后填路径即可）
    "guest": {
        "id": "guest",
        "display_name": "未定名",
        "sprite_pack": "guest",
        "voice_dir": "Vpetvoice_guest",
        "bond_key": "owner_bond_guest",
        "date_scripts": (),
        "romance_enabled": False,
        "placeholder": True,
    },
}


def list_profiles(*, include_placeholder: bool = False) -> list[dict[str, Any]]:
    out = []
    for p in CHARACTER_PROFILES.values():
        if p.get("placeholder") and not include_placeholder:
            continue
        out.append(dict(p))
    return out


def get_profile(character_id: str | None = None) -> dict[str, Any]:
    cid = str(character_id or DEFAULT_CHARACTER_ID).strip() or DEFAULT_CHARACTER_ID
    return dict(CHARACTER_PROFILES.get(cid) or CHARACTER_PROFILES[DEFAULT_CHARACTER_ID])


def load_active_character(path: Path) -> str:
    if not path.is_file():
        return DEFAULT_CHARACTER_ID
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        cid = str((raw or {}).get("active_character") or DEFAULT_CHARACTER_ID)
        if cid in CHARACTER_PROFILES and not CHARACTER_PROFILES[cid].get("placeholder"):
            return cid
    except Exception:
        pass
    return DEFAULT_CHARACTER_ID


def save_active_character(path: Path, character_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cid = str(character_id or DEFAULT_CHARACTER_ID)
    if cid not in CHARACTER_PROFILES or CHARACTER_PROFILES[cid].get("placeholder"):
        cid = DEFAULT_CHARACTER_ID
    path.write_text(
        json.dumps({"active_character": cid}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_date_script(scripts_dir: Path, script_id: str) -> dict[str, Any] | None:
    """加载 data/date_scripts/{id}.json。"""
    sid = str(script_id or "").strip()
    if not sid:
        return None
    path = scripts_dir / f"{sid}.json"
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(raw, dict):
        return None
    return raw


def list_date_scripts(scripts_dir: Path) -> list[str]:
    if not scripts_dir.is_dir():
        return []
    return sorted(p.stem for p in scripts_dir.glob("*.json") if p.is_file())


def can_start_date(
    *,
    bond_level: int,
    script: dict[str, Any] | None,
    weekend_evening: bool = False,
) -> tuple[bool, str]:
    if not script:
        return False, "没有可用来的约会脚本"
    need = int(script.get("min_bond_level") or 3)
    if int(bond_level) < need:
        return False, f"羁绊达到 Lv{need} 后可邀约"
    if script.get("require_weekend_evening") and not weekend_evening:
        return False, "这份邀约更适合周末傍晚"
    return True, ""
