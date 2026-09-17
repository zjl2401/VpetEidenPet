"""所属人羁绊：长线 XP / 阶段 / 共在与专注契约（与跨宠友情 peer_friendship 分离）。"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

# —— 渠道（点菜单收益低；共在 / 番茄 / 日程高）——
CH_MENU = "menu"
CH_SCENE_COEXIST = "scene_coexist"
CH_FOCUS_CONTRACT = "focus_contract"
CH_POMODORO = "pomodoro"
CH_SCHEDULE = "schedule"
CH_TODO = "todo"
CH_DIARY = "diary"

CHANNEL_BASE_XP: dict[str, float] = {
    CH_MENU: 0.4,
    CH_SCENE_COEXIST: 2.0,
    CH_FOCUS_CONTRACT: 4.0,
    CH_POMODORO: 2.5,
    CH_SCHEDULE: 2.0,
    CH_TODO: 1.0,
    CH_DIARY: 0.8,
}

DAILY_XP_CAP = 40.0
CHANNEL_DIMINISH_AFTER = 3  # 同渠道当日超过次数后衰减
CHANNEL_DIMINISH = 0.45

# 共在里程碑（秒）→ 额外倍率
COEXIST_MILESTONES_SEC: tuple[int, ...] = (15 * 60, 30 * 60, 60 * 60)

STAGE_DEFS: tuple[dict[str, Any], ...] = (
    {
        "stage": 0,
        "level": 1,
        "name": "相识",
        "title": "刚记下你的名字",
        "need": 0,
        "privileges": ("基础问候",),
        "next_focus": "一起待一会儿，或完成一轮番茄",
    },
    {
        "stage": 1,
        "level": 2,
        "name": "熟悉",
        "title": "开始记得你的节奏",
        "need": 30,
        "privileges": ("共在反应", "日程兑现奖励"),
        "next_focus": "多完成几轮专注契约",
    },
    {
        "stage": 2,
        "level": 3,
        "name": "默契",
        "title": "同屏也安心",
        "need": 90,
        "privileges": ("家园房间加速", "办公轻反馈"),
        "next_focus": "周末可以邀约小剧场",
    },
    {
        "stage": 3,
        "level": 4,
        "name": "信赖",
        "title": "愿意把今天交给你",
        "need": 180,
        "privileges": ("约会脚本解锁", "专属表情槽"),
        "next_focus": "继续写共同日记",
    },
    {
        "stage": 4,
        "level": 5,
        "name": "羁绊",
        "title": "忘不掉的所属人",
        "need": 300,
        "privileges": ("纪念称号", "多角色档案预留"),
        "next_focus": "一起过更长的日子",
    },
)

SCENE_LABELS: dict[str, str] = {
    "code": "写代码",
    "study": "学习",
    "office": "办公",
    "chat": "聊天",
    "game": "游戏",
    "video": "刷视频",
    "music": "听音乐",
    "idle": "发呆",
}


def _day_key(ts: float | None = None) -> str:
    import datetime as _dt

    return _dt.datetime.fromtimestamp(float(ts if ts is not None else time.time())).strftime("%Y-%m-%d")


def default_bond() -> dict[str, Any]:
    return {
        "points": 0.0,
        "daily_ymd": "",
        "daily_xp": 0.0,
        "channels_today": {},
        "coexist_scene": "",
        "coexist_started_ms": 0,
        "coexist_awarded": {},  # {ymd: {scene: [sec, ...]}}
        "focus_contract": {
            "active": False,
            "scene": "",
            "started_ms": 0,
            "away_ms": 0,
            "target_sec": 25 * 60,
        },
        "quiet_scene_mode": True,  # 新场景默认轻反应（不挡操作）
        "focus_nudge_enabled": False,
        "focus_nudge_ymd": "",
        "focus_nudge_count": 0,
        "last_grant_ms": 0,
        "milestones_noted": [],
    }


def load(path: Path) -> dict[str, Any]:
    base = default_bond()
    if not path.is_file():
        return base
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return base
    if not isinstance(raw, dict):
        return base
    out = default_bond()
    out["points"] = max(0.0, float(raw.get("points") or 0))
    out["daily_ymd"] = str(raw.get("daily_ymd") or "")
    out["daily_xp"] = max(0.0, float(raw.get("daily_xp") or 0))
    ch = raw.get("channels_today")
    out["channels_today"] = dict(ch) if isinstance(ch, dict) else {}
    out["coexist_scene"] = str(raw.get("coexist_scene") or "")
    out["coexist_started_ms"] = int(raw.get("coexist_started_ms") or 0)
    aw = raw.get("coexist_awarded")
    out["coexist_awarded"] = dict(aw) if isinstance(aw, dict) else {}
    fc = raw.get("focus_contract")
    if isinstance(fc, dict):
        out["focus_contract"].update(
            {
                "active": bool(fc.get("active")),
                "scene": str(fc.get("scene") or ""),
                "started_ms": int(fc.get("started_ms") or 0),
                "away_ms": int(fc.get("away_ms") or 0),
                "target_sec": max(5 * 60, int(fc.get("target_sec") or 25 * 60)),
            }
        )
    out["quiet_scene_mode"] = bool(raw.get("quiet_scene_mode", True))
    out["focus_nudge_enabled"] = bool(raw.get("focus_nudge_enabled", False))
    out["focus_nudge_ymd"] = str(raw.get("focus_nudge_ymd") or "")
    out["focus_nudge_count"] = max(0, int(raw.get("focus_nudge_count") or 0))
    out["last_grant_ms"] = int(raw.get("last_grant_ms") or 0)
    notes = raw.get("milestones_noted")
    out["milestones_noted"] = list(notes) if isinstance(notes, list) else []
    return _roll_daily(out)


def save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(data), ensure_ascii=False, indent=2), encoding="utf-8")


def _roll_daily(data: dict[str, Any], *, today: str | None = None) -> dict[str, Any]:
    day = today or _day_key()
    if str(data.get("daily_ymd") or "") != day:
        data["daily_ymd"] = day
        data["daily_xp"] = 0.0
        data["channels_today"] = {}
        data["focus_nudge_count"] = 0
        data["focus_nudge_ymd"] = day
    return data


def level_for_points(points: float) -> int:
    pts = max(0.0, float(points))
    level = 1
    for st in STAGE_DEFS:
        if pts >= float(st["need"]):
            level = int(st["level"])
    return level


def stage_def_for_level(level: int) -> dict[str, Any]:
    for st in STAGE_DEFS:
        if int(st["level"]) == int(level):
            return st
    return STAGE_DEFS[0]


def stats(data: dict[str, Any] | None) -> dict[str, Any]:
    d = data or default_bond()
    pts = max(0.0, float(d.get("points") or 0))
    level = level_for_points(pts)
    cur = stage_def_for_level(level)
    nxt = None
    for st in STAGE_DEFS:
        if int(st["level"]) == level + 1:
            nxt = st
            break
    if nxt:
        need = float(nxt["need"]) - float(cur["need"])
        cur_bar = pts - float(cur["need"])
        pct = int(max(0, min(100, cur_bar * 100 / max(1.0, need))))
        next_need = max(0.0, float(nxt["need"]) - pts)
    else:
        need = 1.0
        cur_bar = need
        pct = 100
        next_need = 0.0
    daily = _roll_daily(dict(d))
    return {
        "points": pts,
        "level": level,
        "stage": int(cur["stage"]),
        "stage_name": str(cur["name"]),
        "stage_title": str(cur["title"]),
        "privileges": list(cur.get("privileges") or []),
        "next_focus": str(cur.get("next_focus") or ""),
        "bar_pct": pct,
        "bar_cur": round(cur_bar, 1),
        "bar_need": round(need, 1),
        "next_need": round(next_need, 1),
        "daily_xp": float(daily.get("daily_xp") or 0),
        "daily_left": max(0.0, DAILY_XP_CAP - float(daily.get("daily_xp") or 0)),
        "daily_capped": float(daily.get("daily_xp") or 0) >= DAILY_XP_CAP - 1e-6,
    }


def privilege_unlocked(level: int, key: str) -> bool:
    """粗粒度特权：按等级门槛。"""
    gates = {
        "scene_react": 1,
        "schedule_reward": 2,
        "room_boost": 3,
        "office_feedback": 3,
        "date_script": 4,
        "bond_title": 5,
    }
    return int(level) >= int(gates.get(key, 99))


def room_bonus_from_bond(level: int) -> int:
    """羁绊等级额外房间数（与相伴天数取 max）。"""
    if level >= 5:
        return 2
    if level >= 3:
        return 1
    return 0


def apply_xp(
    data: dict[str, Any],
    amount: float,
    *,
    channel: str = CH_MENU,
) -> tuple[float, dict[str, Any]]:
    """返回 (实际获得, meta)。"""
    data = _roll_daily(data)
    meta: dict[str, Any] = {"channel": channel, "diminished": False, "capped": False}
    left = DAILY_XP_CAP - float(data.get("daily_xp") or 0)
    if left <= 0:
        meta["capped"] = True
        return 0.0, meta
    ch_map = data.setdefault("channels_today", {})
    count = int(ch_map.get(channel, 0) or 0)
    gain = max(0.0, float(amount))
    if count >= CHANNEL_DIMINISH_AFTER:
        gain *= CHANNEL_DIMINISH
        meta["diminished"] = True
    gain = min(gain, left)
    if gain <= 0:
        meta["capped"] = True
        return 0.0, meta
    data["points"] = float(data.get("points") or 0) + gain
    data["daily_xp"] = float(data.get("daily_xp") or 0) + gain
    ch_map[channel] = count + 1
    data["last_grant_ms"] = int(time.time() * 1000)
    before_lv = level_for_points(float(data["points"]) - gain)
    after_lv = level_for_points(float(data["points"]))
    meta["leveled_up"] = after_lv > before_lv
    meta["level"] = after_lv
    if meta["leveled_up"]:
        note = f"stage_{after_lv}"
        notes = data.setdefault("milestones_noted", [])
        if note not in notes:
            notes.append(note)
    return gain, meta


def grant(
    path: Path,
    amount: float | None = None,
    *,
    channel: str = CH_MENU,
) -> dict[str, Any]:
    data = load(path)
    base = CHANNEL_BASE_XP.get(channel, 1.0) if amount is None else float(amount)
    before = stats(data)
    gained, meta = apply_xp(data, base, channel=channel)
    save(path, data)
    after = stats(data)
    tip = ""
    if meta.get("capped") and gained <= 0:
        tip = "今日羁绊进度已达上限"
    elif meta.get("diminished"):
        tip = "同类互动收益在下降，换种方式更开心"
    elif meta.get("leveled_up"):
        tip = f"羁绊升至「{after.get('stage_name')}」！"
    return {
        **after,
        "gained": gained,
        "xp_meta": meta,
        "leveled_up": bool(meta.get("leveled_up")),
        "tip": tip,
        "before_level": before.get("level"),
    }


def tick_coexist(
    data: dict[str, Any],
    scene: str,
    *,
    now_ms: int | None = None,
) -> tuple[dict[str, Any], list[int]]:
    """更新共在计时；返回 (data, 新达成的里程碑秒列表)。"""
    now = int(now_ms if now_ms is not None else time.time() * 1000)
    data = _roll_daily(data)
    scene = str(scene or "").strip()
    awarded_new: list[int] = []
    if not scene or scene in ("none", "hold", "idle"):
        data["coexist_scene"] = ""
        data["coexist_started_ms"] = 0
        return data, awarded_new
    if str(data.get("coexist_scene") or "") != scene:
        data["coexist_scene"] = scene
        data["coexist_started_ms"] = now
        return data, awarded_new
    started = int(data.get("coexist_started_ms") or 0)
    if started <= 0:
        data["coexist_started_ms"] = now
        return data, awarded_new
    elapsed = max(0, (now - started) // 1000)
    day = str(data.get("daily_ymd") or _day_key())
    bag = data.setdefault("coexist_awarded", {})
    day_bag = bag.setdefault(day, {})
    if not isinstance(day_bag, dict):
        day_bag = {}
        bag[day] = day_bag
    done = day_bag.setdefault(scene, [])
    if not isinstance(done, list):
        done = []
        day_bag[scene] = done
    for ms in COEXIST_MILESTONES_SEC:
        if elapsed >= ms and ms not in done:
            done.append(ms)
            awarded_new.append(ms)
    return data, awarded_new


def start_focus_contract(
    data: dict[str, Any],
    scene: str,
    *,
    target_sec: int = 25 * 60,
    now_ms: int | None = None,
) -> dict[str, Any]:
    now = int(now_ms if now_ms is not None else time.time() * 1000)
    data["focus_contract"] = {
        "active": True,
        "scene": str(scene or "office"),
        "started_ms": now,
        "away_ms": 0,
        "target_sec": max(5 * 60, int(target_sec)),
    }
    return data


def cancel_focus_contract(data: dict[str, Any]) -> dict[str, Any]:
    fc = data.setdefault("focus_contract", default_bond()["focus_contract"])
    fc["active"] = False
    return data


def update_focus_contract(
    data: dict[str, Any],
    current_scene: str,
    *,
    now_ms: int | None = None,
    away_grace_ms: int = 90_000,
) -> tuple[dict[str, Any], str]:
    """
    返回 (data, event)
    event: "" | "remind" | "complete" | "fail"
    """
    fc = data.get("focus_contract")
    if not isinstance(fc, dict) or not fc.get("active"):
        return data, ""
    now = int(now_ms if now_ms is not None else time.time() * 1000)
    target = str(fc.get("scene") or "")
    started = int(fc.get("started_ms") or 0)
    if started <= 0:
        fc["active"] = False
        return data, "fail"
    elapsed = (now - started) / 1000.0
    if current_scene == target or current_scene == "hold":
        fc["away_ms"] = 0
        if elapsed >= float(fc.get("target_sec") or 25 * 60):
            fc["active"] = False
            return data, "complete"
        return data, ""
    away = int(fc.get("away_ms") or 0)
    if away <= 0:
        fc["away_ms"] = now
        return data, "remind"
    if now - away >= away_grace_ms:
        fc["active"] = False
        return data, "fail"
    return data, "remind"


def can_focus_nudge(data: dict[str, Any], *, daily_max: int = 2) -> bool:
    if not data.get("focus_nudge_enabled"):
        return False
    data = _roll_daily(data)
    return int(data.get("focus_nudge_count") or 0) < daily_max


def note_focus_nudge(data: dict[str, Any]) -> dict[str, Any]:
    data = _roll_daily(data)
    data["focus_nudge_count"] = int(data.get("focus_nudge_count") or 0) + 1
    return data


def diary_line_for_coexist(scene: str, minutes: int) -> str:
    label = SCENE_LABELS.get(scene, scene or "电脑")
    return f"今天一起{label}了大约 {max(1, int(minutes))} 分钟。"


def summary_line(data: dict[str, Any] | None) -> str:
    st = stats(data)
    return (
        f"羁绊「{st['stage_name']}」Lv{st['level']} · "
        f"今日 {st['daily_xp']:.0f}/{DAILY_XP_CAP:.0f}"
    )
