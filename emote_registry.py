"""动作 / 表情素材注册表：按触发标签解析文件名，缺图回退到已有表情。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# tag → preferred sprite stems (no extension) then fallback expression names used by pet._trigger_mood_action
REACT_REGISTRY: dict[str, dict[str, Any]] = {
    "react_code": {
        "label": "写代码反应",
        "files": ("react_code_think", "react_code_1"),
        "fallback_emote": "idea",
        "trigger": "scene:code",
    },
    "react_study": {
        "label": "学习反应",
        "files": ("react_study_read", "react_study_1"),
        "fallback_emote": "like",
        "trigger": "scene:study",
    },
    "react_office": {
        "label": "办公反应",
        "files": ("react_office_nod", "react_office_1"),
        "fallback_emote": "happy",
        "trigger": "scene:office",
    },
    "react_chat": {
        "label": "聊天反应",
        "files": ("react_chat_wave", "react_chat_1"),
        "fallback_emote": "hi",
        "trigger": "scene:chat",
    },
    "react_game": {
        "label": "游戏反应",
        "files": ("react_game_cheer",),
        "fallback_emote": "happy",
        "trigger": "scene:game",
    },
    "react_video": {
        "label": "刷视频反应",
        "files": ("react_video_watch",),
        "fallback_emote": "wink",
        "trigger": "scene:video",
    },
    "react_music": {
        "label": "音乐反应",
        "files": ("react_music_sway",),
        "fallback_emote": "happy",
        "trigger": "scene:music",
    },
    "contract_focus": {
        "label": "专注契约",
        "files": ("contract_focus_1", "contract_focus_2"),
        "fallback_emote": "squat",
        "trigger": "focus_contract",
    },
    "contract_done": {
        "label": "契约完成夸赞",
        "files": ("contract_done_1",),
        "fallback_emote": "happy",
        "trigger": "focus_complete",
    },
    "bond_milestone": {
        "label": "羁绊里程碑",
        "files": ("bond_milestone_1", "bond_stage_up"),
        "fallback_emote": "like",
        "trigger": "bond_level_up",
    },
    # 恋爱预留槽
    "blush": {
        "label": "脸红（恋爱预留）",
        "files": ("blush_1", "date_blush"),
        "fallback_emote": "shy",
        "trigger": "romance",
    },
    "date_park": {
        "label": "公园约会（预留）",
        "files": ("date_park_1", "date_walk"),
        "fallback_emote": "happy",
        "trigger": "date_script",
    },
}

SCENE_TO_REACT: dict[str, str] = {
    "code": "react_code",
    "study": "react_study",
    "office": "react_office",
    "chat": "react_chat",
    "game": "react_game",
    "video": "react_video",
    "music": "react_music",
}

_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def resolve_react_tag(tag: str) -> dict[str, Any]:
    return dict(REACT_REGISTRY.get(tag) or {})


def fallback_emote_for_scene(scene: str) -> str:
    tag = SCENE_TO_REACT.get(str(scene or ""), "")
    meta = REACT_REGISTRY.get(tag) or {}
    return str(meta.get("fallback_emote") or "idea")


def find_asset_file(sprite_dirs: list[Path], stem: str) -> Path | None:
    stem = str(stem or "").strip()
    if not stem:
        return None
    for root in sprite_dirs:
        if root is None or not root.is_dir():
            continue
        for ext in _IMAGE_EXTS:
            p = root / f"{stem}{ext}"
            if p.is_file():
                return p
        # 亦允许子目录 react/
        sub = root / "react"
        if sub.is_dir():
            for ext in _IMAGE_EXTS:
                p = sub / f"{stem}{ext}"
                if p.is_file():
                    return p
    return None


def resolve_scene_reaction(
    scene: str,
    sprite_dirs: list[Path] | None = None,
) -> dict[str, Any]:
    """返回 {tag, emote, asset_path|None, label}。"""
    tag = SCENE_TO_REACT.get(str(scene or ""), "")
    meta = resolve_react_tag(tag) if tag else {}
    emote = str(meta.get("fallback_emote") or "idea")
    asset: Path | None = None
    dirs = list(sprite_dirs or [])
    for stem in meta.get("files") or ():
        asset = find_asset_file(dirs, str(stem))
        if asset is not None:
            break
    return {
        "tag": tag,
        "label": str(meta.get("label") or scene),
        "emote": emote,
        "asset_path": asset,
        "has_custom_art": asset is not None,
    }


def list_pack_checklist() -> list[dict[str, str]]:
    rows = []
    for tag, meta in REACT_REGISTRY.items():
        files = ", ".join(meta.get("files") or ())
        rows.append(
            {
                "tag": tag,
                "label": str(meta.get("label") or tag),
                "files": files,
                "fallback": str(meta.get("fallback_emote") or ""),
                "trigger": str(meta.get("trigger") or ""),
            }
        )
    return rows
