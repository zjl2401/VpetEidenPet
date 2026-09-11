"""苍叶 ↔ 伊得 跨桌宠友情：相遇计数、好感等级、联动台词、解锁动作。"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

KIND_AOBA = "aoba"
KIND_EIDEN = "eiden"

PET_DISPLAY: dict[str, str] = {
    KIND_AOBA: "苍叶",
    KIND_EIDEN: "伊得",
}

MINIPET_DISPLAY: dict[str, str] = {
    "rei": "莲",
    "allmate": "莲",
    "aster": "艾斯特",
    "morvay": "墨菲",
}

ACTION_STROLL_TOGETHER = "stroll_together"
ACTION_SIDE_MEET = "side_meet"  # 话/动：先并排站定；动再进入 act_ready 选具体动作

ACTION_BY_LEVEL: dict[int, str] = {
    1: ACTION_STROLL_TOGETHER,
}

ACTION_LABELS: dict[str, str] = {
    ACTION_STROLL_TOGETHER: "并肩散步（15秒）",
}

# 已实装动作的最高友情等级；更高档位面板/升级先锁（加新动作时扩 ACTION_BY_LEVEL 即可）
MAX_IMPLEMENTED_LEVEL = max(ACTION_BY_LEVEL.keys()) if ACTION_BY_LEVEL else 1

# 动：并排到位后短站定，再出动作热区
SIDE_STAND_HOLD_MS = 480
SIDE_DIALOG_GAP_MS = 450
SIDE_TALK_REPLY_TIMEOUT_MS = 4000  # 对端不接话时本机代说第二句

SESSION_FILE = "crossover_session.json"
DIALOGUES_FILE = "crossover_dialogues.json"

STROLL_DURATION_MS = 15_000
STROLL_APPROACH_MAX_MS = 4500
STROLL_STEP_MS = 160
STROLL_CHAT_INTERVAL_MS = 2600
# 跨宠接话：等对方气泡预计收起后再开口（进程间看不到对方 Tk 窗）
SPEECH_TURN_GAP_MS = 380
SPEECH_MS_PER_CHAR = 48
SPEECH_TYPE_MIN_MS = 400
SPEECH_TYPE_MAX_MS = 2400
# 「话」第二句：等对端说完的最长时间；超时本机也要接上，避免对话断掉
DIALOGUE_PEER_WAIT_MAX_MS = 3600
DIALOGUE_INITIATOR_FALLBACK_MS = 4200

PAIR_KEY = "aoba_eiden"

PHASE_SILENT = "silent"  # 兼容旧引用；meet_phase 不再返回此阶段
PHASE_FAMILIAR = "familiar"
PHASE_INTRO = "intro"
PHASE_FREE = "free"


def meet_phase(meet_count: int) -> str:
    """相遇阶段：1–10 眼熟 · 11 自我介绍 · 12+ 自由（已去掉静默期）。"""
    n = max(0, int(meet_count))
    if n <= 0:
        return PHASE_FAMILIAR
    if n <= 10:
        return PHASE_FAMILIAR
    if n == 11:
        return PHASE_INTRO
    return PHASE_FREE


def meet_phase_label(meet_count: int) -> str:
    phase = meet_phase(meet_count)
    return {
        PHASE_SILENT: "有点眼熟",
        PHASE_FAMILIAR: "有点眼熟",
        PHASE_INTRO: "正式相识",
        PHASE_FREE: "老朋友",
    }.get(phase, "相遇中")


def points_gain_for_meet(meet_count_after: int) -> float:
    n = max(1, int(meet_count_after))
    if n <= 10:
        return 0.4
    return 1.0


# 每级进度条所需点数（逐级变难）
def points_for_bar(level: int) -> int:
    lv = max(1, int(level))
    return 4 + (lv - 1) * 3 + max(0, lv - 2) * (lv - 2)


def cumulative_before(level: int) -> float:
    return float(sum(points_for_bar(i) for i in range(1, max(1, int(level)))))


def max_points_at_cap() -> float:
    """锁在已实装最高级时：进度条满格，但不跨入下一级。"""
    lv = max(1, int(MAX_IMPLEMENTED_LEVEL))
    return float(cumulative_before(lv) + points_for_bar(lv))


def clamp_points(points: float) -> float:
    return max(0.0, min(float(points), max_points_at_cap()))


def stats(points: float) -> dict:
    pts = clamp_points(points)
    level = 1
    while pts >= cumulative_before(level) + points_for_bar(level):
        level += 1
        if level >= MAX_IMPLEMENTED_LEVEL:
            # 满级：进度顶格，不再升到未实装档
            level = MAX_IMPLEMENTED_LEVEL
            base = cumulative_before(level)
            need = points_for_bar(level)
            cur = min(float(need), max(0.0, pts - base))
            pct = min(100, int(cur * 100 / max(1, need)))
            return {
                "level": level,
                "points": pts,
                "bar_pct": pct,
                "bar_cur": cur,
                "bar_need": need,
                "level_capped": True,
                "max_implemented_level": MAX_IMPLEMENTED_LEVEL,
            }
    base = cumulative_before(level)
    need = points_for_bar(level)
    cur = pts - base
    pct = min(100, int(cur * 100 / max(1, need)))
    return {
        "level": level,
        "points": pts,
        "bar_pct": pct,
        "bar_cur": cur,
        "bar_need": need,
        "level_capped": level >= MAX_IMPLEMENTED_LEVEL and cur >= need - 1e-6,
        "max_implemented_level": MAX_IMPLEMENTED_LEVEL,
    }


def _path(presence_dir: Path) -> Path:
    return presence_dir / "crossover_friendship.json"


def load(presence_dir: Path) -> dict:
    path = _path(presence_dir)
    empty = {
        "pair": PAIR_KEY,
        "points": 0.0,
        "meet_count": 0,
        "last_meet_ms": 0,
        "familiar_os_used": {},
        "shared_facts": [],
        "last_talk_mode": "",
    }
    if not path.is_file():
        return dict(empty)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            used = raw.get("familiar_os_used") or {}
            if not isinstance(used, dict):
                used = {}
            facts = raw.get("shared_facts") or []
            if not isinstance(facts, list):
                facts = []
            return {
                "pair": PAIR_KEY,
                "points": float(raw.get("points") or 0),
                "meet_count": int(raw.get("meet_count") or 0),
                "last_meet_ms": int(raw.get("last_meet_ms") or 0),
                "familiar_os_used": {str(k): list(v) if isinstance(v, list) else [] for k, v in used.items()},
                "shared_facts": [str(x) for x in facts if str(x).strip()],
                "last_talk_mode": str(raw.get("last_talk_mode") or ""),
            }
    except Exception:
        pass
    return dict(empty)


def save(presence_dir: Path, data: dict) -> None:
    try:
        presence_dir.mkdir(parents=True, exist_ok=True)
        used = data.get("familiar_os_used") or {}
        if not isinstance(used, dict):
            used = {}
        facts = data.get("shared_facts") or []
        if not isinstance(facts, list):
            facts = []
        payload = {
            "pair": PAIR_KEY,
            "points": clamp_points(float(data.get("points") or 0)),
            "meet_count": int(data.get("meet_count") or 0),
            "last_meet_ms": int(data.get("last_meet_ms") or 0),
            "familiar_os_used": {str(k): [str(x) for x in (v or [])] for k, v in used.items()},
            "shared_facts": [str(x) for x in facts if str(x).strip()],
            "last_talk_mode": str(data.get("last_talk_mode") or ""),
        }
        _path(presence_dir).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def record_meet(
    presence_dir: Path,
    *,
    writer_id: str,
    peer_id: str,
    now_ms: int,
    force: bool = False,
) -> dict:
    """记录一次有效相遇。

    自动擦肩时两边几乎同时调用：非 force 时仅 id 较小的一侧写盘，避免双计。
    两步「遇」配对 / 手动「话」只有完成方调用一次，须 force=True，否则
    eiden_* > aoba_* 时伊得点第二下永远不涨相遇次数。
    """
    data = load(presence_dir)
    if (
        not force
        and writer_id
        and peer_id
        and writer_id > peer_id
    ):
        return {
            **data,
            **stats(float(data.get("points") or 0)),
            "phase": meet_phase(int(data.get("meet_count") or 0)),
        }
    data["meet_count"] = int(data.get("meet_count") or 0) + 1
    gain = points_gain_for_meet(int(data["meet_count"]))
    data["points"] = clamp_points(float(data.get("points") or 0) + gain)
    data["last_meet_ms"] = int(now_ms)
    save(presence_dir, data)
    phase = meet_phase(int(data["meet_count"]))
    return {**data, **stats(float(data["points"])), "phase": phase}


def unlocked_actions(level: int) -> list[str]:
    lv = max(0, int(level))
    return [act for req, act in sorted(ACTION_BY_LEVEL.items()) if lv >= req]


def action_label(action: str) -> str:
    return ACTION_LABELS.get(action, action)


def session_path(presence_dir: Path) -> Path:
    return presence_dir / SESSION_FILE


SESSION_STALE_MS = 180_000  # 并排/对话会话超时；过期清掉以免挡住「遇」热区


def load_session(presence_dir: Path) -> dict | None:
    path = session_path(presence_dir)
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return None
        # 无 flow 的动作会话：靠 started_ms / stand_until 判断过期
        flow = str(raw.get("flow") or "").strip().lower()
        if flow not in ("picking", "linked"):
            now = int(time.time() * 1000)
            started = int(raw.get("started_ms") or raw.get("ts") or 0)
            stand_until = int(raw.get("stand_until_ms") or 0)
            stroll_until = int(raw.get("stroll_until_ms") or 0)
            speak_until = int(raw.get("speaking_until_ms") or raw.get("speaker_until_ms") or 0)
            anchor = max(started, stand_until, stroll_until, speak_until)
            if anchor > 0 and (now - anchor) > SESSION_STALE_MS:
                try:
                    path.unlink()
                except Exception:
                    pass
                return None
        return raw
    except Exception:
        return None


def save_session(presence_dir: Path, data: dict) -> None:
    try:
        presence_dir.mkdir(parents=True, exist_ok=True)
        session_path(presence_dir).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def clear_session(presence_dir: Path) -> None:
    try:
        path = session_path(presence_dir)
        if path.is_file():
            path.unlink()
    except Exception:
        pass


# 手动相遇 UI 流程：
# idle → 靠近显示「相遇」像素图标 → 两边各点一次完成配对
# → 1s 后双方弹动（2–10 次另加眼熟内心 OS）
# → 第 11 次起 linked 显示「对话」图标；等级够时再显「互动」图标
# 对话/互动均先走到中间并排，再对话 / 触发动作
# 仅两边点「相遇」完成的配对计入有效相遇；自动擦肩等不计。
FLOW_PICKING = "picking"
FLOW_LINKED = "linked"
FLOW_STALE_MS = 90_000

# 热区模式键（UI 用像素图案，不再画汉字）
ICON_MEET = "meet"
ICON_TALK = "talk"
ICON_ACT = "act"
# 兼容旧引用
GLYPH_MEET_START = ICON_MEET
GLYPH_MEET_JOIN = ICON_MEET
GLYPH_TALK = ICON_TALK
GLYPH_ACT = ICON_ACT

ACTION_PAIR_DIALOGUE = "pair_dialogue"
MEET_REACTION_DELAY_MS = 1000


def can_show_talk(meet_count: int) -> bool:
    """第 11 次有效相遇后才出现「话」。"""
    return int(meet_count or 0) >= 11


def can_show_action(level: int, meet_count: int) -> bool:
    """亲密动作「动」：自我介绍完成后解锁。"""
    return actions_available(level, meet_count)


def _flow_fresh(raw: dict | None) -> dict | None:
    if not isinstance(raw, dict):
        return None
    flow = str(raw.get("flow") or "").strip().lower()
    if flow not in (FLOW_PICKING, FLOW_LINKED):
        return None
    ts = int(raw.get("ts") or 0)
    if ts <= 0 or (int(time.time() * 1000) - ts) > FLOW_STALE_MS:
        return None
    return raw


def get_flow(presence_dir: Path) -> dict | None:
    return _flow_fresh(load_session(presence_dir))


def begin_pick(
    presence_dir: Path,
    *,
    picker_id: str,
    picker_kind: str,
    x: int,
    y: int,
    size: int,
) -> None:
    now = int(time.time() * 1000)
    save_session(
        presence_dir,
        {
            "flow": FLOW_PICKING,
            "picker_id": str(picker_id),
            "picker_kind": str(picker_kind or "").strip().lower(),
            "picker_x": int(x),
            "picker_y": int(y),
            "picker_size": int(size),
            "ts": now,
        },
    )


def complete_link(
    presence_dir: Path,
    *,
    picker_id: str,
    peer_id: str,
    link_token: str,
    meet_count: int,
) -> None:
    now = int(time.time() * 1000)
    save_session(
        presence_dir,
        {
            "flow": FLOW_LINKED,
            "picker_id": str(picker_id),
            "peer_id": str(peer_id),
            "link_token": str(link_token),
            "meet_count": int(meet_count),
            "ts": now,
        },
    )


def merge_session(presence_dir: Path, **fields) -> dict:
    """在现有 session 上合并字段（保留 flow / linked 信息）。"""
    cur = load_session(presence_dir) or {}
    updated = dict(cur)
    updated.update(fields)
    updated["ts"] = int(time.time() * 1000)
    save_session(presence_dir, updated)
    return updated


def dialogue_lines_for_pair(
    initiator_kind: str,
    other_kind: str,
    *,
    meet_count: int,
) -> tuple[str, str]:
    """发起方一句 + 另一方回一句。"""
    n = int(meet_count or 0)
    if n <= 11:
        a_lines = intro_script(initiator_kind, other_kind)
        b_lines = intro_script(other_kind, initiator_kind)
        return (a_lines[0], b_lines[0])
    a = build_greeting(initiator_kind, other_kind)
    # 回句取对方视角的交流短句
    b = build_exchange(other_kind, initiator_kind)
    # build_greeting 可能多行，对话只用首行
    a0 = str(a).split("\n", 1)[0].strip() or "……"
    b0 = str(b).split("\n", 1)[0].strip() or "……"
    return (a0, b0)


def clear_flow(presence_dir: Path) -> None:
    clear_session(presence_dir)


# 兼容旧调用名
UI_MODE_MEET = "meet"
UI_MODE_TALK = "talk"
UI_MODE_STALE_MS = FLOW_STALE_MS


def get_ui_mode(presence_dir: Path) -> str | None:
    """旧接口：picking 视作 meet；linked 不返回 mode。"""
    flow = get_flow(presence_dir)
    if not flow:
        return None
    if str(flow.get("flow")) == FLOW_PICKING:
        return UI_MODE_MEET
    return None


def set_ui_mode(presence_dir: Path, mode: str) -> None:
    # 旧接口废弃：改走 begin_pick / complete_link
    _ = (presence_dir, mode)


def clear_ui_mode(presence_dir: Path) -> None:
    clear_flow(presence_dir)


def compute_stroll_layout(
    ax: int,
    ay: int,
    asz: int,
    bx: int,
    by: int,
    bsz: int,
    *,
    gap: int = 8,
) -> dict:
    """两桌宠朝中间靠拢后左右并排的目标位。"""
    acx = int(ax) + int(asz) // 2
    bcx = int(bx) + int(bsz) // 2
    acy = int(ay) + int(asz) // 2
    bcy = int(by) + int(bsz) // 2
    mid_x = (acx + bcx) // 2
    mid_y = (acy + bcy) // 2
    slot_y = mid_y - max(int(asz), int(bsz)) // 2
    size = max(int(asz), int(bsz))
    half_gap = max(4, int(gap)) // 2
    if acx <= bcx:
        left_x = mid_x - half_gap - size
        right_x = mid_x + half_gap
        a_is_left = True
    else:
        left_x = mid_x - half_gap - size
        right_x = mid_x + half_gap
        a_is_left = False
    return {
        "mid_x": mid_x,
        "mid_y": mid_y,
        "slot_y": slot_y,
        "left_x": left_x,
        "right_x": right_x,
        "slot_size": size,
        "a_is_left": a_is_left,
    }


def pick_stroll_direction(left_x: int, right_x: int, slot_y: int, screen_w: int, size: int) -> str:
    room_l = max(0, left_x)
    room_r = max(0, screen_w - (right_x + size))
    return "right" if room_r >= room_l else "left"


def estimate_speech_ms(
    text: str,
    *,
    auto_hide_ms: int | None = None,
    instant: bool = False,
) -> int:
    """估算一句台词占屏时长（打字 + 停留），供对端接话对齐。"""
    n = max(1, len(str(text or "").strip()))
    type_ms = 0 if instant else min(SPEECH_TYPE_MAX_MS, max(SPEECH_TYPE_MIN_MS, n * SPEECH_MS_PER_CHAR))
    hide = max(900, int(auto_hide_ms if auto_hide_ms is not None else 2400))
    return int(type_ms + hide + 160)


def speech_still_active(until_ms: int, *, now_ms: int | None = None) -> bool:
    now = int(now_ms if now_ms is not None else time.time() * 1000)
    return int(until_ms or 0) > now


def garbled_chat_line(*, length: int | None = None) -> str:
    moji = "啊嗯哦唔嘿呀嘛呢吧啦噗嘻呜哇呐哟"
    garb = "▓░▒■□●◆"
    n = max(4, int(length or random.randint(6, 14)))
    parts: list[str] = []
    for _ in range(n):
        if random.random() < 0.22:
            parts.append(random.choice(garb))
        else:
            parts.append(random.choice(moji))
    if random.random() < 0.45:
        parts.append("~" * random.randint(1, 3))
    return "".join(parts)


def dialogues_path(presence_dir: Path, data_dir: Path | None = None) -> Path | None:
    for base in (presence_dir, data_dir):
        if base is None:
            continue
        path = base / DIALOGUES_FILE
        if path.is_file():
            return path
    return None


def load_custom_dialogues(presence_dir: Path, data_dir: Path | None = None) -> dict[str, list[dict]]:
    """自定义相遇台词。支持纯字符串，或 {text, keyword, bubble, cells}。

    bubble: \"text\" | \"pixels\" —— 气泡里是文字还是像素画；
    keyword: 可选，可作为 AI 对话围绕展开的关键词；
    cells: 可选，12×12 色板下标（0=透明），bubble=pixels 时绘制。
    """
    path = dialogues_path(presence_dir, data_dir)
    if not path:
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {}
        out: dict[str, list[dict]] = {}
        for key, val in raw.items():
            kind = str(key or "").strip().lower()
            if not kind:
                continue
            items = val if isinstance(val, list) else ([val] if val else [])
            entries: list[dict] = []
            for item in items:
                entry = normalize_dialogue_entry(item)
                if entry is not None:
                    entries.append(entry)
            if entries:
                out[kind] = entries
        return out
    except Exception:
        return {}


def normalize_dialogue_entry(raw) -> dict | None:
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        return {"text": text, "keyword": "", "bubble": "text", "cells": []}
    if not isinstance(raw, dict):
        return None
    text = str(raw.get("text") or raw.get("line") or "").strip()
    if not text:
        return None
    bubble = str(raw.get("bubble") or "text").strip().lower()
    if bubble not in ("text", "pixels"):
        bubble = "text"
    keyword = str(raw.get("keyword") or raw.get("topic") or "").strip()
    cells_raw = raw.get("cells")
    cells: list[int] = []
    if isinstance(cells_raw, list):
        for v in cells_raw[:144]:
            try:
                cells.append(max(0, min(15, int(v or 0))))
            except Exception:
                cells.append(0)
        while len(cells) < 144:
            cells.append(0)
    return {"text": text, "keyword": keyword, "bubble": bubble, "cells": cells}


def pick_custom_entry(self_kind: str, dialogues: dict[str, list[dict]] | None) -> dict | None:
    pool = (dialogues or {}).get(self_kind) or []
    if not pool:
        return None
    return dict(random.choice(pool))


def build_custom_talk(
    self_kind: str,
    other_kind: str,
    dialogues: dict[str, list[dict]] | None,
    *,
    owner_name: str = "",
) -> str | None:
    entry = pick_custom_entry(self_kind, dialogues)
    if entry is None:
        return None
    line = str(entry.get("text") or "")
    other = PET_DISPLAY.get(other_kind, other_kind)
    owner = str(owner_name or "").strip()
    try:
        return line.format(other=other, owner=owner, self=PET_DISPLAY.get(self_kind, self_kind))
    except Exception:
        return line


def build_custom_entry_talk(
    entry: dict,
    self_kind: str,
    other_kind: str,
    *,
    owner_name: str = "",
) -> str:
    line = str(entry.get("text") or "")
    other = PET_DISPLAY.get(other_kind, other_kind)
    owner = str(owner_name or "").strip()
    try:
        return line.format(other=other, owner=owner, self=PET_DISPLAY.get(self_kind, self_kind))
    except Exception:
        return line


def actions_available(level: int, meet_count: int) -> bool:
    # 加长 P0 后：自我介绍完成（≥11）且 Lv≥1 才解锁并肩
    return int(meet_count) >= 11 and int(level) >= 1


def next_unlock_hint(level: int) -> str | None:
    nxt = int(level) + 1
    if nxt > MAX_IMPLEMENTED_LEVEL:
        return "后续等级暂未开放"
    act = ACTION_BY_LEVEL.get(nxt)
    if not act:
        return "后续等级暂未开放"
    return action_label(act)


def minipet_names(kinds: list[str], *, limit: int = 2) -> str:
    names: list[str] = []
    for key in kinds[:limit]:
        label = MINIPET_DISPLAY.get(key, key)
        if label not in names:
            names.append(label)
    return "、".join(names)


def normalize_companions(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        key = str(item or "").strip().lower()
        if key and key not in out:
            out.append(key)
    return out


def minipet_line(self_kind: str, self_companions: list[str], other_companions: list[str]) -> str | None:
    if not self_companions and not other_companions:
        return None
    self_name = PET_DISPLAY.get(self_kind, self_kind)
    parts: list[str] = []
    other_label = minipet_names(other_companions)
    self_label = minipet_names(self_companions)
    if other_companions:
        parts.append(f"{self_name}向{other_label}挥挥手")
        if self_kind == KIND_AOBA and "rei" in other_companions:
            parts.append("莲也在那边呢，打个招呼吧~")
    if self_companions:
        if other_companions:
            parts.extend(
                (
                    f"{self_label}：嗨，{other_label}~",
                    f"迷你宠 {self_label} 和 {other_label} 碰面了。",
                    f"{self_label}小声说：你好呀，{other_label}。",
                )
            )
        else:
            parts.append(f"{self_label}也在呢")
    if not parts:
        return None
    return random.choice(parts)


def familiar_lines(self_kind: str, other_kind: str) -> tuple[str, ...]:
    """眼熟阶段：极短（≤12 字），见面 UI 轻量化。"""
    other = PET_DISPLAY.get(other_kind, other_kind)
    if self_kind == KIND_EIDEN:
        return (
            f"……是{other}？",
            "有点眼熟……",
            "好像见过……",
            f"诶，{other}？",
            "这感觉……",
            "桌面又撞见。",
            "嗯，是你吧。",
            "心跳漏半拍。",
            "又碰面了。",
            "记得这气息。",
            "别擦肩啊。",
            "轻轻点头。",
        )
    return (
        f"……{other}？",
        "有点印象……",
        "擦肩过？",
        f"嗯……{other}？",
        "好像见过。",
        "印象里有你。",
        "又遇见了。",
        "轻轻挥一下。",
    )


def _os_key(line: str) -> str:
    return str(line or "").strip()


def build_familiar(self_kind: str, other_kind: str, presence_dir: Path | None = None) -> str:
    """2–10 次眼熟 OS；传入 presence_dir 时按角色去重，用尽后重置。"""
    lines = familiar_lines(self_kind, other_kind)
    if presence_dir is None:
        return random.choice(lines)
    data = load(presence_dir)
    used_map = dict(data.get("familiar_os_used") or {})
    used = [str(x) for x in (used_map.get(self_kind) or [])]
    used_set = set(used)
    pool = [ln for ln in lines if _os_key(ln) not in used_set]
    if not pool:
        used = []
        used_set.clear()
        pool = list(lines)
    choice = random.choice(pool)
    used.append(_os_key(choice))
    used_map[self_kind] = used
    data["familiar_os_used"] = used_map
    save(presence_dir, data)
    return choice


# —— 12+ 交流：普通对话知识点（告诉 / 你还记得吗）——
TELL_PREFIXES: tuple[str, ...] = (
    "我想告诉你——",
    "你知道吗？",
    "悄悄跟你说：",
    "跟你讲一件事：",
)
REMEMBER_ACK: tuple[str, ...] = (
    "嗯，我记住了。",
    "好，记下了。",
    "知道了，谢谢你告诉我。",
    "收到，我会记得的。",
)
QUIZ_PREFIXES: tuple[str, ...] = (
    "你还记得吗？",
    "考你一下——你还记得吗？",
    "上次跟你说过，你还记得吗？",
)

# 来自普通对话设定；simple=True 适合所属人填空
KNOWLEDGE_FACTS: tuple[dict, ...] = (
    {
        "id": "name",
        "topic": "名字",
        "fact": "我叫伊得，本名 Eiden",
        "ask": "我叫什么名字？",
        "answers": ("伊得", "eiden", "Eiden", "EIDEN"),
        "simple": True,
    },
    {
        "id": "age",
        "topic": "年龄",
        "fact": "我今年二十三岁",
        "ask": "我多大了？",
        "answers": ("23", "二十三", "23岁", "二十三岁", "廿三"),
        "simple": True,
    },
    {
        "id": "birthday",
        "topic": "生日",
        "fact": "我的生日是 6 月 17 日",
        "ask": "我的生日是哪天？",
        "answers": ("6月17", "6月17日", "六月十七", "6/17", "06/17", "6-17", "617"),
        "simple": True,
    },
    {
        "id": "height",
        "topic": "身高",
        "fact": "我身高 176cm",
        "ask": "我多高？",
        "answers": ("176", "176cm", "一七六", "一百七十六", "176厘米"),
        "simple": True,
    },
    {
        "id": "looks",
        "topic": "发色瞳色",
        "fact": "我是褐发，瞳色偏褐黄",
        "ask": "我的头发和眼睛是什么颜色？",
        "answers": ("褐发", "褐黄", "褐色", "褐发褐黄", "棕色", "棕发"),
        "simple": True,
    },
    {
        "id": "cv",
        "topic": "声优",
        "fact": "我的配音是刺草ネトル",
        "ask": "我的声优是谁？",
        "answers": ("刺草ネトル", "刺草", "ネトル"),
        "simple": True,
    },
    {
        "id": "origin",
        "topic": "出身",
        "fact": "我出身现代世界，以前经常搬家",
        "ask": "我从哪里来？",
        "answers": ("现代世界", "现代", "异世界也待过", "卡莱因"),
        "simple": False,
    },
    {
        "id": "alias",
        "topic": "别号",
        "fact": "有人叫我「卡莱因之星」",
        "ask": "我的别号是什么？",
        "answers": ("卡莱因之星", "卡莱因"),
        "simple": True,
    },
    {
        "id": "mage",
        "topic": "大魔法师",
        "fact": "虽有「大魔法师」名号，我本质上也会害怕、也会怯懦",
        "ask": "大魔法师对我来说意味着什么？",
        "answers": ("普通人", "会害怕", "怯懦", "名号", "身份"),
        "simple": False,
    },
    {
        "id": "job",
        "topic": "以前的工作",
        "fact": "在现代世界时，我是经常搬家、每天工作超过十二小时的社畜",
        "ask": "我以前的工作是怎样的？",
        "answers": ("社畜", "加班", "十二小时", "12小时", "搬家"),
        "simple": False,
    },
    {
        "id": "childhood",
        "topic": "童年",
        "fact": "我在孤儿院长大，童年并不幸福，那时候缺少稳定的安全感",
        "ask": "我的童年是怎样的？",
        "answers": ("孤儿院", "缺少安全感", "不幸福", "安全感"),
        "simple": False,
    },
)


def knowledge_by_id(fact_id: str) -> dict | None:
    fid = str(fact_id or "").strip()
    for fact in KNOWLEDGE_FACTS:
        if str(fact.get("id") or "") == fid:
            return dict(fact)
    return None


def normalize_quiz_answer(text: str) -> str:
    t = str(text or "").strip().lower()
    for ch in (" ", "　", "。", "？", "?", "！", "!", "的", "是", "呢", "啊", "呀"):
        t = t.replace(ch, "")
    return t


def quiz_answer_correct(fact: dict, user_text: str) -> bool:
    raw = str(user_text or "").strip()
    if not raw:
        return False
    norm = normalize_quiz_answer(raw)
    for ans in fact.get("answers") or ():
        a = normalize_quiz_answer(str(ans))
        if not a:
            continue
        if norm == a or a in norm or norm in a:
            return True
    return False


def bump_friendship_level(presence_dir: Path, delta: int) -> dict:
    """答对 +1 级 / 答错 -1 级（不低于 1）；落在目标等级进度条约 15% 处。
    高于已实装动作档位时锁在最高级满格，不再升虚级。"""
    data = load(presence_dir)
    st = stats(float(data.get("points") or 0))
    new_lv = max(1, int(st.get("level") or 1) + int(delta))
    if new_lv > MAX_IMPLEMENTED_LEVEL:
        new_lv = MAX_IMPLEMENTED_LEVEL
        data["points"] = max_points_at_cap()
    else:
        data["points"] = clamp_points(
            float(cumulative_before(new_lv) + points_for_bar(new_lv) * 0.15)
        )
    save(presence_dir, data)
    return {**data, **stats(float(data["points"]))}


def remember_shared_fact(presence_dir: Path, fact_id: str, *, talk_mode: str = "tell") -> None:
    data = load(presence_dir)
    facts = [str(x) for x in (data.get("shared_facts") or [])]
    fid = str(fact_id or "").strip()
    if fid and fid not in facts:
        facts.append(fid)
    data["shared_facts"] = facts
    data["last_talk_mode"] = str(talk_mode or "")
    save(presence_dir, data)


def plan_knowledge_talk(
    presence_dir: Path,
    initiator_kind: str,
    other_kind: str,
    *,
    meet_count: int,
) -> dict:
    """12+「话」：告诉知识点 或 提问你还记得吗。"""
    n = int(meet_count or 0)
    if n < 12:
        a0, b0 = dialogue_lines_for_pair(initiator_kind, other_kind, meet_count=n)
        return {"mode": "plain", "line1": a0, "line2": b0, "fact_id": "", "simple": False}

    data = load(presence_dir)
    shared = [str(x) for x in (data.get("shared_facts") or []) if knowledge_by_id(str(x))]
    last_mode = str(data.get("last_talk_mode") or "")
    # 有已分享知识点时：上次是告诉则优先提问，否则约一半概率提问
    want_quiz = bool(shared) and (last_mode == "tell" or (last_mode != "quiz" and random.random() < 0.5))
    if want_quiz:
        fact = knowledge_by_id(random.choice(shared)) or {}
        prefix = random.choice(QUIZ_PREFIXES)
        ask = str(fact.get("ask") or "这件事？")
        return {
            "mode": "quiz",
            "fact_id": str(fact.get("id") or ""),
            "line1": f"{prefix}{ask}",
            "line2": "",
            "simple": bool(fact.get("simple")),
            "topic": str(fact.get("topic") or ""),
            "hint": " / ".join(list(fact.get("answers") or ())[:2]) if fact.get("simple") else "",
        }

    unused = [f for f in KNOWLEDGE_FACTS if str(f.get("id") or "") not in shared]
    fact = dict(random.choice(unused or list(KNOWLEDGE_FACTS)))
    prefix = random.choice(TELL_PREFIXES)
    line1 = f"{prefix}{fact.get('fact')}。"
    line2 = random.choice(REMEMBER_ACK)
    return {
        "mode": "tell",
        "fact_id": str(fact.get("id") or ""),
        "line1": line1,
        "line2": line2,
        "simple": bool(fact.get("simple")),
        "topic": str(fact.get("topic") or ""),
        "hint": "",
    }


def intro_script(self_kind: str, other_kind: str) -> tuple[str, ...]:
    other = PET_DISPLAY.get(other_kind, other_kind)
    self_n = PET_DISPLAY.get(self_kind, self_kind)
    if self_kind == KIND_EIDEN:
        return (
            f"……你好，我是{self_n}。",
            f"你是{other}吧？我们终于正式见面了。",
            "以后在桌面上碰面，就多多关照啦~",
            "我也会怕，也会笑——先从招呼开始。",
            f"从这边世界来的访客，就是我。请多指教，{other}。",
        )
    return (
        f"……我是{self_n}。",
        f"原来你就是{other}啊，幸会。",
        "嗯……以后请多指教。",
    )


def greeting_lines(self_kind: str, other_kind: str) -> tuple[str, ...]:
    other = PET_DISPLAY.get(other_kind, other_kind)
    self_n = PET_DISPLAY.get(self_kind, self_kind)
    if self_kind == KIND_EIDEN and other_kind == KIND_AOBA:
        return (
            f"嗨，{other}！没想到在桌面遇见你。",
            f"{other}，碧岛的空气还习惯吗？我是{self_n}。",
            f"原来{other}也会跑出来啊……你好！",
            f"诶，是{other}！要不要一起待会儿？",
            f"{other}，旧货店今天忙吗？我刚穿过来喘口气。",
            f"跨世界打卡成功——目标：{other}。",
            f"嗨嗨，{other}。姜汤带不过来，只能用问候顶上。",
            f"{other}！别紧张，我不是来抢箱子的。",
        )
    if self_kind == KIND_AOBA and other_kind == KIND_EIDEN:
        return (
            f"……{other}？你怎么也在这儿？",
            f"嗨，{other}。旧货店今天客人少，到处逛逛也好。",
            f"{other}，欢迎来到碧岛……算是吧。",
            f"桌面另一边是{other}啊，幸会~",
        )
    return (f"你好，{other}~", f"{self_n}遇见{other}了。")


def exchange_lines(self_kind: str, other_kind: str) -> tuple[str, ...]:
    other = PET_DISPLAY.get(other_kind, other_kind)
    if self_kind == KIND_EIDEN:
        return (
            f"今天{other}看起来精神不错。",
            "我这边刚忙完，过来透口气。",
            "要是能一起去散步就好了……",
            f"{other}那边的风，闻起来比较安静。",
            "社畜技能：见面先嘘寒问暖。",
            "下次带点见闻交换？我可以用甜点配方换。",
            f"有{other}在，桌面就不那么空了。",
            "要是累了就说，我听着。",
        )
    return (
        f"莲说{other}看起来挺可靠的。",
        "平凡今天不算忙，可以多聊两句。",
        "下次要不要交换各自世界的见闻？",
    )


def build_greeting(
    self_kind: str,
    other_kind: str,
    *,
    self_companions: list[str] | None = None,
    other_companions: list[str] | None = None,
) -> str:
    sc = normalize_companions(self_companions or [])
    oc = normalize_companions(other_companions or [])
    main = random.choice(greeting_lines(self_kind, other_kind))
    extra = minipet_line(self_kind, sc, oc)
    if extra and random.random() < 0.72:
        return f"{main}\n{extra}"
    return main


def build_exchange(self_kind: str, other_kind: str) -> str:
    return random.choice(exchange_lines(self_kind, other_kind))
