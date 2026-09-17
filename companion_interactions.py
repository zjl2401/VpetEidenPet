"""Long-term companion prompts and user-supplied reaction-image slots.

This module deliberately keeps the assets outside the bundled sprite set: players can
replace the images without editing the program or overwriting their save data.
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any

SLOT_DEFS: tuple[dict[str, str], ...] = (
    {"id": "greet", "label": "见面招呼", "hint": "放入打招呼 / 挥手图片"},
    {"id": "cheer", "label": "专注鼓励", "hint": "放入加油 / 陪伴图片"},
    {"id": "celebrate", "label": "完成庆祝", "hint": "放入完成任务时的图片"},
    {"id": "cozy", "label": "家园休憩", "hint": "放入家园闲聊图片"},
    {"id": "shy", "label": "害羞回应", "hint": "放入脸红 / 小表情图片"},
    {"id": "free", "label": "自由槽位", "hint": "留给你的自定义动作或表情"},
)


def default_state() -> dict[str, Any]:
    return {"slots": {}, "prompt_day": "", "prompt_done": []}


def load(path: Path) -> dict[str, Any]:
    state = default_state()
    try:
        raw = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except Exception:
        raw = {}
    if isinstance(raw, dict):
        slots = raw.get("slots")
        state["slots"] = dict(slots) if isinstance(slots, dict) else {}
        state["prompt_day"] = str(raw.get("prompt_day") or "")
        done = raw.get("prompt_done")
        state["prompt_done"] = list(done) if isinstance(done, list) else []
    return state


def save(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def set_slot(path: Path, slot_id: str, source: Path | None) -> dict[str, Any]:
    """Copy a player image into a stable custom-assets folder; None clears a slot."""
    allowed = {str(item["id"]) for item in SLOT_DEFS}
    if slot_id not in allowed:
        raise ValueError(f"unknown slot: {slot_id}")
    state = load(path)
    target_dir = path.parent / "custom_reactions"
    target_dir.mkdir(parents=True, exist_ok=True)
    old = str(state["slots"].get(slot_id) or "")
    if source is None:
        state["slots"].pop(slot_id, None)
        if old:
            try:
                (path.parent / old).unlink(missing_ok=True)
            except OSError:
                pass
        save(path, state)
        return state
    if not source.is_file() or source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        raise ValueError("unsupported image")
    ext = source.suffix.lower()
    dest = target_dir / f"{slot_id}{ext}"
    shutil.copy2(source, dest)
    state["slots"][slot_id] = str(dest.relative_to(path.parent)).replace("\\", "/")
    save(path, state)
    return state


def slot_path(state_path: Path, state: dict[str, Any], slot_id: str) -> Path | None:
    rel = str((state.get("slots") or {}).get(slot_id) or "")
    path = (state_path.parent / rel).resolve()
    try:
        path.relative_to(state_path.parent.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def daily_prompts(path: Path, *, day: str | None = None) -> list[dict[str, str]]:
    """Return three rotating, once-per-day conversation starters."""
    today = day or time.strftime("%Y-%m-%d")
    state = load(path)
    if state["prompt_day"] != today:
        state["prompt_day"] = today
        state["prompt_done"] = []
        save(path, state)
    seed = sum(ord(c) for c in today)
    pool = (
        ("check_in", "今天最想完成哪一件事？", "我先替你记住这件小目标。"),
        ("memory", "今天有没有一件想一起记下的小事？", "好，我会把它当成今天的小回忆。"),
        ("care", "现在的你更需要：加油、安静陪伴，还是休息？", "收到，我会按你的节奏陪着。"),
        ("home", "要不要为家园留一个小角落？", "等你放好，我想去那里坐一会儿。"),
        ("thanks", "今天有什么值得对自己说“做得好”的地方？", "我也觉得你做得很好。"),
    )
    picks = [pool[(seed + i * 2) % len(pool)] for i in range(3)]
    done = {str(x) for x in state["prompt_done"]}
    return [{"id": a, "question": b, "reply": c, "done": a in done} for a, b, c in picks]


def complete_prompt(path: Path, prompt_id: str) -> bool:
    state = load(path)
    prompts = {p["id"] for p in daily_prompts(path)}
    if prompt_id not in prompts or prompt_id in state["prompt_done"]:
        return False
    state["prompt_done"].append(prompt_id)
    save(path, state)
    return True
