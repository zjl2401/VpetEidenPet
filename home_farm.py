"""家园室外经营：农田、钱包、合成（脱离原作）。"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

# —— 流通物品 ——
ITEM_LABELS: dict[str, str] = {
    "seed_wheat": "麦种",
    "seed_berry": "莓种",
    "seed_corn": "玉米种",
    "crop_wheat": "小麦",
    "crop_berry": "莓果",
    "crop_corn": "玉米穗",
    "wood": "木材",
    "flower_cut": "采下的花",
    "fish": "鲜鱼",
    "work_reward_box": "工作宝箱",
    "achieve_reward_box": "成就宝箱",
    "dew": "水滴",
    "dew_drop": "露水",
    "fertilizer": "肥料",
    "compost": "堆肥",
    "jam_berry": "莓果酱",
}

SEED_TO_CROP: dict[str, str] = {
    "seed_wheat": "wheat",
    "seed_berry": "berry",
    "seed_corn": "corn",
}

# 成熟度：满分 100；每小时 +5；浇水后 1 小时内速率 ×2；每天最多浇 2 次
MATURITY_MAX = 100.0
MATURITY_PER_HOUR = 5.0
WATER_BOOST_SEC = 3600.0
WATER_MAX_PER_DAY = 2
TREE_REGROW_SEC = 48 * 3600
CHOP_DICE_MIN = 2
CHOP_DICE_MAX = 6

# —— 轻量种田（低压力；逻辑对齐苍叶，文案/资源名可并存）——
DAILY_ACTION_CAP = 5  # 今日经营「小事」软上限
DAILY_ACTION_SOFT = 5
DAILY_ACTION_HARD = 8
OFFLINE_GROWTH_CAP_HOURS = 12.0  # 离线成长最多按 12 小时结算
WILT_AFTER_DRY_DAYS = 4  # 连续多日未浇 → 枯萎可堆肥，不重罚
FERTILIZER_BOOST_SEC = 7200.0
POMODORO_DEW_REWARD = 1  # 番茄完成一轮赠水滴/露水

CROP_DEFS: dict[str, dict[str, Any]] = {
    "wheat": {
        "label": "小麦",
        "seed": "seed_wheat",
        "item": "crop_wheat",
        "days": 2,
        "sell": 4,
        "use": "做饭 / 烤面包",
        "tier": "stable",  # 新手稳产
        "colors": ("#c8b070", "#d4c078", "#e8d888", "#f0e090"),
    },
    "berry": {
        "label": "莓果",
        "seed": "seed_berry",
        "item": "crop_berry",
        "days": 2,
        "sell": 5,
        "use": "点心 / 送礼",
        "tier": "stable",
        "colors": ("#886688", "#aa6688", "#cc6688", "#ee5588"),
    },
    "corn": {
        "label": "玉米",
        "seed": "seed_corn",
        "item": "crop_corn",
        "days": 3,
        "sell": 5,
        "use": "烤玉米 / 饲料",
        "tier": "mid",
        "colors": ("#889944", "#aaba44", "#ccdd55", "#ffe066"),
    },
}

# 季节不是倒计时处罚，而是给每天的田园决定一个不同的“小目标”。
# 用现实月份换季，避免单机存档因长时间未开而错过内容。
SEASONS: tuple[dict[str, Any], ...] = (
    {"id": "spring", "label": "春", "months": (3, 4, 5), "accent": "#e88eaa", "favored": "berry", "event": "花信日", "note": "花与莓果更受欢迎"},
    {"id": "summer", "label": "夏", "months": (6, 7, 8), "accent": "#e8bd58", "favored": "corn", "event": "萤火夜", "note": "玉米与钓鱼订单更常见"},
    {"id": "autumn", "label": "秋", "months": (9, 10, 11), "accent": "#d58a50", "favored": "wheat", "event": "丰收茶会", "note": "小麦与果酱适合交付"},
    {"id": "winter", "label": "冬", "months": (12, 1, 2), "accent": "#82b7d9", "favored": "fish", "event": "围炉信箱", "note": "慢慢整理库存，也会收到鲜鱼委托"},
)


def current_season(*, month: int | None = None) -> dict[str, Any]:
    """Return the current low-pressure season card used by the farm HUD and orders."""
    if month is None:
        import datetime as _dt

        month = _dt.datetime.now().month
    for season in SEASONS:
        if int(month) in season["months"]:
            return dict(season)
    return dict(SEASONS[0])


def season_summary(*, month: int | None = None) -> str:
    season = current_season(month=month)
    return f"{season['label']}季·{season['event']}：{season['note']}"

# 商店：金币买种子/木材
SHOP_PRICES: dict[str, int] = {
    "seed_wheat": 3,
    "seed_berry": 4,
    "seed_corn": 4,
    "wood": 5,
}

# 售出作物
SELL_PRICES: dict[str, int] = {
    "crop_wheat": 4,
    "crop_berry": 5,
    "crop_corn": 5,
    "fish": 6,
    "flower_cut": 2,
    "jam_berry": 14,
}

# 默认可放置（布置模式）；合成解锁 sofa / shelf / 部分家电
DEFAULT_FURNITURE_UNLOCK: frozenset[str] = frozenset(
    {
        "bed",
        "table",
        "chair",
        "plant",
        "carpet",
        "lamp",
        "window",
        "vase",
        "door",
        "partition",
        "floor_wood",
        "floor_tile",
        "coffee",
        "nightstand",
        "tv",
        "wardrobe",
        "stove",
        "sink",
        "fridge",
        "counter",
        "toilet",
        "bathtub",
        "basin",
        "grass",
        "land",
        "water",
        "brick",
        "tree",
        "tree_pine",
        "tree_fruit",
        "tree_blossom",
        "rock",
        "flower",
        "fence",
        "bush",
        "path",
        "gift_art",
        "user_paint",
        "erase",
    }
)

CRAFT_ONLY_FURNITURE: frozenset[str] = frozenset({"sofa", "shelf"})

# 合成配方：id, label, costs{item:n}, result kind
# result: ("food", food_id) | ("furniture", kind) | ("item", item_id)
CRAFT_RECIPES: tuple[dict[str, Any], ...] = (
    {
        "id": "bread",
        "label": "烤面包",
        "costs": {"crop_wheat": 2},
        "result": ("food", "bread"),
        "desc": "2 小麦 → 面包",
    },
    {
        "id": "berry_snack",
        "label": "莓果点心",
        "costs": {"crop_berry": 2},
        "result": ("food", "berry"),
        "desc": "2 莓果 → 草莓",
    },
    {
        "id": "corn_food",
        "label": "烤玉米",
        "costs": {"crop_corn": 2},
        "result": ("food", "corn"),
        "desc": "2 玉米穗 → 玉米",
    },
    {
        "id": "juice",
        "label": "果汁",
        "costs": {"crop_berry": 1, "crop_wheat": 1},
        "result": ("food", "juice"),
        "desc": "莓果+小麦 → 果汁",
    },
    {
        "id": "jam_berry",
        "label": "莓果酱",
        "costs": {"crop_berry": 3},
        "result": ("item", "jam_berry"),
        "desc": "3 莓果 → 果酱（可卖 / 交订单）",
    },
    {
        "id": "sofa",
        "label": "解锁沙发",
        "costs": {"wood": 3, "crop_wheat": 1},
        "result": ("furniture", "sofa"),
        "desc": "3 木材+1 小麦 → 解锁沙发",
    },
    {
        "id": "shelf",
        "label": "解锁柜子",
        "costs": {"wood": 2, "crop_berry": 1},
        "result": ("furniture", "shelf"),
        "desc": "2 木材+1 莓果 → 解锁柜子",
    },
)

FARM_DISCLAIMER = "轻量种田 · 每天一小步"

# 工具键位：切换 / 确定使用
FARM_TOOL_KEYS: dict[str, str] = {
    "1": "till",
    "z": "till",
    "Z": "till",
    "2": "plant",
    "x": "plant",
    "X": "plant",
    "3": "water",
    "c": "water",
    "C": "water",
    "4": "harvest",
    "v": "harvest",
    "V": "harvest",
    "5": "chop",
    "b": "chop",
    "B": "chop",
    "6": "fish",
    "f": "fish",
    "F": "fish",
    "7": "pick",
    "g": "pick",
    "G": "pick",
    "8": "fert",
    "h": "fert",
    "H": "fert",
}

FARM_TOOL_LABELS: dict[str, str] = {
    "till": "锄地",
    "plant": "播种",
    "water": "浇水",
    "harvest": "收获",
    "chop": "砍树",
    "fish": "钓鱼",
    "pick": "采花",
    "fert": "施肥",
}

FARM_TOOL_HINTS: dict[str, str] = {
    "till": "先清上面，再锄两下草地→土地",
    "plant": "仅土地可种；可批量同种",
    "water": "每天有限次；湿土一眼蓝点；可全浇",
    "harvest": "成熟可收；枯了可堆肥；可全收",
    "chop": "点树四周格子；掷骰砍够次数得木材",
    "fish": "点水面四周格子；上钩时再按一次",
    "pick": "采小花：可插花瓶，或在面板背包戴到头顶",
    "fert": "肥料/堆肥加速成长；不强制每日点满",
}

FARM_GUIDE_BODY = (
    "· 每天建议只做 3～5 件小事（浇/收/种/摸），别当肝游。\n"
    "· 主循环：锄地 → 播种 → 浇水 → 收获（约 30～90 秒一轮）。\n"
    "· 离线也会慢慢长大（有上限）；枯了可堆肥，不重罚。\n"
    "· 可用「全浇 / 全收 / 全种」批量操作；番茄钟完成会掉水滴。\n"
    "· 合成可做果酱；每日订单交付换金币；可摸摸小团子。\n"
    "· 数字键切换工具；确定 / Enter / 空格在脚下执行。"
)

FARM_GUIDE_SECTIONS: tuple[tuple[str, str, str], ...] = (
    ("🚪", "进入", "室外 →「经营」"),
    ("🚶", "移动", "WASD / 点格子"),
    ("1️⃣", "锄地", "先清上面；草地锄两下变土地"),
    ("2️⃣", "播种", "种在土地格中心；可全种"),
    ("3️⃣", "浇水", "湿土蓝点；可全浇"),
    ("4️⃣", "收获", "成熟收；枯了堆肥；可全收"),
    ("5️⃣", "砍树", "在树四周格操作"),
    ("6️⃣", "钓鱼", "在水面四周格操作"),
    ("7️⃣", "采花", "可插花瓶；面板背包可戴/摘"),
    ("8️⃣", "施肥", "肥料/堆肥加速；枯株用「收」堆肥"),
    ("⏎", "执行", "数字键只切换工具；确定 / Enter / 空格才执行"),
    ("🛒", "商店", "购买种子与木材"),
    ("⚒", "合成", "食物 / 果酱 / 解锁家具"),
    ("📋", "订单", "每日两单，交付作物换金币"),
    ("🐑", "团子", "每天摸摸 / 喂食提心情"),
    ("✦", "羁绊", "专注契约完成可掉种子/露水"),
)

SEED_START: dict[str, int] = {
    "seed_wheat": 6,
    "seed_berry": 2,
    "seed_corn": 2,
    "wood": 1,
    "flower_cut": 0,
    "fish": 0,
    "dew": 2,
    "dew_drop": 0,
    "fertilizer": 0,
    "compost": 0,
    "jam_berry": 0,
}

DEFAULT_RANCH_PET: dict[str, Any] = {
    "name": "团子",
    "kind": "sheep",
    "mood": 70,
    "last_pet_ymd": "",
    "last_feed_ymd": "",
}

ORDER_POOL: tuple[dict[str, Any], ...] = (
    {"id": "o_wheat", "item": "crop_wheat", "need": 2, "pay": 12, "label": "茶会订单·小麦×2"},
    {"id": "o_berry", "item": "crop_berry", "need": 2, "pay": 14, "label": "茶会订单·莓果×2"},
    {"id": "o_corn", "item": "crop_corn", "need": 2, "pay": 14, "label": "茶会订单·玉米×2"},
    {"id": "o_jam", "item": "jam_berry", "need": 1, "pay": 20, "label": "茶会订单·果酱×1"},
    {"id": "o_fish", "item": "fish", "need": 1, "pay": 10, "label": "茶会订单·鲜鱼×1"},
    {"id": "o_flower", "item": "flower_cut", "need": 2, "pay": 8, "label": "茶会订单·花×2"},
)


def default_wallet() -> dict:
    return {
        "coins": 20,
        "items": dict(SEED_START),
        "last_daily_coin_ymd": "",
        "farm_day": "",
        "farm_actions_today": 0,
        "farm_quests": {},
        "farm_orders_ymd": "",
        "farm_orders": [],
        "ranch_pet": dict(DEFAULT_RANCH_PET),
    }


def normalize_wallet(raw: object) -> dict:
    base = default_wallet()
    if not isinstance(raw, dict):
        return base
    coins = max(0, int(raw.get("coins") or 0))
    items_in = raw.get("items") if isinstance(raw.get("items"), dict) else {}
    items: dict[str, int] = {}
    for k in ITEM_LABELS:
        items[k] = max(0, int(items_in.get(k, base["items"].get(k, 0))))
    for k, v in items_in.items():
        if k not in items:
            try:
                items[str(k)] = max(0, int(v))
            except Exception:
                pass
    last_day = str(raw.get("last_daily_coin_ymd") or "").strip()
    farm_day = str(raw.get("farm_day") or "").strip()
    farm_actions = max(0, int(raw.get("farm_actions_today") or 0))
    quests = raw.get("farm_quests") if isinstance(raw.get("farm_quests"), dict) else {}
    pet_raw = raw.get("ranch_pet") if isinstance(raw.get("ranch_pet"), dict) else {}
    ranch = dict(DEFAULT_RANCH_PET)
    ranch["name"] = str(pet_raw.get("name") or ranch["name"])[:8] or "团子"
    ranch["kind"] = str(pet_raw.get("kind") or "sheep")
    ranch["mood"] = max(0, min(100, int(pet_raw.get("mood") or 70)))
    ranch["last_pet_ymd"] = str(pet_raw.get("last_pet_ymd") or "")
    ranch["last_feed_ymd"] = str(pet_raw.get("last_feed_ymd") or "")
    orders_raw = raw.get("farm_orders") if isinstance(raw.get("farm_orders"), list) else []
    orders: list[dict] = []
    for o in orders_raw[:4]:
        if isinstance(o, dict) and o.get("id"):
            orders.append(
                {
                    "id": str(o.get("id")),
                    "item": str(o.get("item") or ""),
                    "need": max(1, int(o.get("need") or 1)),
                    "pay": max(1, int(o.get("pay") or 1)),
                    "label": str(o.get("label") or o.get("id")),
                    "done": bool(o.get("done")),
                }
            )
    return {
        "coins": coins,
        "items": items,
        "last_daily_coin_ymd": last_day,
        "farm_day": farm_day,
        "farm_actions_today": farm_actions,
        "farm_quests": quests,
        "farm_orders_ymd": str(raw.get("farm_orders_ymd") or "").strip(),
        "farm_orders": orders,
        "ranch_pet": ranch,
    }


DAILY_LOGIN_COINS = 1


def try_claim_daily_login_coin(wallet: dict, *, today: str | None = None) -> tuple[bool, int]:
    """每天首次打开领取登录金币。返回 (是否领取成功, 当前持有)。"""
    import datetime as _dt

    day = today or _dt.datetime.now().strftime("%Y-%m-%d")
    if str(wallet.get("last_daily_coin_ymd") or "") == day:
        return False, int(wallet.get("coins") or 0)
    wallet["last_daily_coin_ymd"] = day
    total = grant_coins_to_wallet(wallet, DAILY_LOGIN_COINS)
    return True, total


def load_wallet(path: Path) -> dict:
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return normalize_wallet(data)
        except Exception:
            pass
    return default_wallet()


def save_wallet(path: Path, wallet: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = normalize_wallet(wallet)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def blank_farm(cols: int, rows: int) -> list[list[dict | None]]:
    return [[None for _ in range(cols)] for _ in range(rows)]


def _day_key(ts: float | None = None) -> str:
    import datetime as _dt

    return _dt.datetime.fromtimestamp(float(ts if ts is not None else time.time())).strftime("%Y-%m-%d")


def _normalize_plot(v: object) -> dict | None:
    if not isinstance(v, dict):
        return None
    crop = str(v.get("crop") or "").strip()
    if crop not in CROP_DEFS:
        return None
    planted = int(v.get("planted_at") or 0)
    now = time.time()
    if "maturity" in v:
        maturity = max(0.0, min(MATURITY_MAX, float(v.get("maturity") or 0)))
    else:
        # 旧档：按经过小时粗略迁移
        watered = int(v.get("watered") or 0)
        elapsed_h = max(0.0, (now - planted) / 3600.0) if planted else 0.0
        maturity = max(0.0, min(MATURITY_MAX, elapsed_h * MATURITY_PER_HOUR + watered * 8.0))
    return {
        "crop": crop,
        "planted_at": planted,
        "maturity": maturity,
        "last_tick": float(v.get("last_tick") or planted or now),
        "boost_until": float(v.get("boost_until") or 0),
        "water_day": str(v.get("water_day") or ""),
        "water_count": int(v.get("water_count") or 0),
        # 兼容旧 UI 字段
        "watered": int(v.get("water_count") or v.get("watered") or 0),
    }


def normalize_farm(raw: object, cols: int, rows: int) -> list[list[dict | None]]:
    out = blank_farm(cols, rows)
    if not isinstance(raw, list):
        return out
    for y in range(min(rows, len(raw))):
        row = raw[y]
        if not isinstance(row, list):
            continue
        for x in range(min(cols, len(row))):
            out[y][x] = _normalize_plot(row[x])
    return out


def normalize_crafted_furniture(raw: object) -> list[str]:
    out: list[str] = []
    if not isinstance(raw, list):
        return out
    for v in raw:
        k = str(v or "").strip()
        if k and k not in out:
            out.append(k)
    return out


def furniture_unlocked(kind: str, crafted: list[str] | None) -> bool:
    if kind in DEFAULT_FURNITURE_UNLOCK:
        return True
    if kind in (crafted or []):
        return True
    # 非合成限定的其它 kind（如未来扩展）默认可用
    if kind not in CRAFT_ONLY_FURNITURE:
        return True
    return False


def advance_plot_maturity(plot: dict | None, *, now: float | None = None) -> None:
    """按真实时间推进成熟度（浇水加成区间内 ×2）。"""
    if not plot:
        return
    t_now = float(now if now is not None else time.time())
    last = float(plot.get("last_tick") or plot.get("planted_at") or t_now)
    if t_now <= last:
        plot["last_tick"] = t_now
        return
    maturity = float(plot.get("maturity") or 0.0)
    boost_until = float(plot.get("boost_until") or 0.0)
    rate = MATURITY_PER_HOUR / 3600.0
    t0 = last
    while t0 < t_now and maturity < MATURITY_MAX:
        if t0 < boost_until:
            seg = min(t_now, boost_until)
            maturity += (seg - t0) * rate * 2.0
            t0 = seg
        else:
            maturity += (t_now - t0) * rate
            t0 = t_now
    plot["maturity"] = max(0.0, min(MATURITY_MAX, maturity))
    plot["last_tick"] = t_now


def advance_farm(farm: list[list[dict | None]], *, now: float | None = None) -> None:
    t_now = float(now if now is not None else time.time())
    for row in farm:
        if not isinstance(row, list):
            continue
        for plot in row:
            if isinstance(plot, dict):
                advance_plot_maturity(plot, now=t_now)


def apply_offline_growth(
    farm: list[list[dict | None]],
    *,
    now: float | None = None,
    cap_hours: float = OFFLINE_GROWTH_CAP_HOURS,
) -> float:
    """
    打开家园时结算离线成长：每格最多按 cap_hours 推进，防挂机爆炸。
    返回实际结算的小时数（各格取最大）。
    """
    t_now = float(now if now is not None else time.time())
    capped = 0.0
    for row in farm:
        if not isinstance(row, list):
            continue
        for plot in row:
            if not isinstance(plot, dict):
                continue
            last = float(plot.get("last_tick") or plot.get("planted_at") or t_now)
            gap_h = max(0.0, (t_now - last) / 3600.0)
            if gap_h <= 0:
                continue
            use_h = min(gap_h, float(cap_hours))
            capped = max(capped, use_h)
            # 把 last_tick 前移，使 advance 只吃 capped 时段
            plot["last_tick"] = t_now - use_h * 3600.0
            advance_plot_maturity(plot, now=t_now)
            _refresh_wilt_flag(plot, now=t_now)
    return capped


def crop_card(crop_id: str) -> dict[str, Any]:
    """作物信息卡：季节感用天数近似，卖价与用途一眼懂。"""
    meta = CROP_DEFS.get(crop_id) or {}
    return {
        "id": crop_id,
        "label": str(meta.get("label") or crop_id),
        "days": int(meta.get("days") or 2),
        "sell": int(meta.get("sell") or SELL_PRICES.get(str(meta.get("item") or ""), 0)),
        "use": str(meta.get("use") or "—"),
        "tier": str(meta.get("tier") or "mid"),
        "seed": str(meta.get("seed") or ""),
    }


def plot_moisture(plot: dict | None, *, now: float | None = None) -> str:
    """土壤状态：dry / wet / ready / wilt。"""
    if not plot:
        return "empty"
    t_now = float(now if now is not None else time.time())
    advance_plot_maturity(plot, now=t_now)
    if plot.get("wilted"):
        return "wilt"
    if plot_ready(plot, now=t_now):
        return "ready"
    if plot_boost_active(plot, now=t_now):
        return "wet"
    day = _day_key(t_now)
    if str(plot.get("water_day") or "") == day and int(plot.get("water_count") or 0) > 0:
        return "wet"
    return "dry"


def plot_soil_state(plot: dict | None, *, now: float | None = None) -> str:
    """对齐苍叶命名：empty / wilted / ready / wet / dry。"""
    st = plot_moisture(plot, now=now)
    return {"wilt": "wilted", "empty": "empty"}.get(st, st)


def crop_card_text(crop_id: str) -> str:
    card = crop_card(crop_id)
    if not card.get("label"):
        return crop_id
    return f"{card['label']} · 约{card['days']}天 · 卖{card['sell']} · {card.get('use') or ''}"


def can_spend_farm_action(wallet: dict, *, today: str | None = None) -> tuple[bool, str]:
    ensure_farm_day(wallet, today=today)
    n = int(wallet.get("farm_actions_today") or 0)
    if n >= DAILY_ACTION_HARD:
        return False, f"今天小事已做满 {DAILY_ACTION_HARD} 件，明天再来～"
    if n >= DAILY_ACTION_SOFT:
        return True, f"今日已做 {n}/{DAILY_ACTION_SOFT} 件（还可继续，别肝坏了）"
    return True, f"今日小事 {n}/{DAILY_ACTION_SOFT}"


def today_farm_quest(farm: list[list[dict | None]], wallet: dict) -> str:
    """短句今日推荐（对齐苍叶）。"""
    dry = ready = wilted = empty_land = 0
    for row in farm:
        if not isinstance(row, list):
            continue
        for plot in row:
            if not isinstance(plot, dict):
                empty_land += 1
                continue
            st = plot_soil_state(plot)
            if st == "dry":
                dry += 1
            elif st == "ready":
                ready += 1
            elif st == "wilted":
                wilted += 1
    if wilted:
        return f"今日推荐：把 {wilted} 格枯萎作物收成堆肥"
    if ready:
        return f"今日推荐：收菜 {ready} 格（可用「全收」）"
    if dry:
        return f"今日推荐：浇水 {min(dry, 5)} 格（可用「全浇」）"
    items = wallet.get("items") or {}
    seeds = sum(int(items.get(s, 0) or 0) for s in SEED_TO_CROP)
    if seeds > 0 and empty_land > 0:
        return "今日推荐：种一格稳产菜（麦/莓）"
    if seeds <= 0:
        return "今日推荐：去商店买点麦种"
    return "今日推荐：摆一件装饰 / 歇一会儿也很好"


def claim_offline_garden(
    farm: list[list[dict | None]],
    wallet: dict,
    *,
    now: float | None = None,
) -> tuple[bool, str]:
    """打开经营时：推进成长 + 每日一次离线微收益（对齐苍叶）。"""
    t_now = float(now if now is not None else time.time())
    day = _day_key(t_now)
    hours = apply_offline_growth(farm, now=t_now)
    already = str(wallet.get("farm_offline_ymd") or "") == day
    bits: list[str] = []
    if hours >= 0.4:
        bits.append(f"离线微成长约 {hours:.1f} 小时")
    if not already:
        watered = 0
        for row in farm:
            if not isinstance(row, list):
                continue
            for plot in row:
                if not isinstance(plot, dict) or plot.get("wilted"):
                    continue
                if plot_ready(plot) or plot_boost_active(plot):
                    continue
                plot["water_day"] = day
                plot["water_count"] = max(1, int(plot.get("water_count") or 0))
                plot["boost_until"] = t_now + WATER_BOOST_SEC
                watered += 1
                if watered >= 2:
                    break
            if watered >= 2:
                break
        coins = 1 if hours >= 1.0 else 0
        if coins:
            wallet["coins"] = int(wallet.get("coins") or 0) + coins
            bits.append(f"金币+{coins}")
        if watered:
            bits.append(f"自动润土 {watered} 格")
        wallet["farm_offline_ymd"] = day
    wallet["last_farm_visit"] = t_now
    if bits:
        return True, " · ".join(bits)
    return False, ""


def grant_pomodoro_farm_drop(wallet: dict) -> str:
    """番茄完成 → 家园掉落露水（对齐苍叶 API；同步水滴库存）。"""
    items = wallet.setdefault("items", {})
    items["dew_drop"] = int(items.get("dew_drop", 0)) + 1
    items["dew"] = int(items.get("dew", 0)) + 1
    return "番茄完成！家园掉落露水 ×1（经营里可点「露水」浇一格）"


def try_use_dew_drop(farm: list[list[dict | None]], wallet: dict) -> tuple[bool, str]:
    """消耗 1 露水/水滴：浇最干的一格。"""
    items = wallet.setdefault("items", {})
    dew = int(items.get("dew_drop", 0)) + int(items.get("dew", 0))
    if dew <= 0:
        return False, "没有露水"
    target = None
    for row in farm:
        if not isinstance(row, list):
            continue
        for plot in row:
            if not isinstance(plot, dict) or plot.get("wilted"):
                continue
            if plot_ready(plot) or plot_boost_active(plot):
                continue
            target = plot
            break
        if target is not None:
            break
    if target is None:
        return False, "没有需要浇的干地"
    if int(items.get("dew_drop", 0)) > 0:
        items["dew_drop"] = int(items.get("dew_drop", 0)) - 1
    else:
        items["dew"] = int(items.get("dew", 0)) - 1
    now = time.time()
    advance_plot_maturity(target, now=now)
    target["boost_until"] = now + WATER_BOOST_SEC
    target["water_day"] = _day_key(now)
    target["water_count"] = max(1, int(target.get("water_count") or 0))
    return True, "用露水浇了一格！"


def _refresh_wilt_flag(plot: dict, *, now: float | None = None) -> None:
    """多日未浇且未成熟 → 标记枯萎（可堆肥），不直接清空。"""
    if not plot or plot_ready(plot, now=now):
        plot.pop("wilted", None)
        return
    t_now = float(now if now is not None else time.time())
    planted = float(plot.get("planted_at") or t_now)
    age_days = max(0.0, (t_now - planted) / 86400.0)
    water_day = str(plot.get("water_day") or "")
    dry_days = age_days
    if water_day:
        try:
            import datetime as _dt

            last = _dt.datetime.strptime(water_day, "%Y-%m-%d")
            dry_days = max(0.0, ( _dt.datetime.fromtimestamp(t_now) - last).total_seconds() / 86400.0)
        except Exception:
            pass
    if dry_days >= WILT_AFTER_DRY_DAYS and age_days >= WILT_AFTER_DRY_DAYS:
        plot["wilted"] = True
    else:
        plot.pop("wilted", None)


def ensure_farm_day(wallet: dict, *, today: str | None = None) -> None:
    day = today or _day_key()
    if str(wallet.get("farm_day") or "") != day:
        wallet["farm_day"] = day
        wallet["farm_actions_today"] = 0
        wallet["farm_quests"] = _fresh_daily_quests(day)


def _fresh_daily_quests(day: str) -> dict:
    """今日小目标板：3 件小事即可。"""
    return {
        "day": day,
        "water": {"need": 2, "done": 0, "label": "浇水 2 次"},
        "harvest": {"need": 1, "done": 0, "label": "收获 1 次"},
        "plant": {"need": 1, "done": 0, "label": "播种 1 次"},
    }


def farm_actions_left(wallet: dict) -> int:
    ensure_farm_day(wallet)
    used = int(wallet.get("farm_actions_today") or 0)
    return max(0, DAILY_ACTION_CAP - used)


def note_farm_action(wallet: dict, kind: str, *, count: int = 1) -> tuple[bool, str]:
    """记录今日小事；超额时仍允许操作但提示「今日已够轻」。"""
    ensure_farm_day(wallet)
    wallet["farm_actions_today"] = int(wallet.get("farm_actions_today") or 0) + max(1, int(count))
    quests = wallet.get("farm_quests") if isinstance(wallet.get("farm_quests"), dict) else {}
    q = quests.get(kind) if isinstance(quests.get(kind), dict) else None
    if q is not None:
        q["done"] = int(q.get("done") or 0) + max(1, int(count))
        quests[kind] = q
        wallet["farm_quests"] = quests
    left = farm_actions_left(wallet)
    if left <= 0:
        return True, "今日小事已做够，可以歇啦（仍可继续，但不催肝）"
    return True, f"今日还可轻松再做 {left} 件"


def daily_quest_summary(wallet: dict) -> str:
    ensure_farm_day(wallet)
    quests = wallet.get("farm_quests") if isinstance(wallet.get("farm_quests"), dict) else {}
    parts = []
    for key in ("water", "harvest", "plant"):
        q = quests.get(key) if isinstance(quests.get(key), dict) else None
        if not q:
            continue
        done = int(q.get("done") or 0)
        need = int(q.get("need") or 1)
        mark = "✓" if done >= need else f"{min(done, need)}/{need}"
        parts.append(f"{q.get('label') or key} {mark}")
    left = farm_actions_left(wallet)
    head = f"今日小事剩 {left}/{DAILY_ACTION_CAP}"
    return head + (" · " + " · ".join(parts) if parts else "")


def try_compost(farm: list[list[dict | None]], wallet: dict, x: int, y: int) -> tuple[bool, str]:
    """枯萎作物堆肥回收（低惩罚）。"""
    if y < 0 or x < 0 or y >= len(farm) or x >= len(farm[0]):
        return False, "超出范围"
    plot = farm[y][x]
    if not plot:
        return False, "空地"
    _refresh_wilt_flag(plot)
    if not plot.get("wilted") and not plot_ready(plot):
        # 未枯也可主动铲掉换少量堆肥（更轻）
        farm[y][x] = None
        items = wallet.setdefault("items", {})
        items["compost"] = int(items.get("compost", 0)) + 1
        return True, "已收回，换成堆肥 +1"
    farm[y][x] = None
    items = wallet.setdefault("items", {})
    items["compost"] = int(items.get("compost", 0)) + 2
    items["fertilizer"] = int(items.get("fertilizer", 0)) + 1
    return True, "枯株堆肥：堆肥+2、肥料+1"


def try_fertilize(farm: list[list[dict | None]], wallet: dict, x: int, y: int) -> tuple[bool, str]:
    if y < 0 or x < 0 or y >= len(farm) or x >= len(farm[0]):
        return False, "超出范围"
    plot = farm[y][x]
    if not plot:
        return False, "没有作物"
    items = wallet.setdefault("items", {})
    if int(items.get("fertilizer", 0)) <= 0 and int(items.get("compost", 0)) <= 0:
        return False, "没有肥料/堆肥"
    if int(items.get("fertilizer", 0)) > 0:
        items["fertilizer"] = int(items.get("fertilizer", 0)) - 1
    else:
        items["compost"] = int(items.get("compost", 0)) - 1
    now = time.time()
    advance_plot_maturity(plot, now=now)
    plot["boost_until"] = max(float(plot.get("boost_until") or 0), now + FERTILIZER_BOOST_SEC)
    plot["maturity"] = min(MATURITY_MAX, float(plot.get("maturity") or 0) + 12.0)
    return True, "施肥！成长加速一段时间"


def grant_pomodoro_farm_reward(wallet: dict) -> str:
    """番茄完成 → 家园水滴（兼容旧名；内部走露水掉落）。"""
    return grant_pomodoro_farm_drop(wallet)


def grant_focus_contract_farm_drop(wallet: dict) -> str:
    """专注契约完成 → 少量种子或露水（长线经营对接羁绊）。"""
    items = wallet.setdefault("items", {})
    # 轮换：优先补莓种，其次麦种，再露水
    if int(items.get("seed_berry", 0) or 0) < 8:
        items["seed_berry"] = int(items.get("seed_berry", 0) or 0) + 1
        return "专注契约完成！掉落莓种 ×1"
    if int(items.get("seed_wheat", 0) or 0) < 10:
        items["seed_wheat"] = int(items.get("seed_wheat", 0) or 0) + 1
        return "专注契约完成！掉落麦种 ×1"
    items["dew"] = int(items.get("dew", 0) or 0) + 1
    items["dew_drop"] = int(items.get("dew_drop", 0) or 0) + 1
    return "专注契约完成！掉落露水 ×1"


def consume_dew_for_extra_water(wallet: dict) -> bool:
    items = wallet.setdefault("items", {})
    if int(items.get("dew", 0)) <= 0:
        return False
    items["dew"] = int(items.get("dew", 0)) - 1
    return True


def batch_water(
    farm: list[list[dict | None]],
    wallet: dict | None = None,
) -> tuple[int, str]:
    """全浇：所有未成熟作物。可用水滴突破每日 2 次上限。"""
    ok_n = 0
    for y, row in enumerate(farm):
        if not isinstance(row, list):
            continue
        for x, plot in enumerate(row):
            if not isinstance(plot, dict):
                continue
            ok, _msg = try_water(farm, x, y, wallet=wallet, allow_dew=True)
            if ok:
                ok_n += 1
    if wallet is not None and ok_n:
        note_farm_action(wallet, "water", count=ok_n)
    if ok_n <= 0:
        return 0, "没有需要浇的地"
    return ok_n, f"全浇完成 · {ok_n} 格"


def batch_harvest(farm: list[list[dict | None]], wallet: dict) -> tuple[int, str]:
    ok_n = 0
    compost_n = 0
    for y, row in enumerate(farm):
        if not isinstance(row, list):
            continue
        for x, plot in enumerate(row):
            if not isinstance(plot, dict):
                continue
            _refresh_wilt_flag(plot)
            if plot.get("wilted"):
                ok, _ = try_compost(farm, wallet, x, y)
                if ok:
                    compost_n += 1
                continue
            ok, _ = try_harvest(farm, wallet, x, y)
            if ok:
                ok_n += 1
    if ok_n:
        note_farm_action(wallet, "harvest", count=ok_n)
    if ok_n <= 0 and compost_n <= 0:
        return 0, "没有可收的菜"
    tip = f"全收 · 收获 {ok_n}"
    if compost_n:
        tip += f" · 堆肥 {compost_n}"
    return ok_n + compost_n, tip


def batch_plant(
    farm: list[list[dict | None]],
    wallet: dict,
    outdoor_tiles: list,
    seed_id: str,
    *,
    cell_kind,
) -> tuple[int, str]:
    ok_n = 0
    for y, row in enumerate(farm):
        if not isinstance(row, list):
            continue
        for x in range(len(row)):
            ok, _ = try_plant(farm, wallet, outdoor_tiles, x, y, seed_id, cell_kind=cell_kind)
            if ok:
                ok_n += 1
    if ok_n:
        note_farm_action(wallet, "plant", count=ok_n)
    if ok_n <= 0:
        return 0, "没有可种的土地或种子不足"
    return ok_n, f"全种完成 · {ok_n} 格 {ITEM_LABELS.get(seed_id, seed_id)}"


def plot_stage(plot: dict | None, *, now: float | None = None) -> int:
    """0..3 仅用于上色阶段。"""
    if not plot:
        return -1
    advance_plot_maturity(plot, now=now)
    prog = float(plot.get("maturity") or 0.0) / MATURITY_MAX
    if prog >= 1.0:
        return 3
    if prog >= 0.66:
        return 2
    if prog >= 0.33:
        return 1
    return 0


def plot_progress(plot: dict | None, *, now: float | None = None) -> float:
    """成长进度 0.0..1.0（成熟为 1）。"""
    if not plot:
        return 0.0
    advance_plot_maturity(plot, now=now)
    return max(0.0, min(1.0, float(plot.get("maturity") or 0.0) / MATURITY_MAX))


def plot_ready(plot: dict | None, *, now: float | None = None) -> bool:
    if not plot:
        return False
    advance_plot_maturity(plot, now=now)
    return float(plot.get("maturity") or 0.0) >= MATURITY_MAX - 1e-6


def plot_color(plot: dict | None, *, now: float | None = None) -> str:
    if not plot:
        return "#5a4830"
    crop = str(plot.get("crop") or "")
    meta = CROP_DEFS.get(crop)
    if not meta:
        return "#5a4830"
    colors = meta["colors"]
    st = plot_stage(plot, now=now)
    return colors[min(st, len(colors) - 1)]


def plot_boost_active(plot: dict | None, *, now: float | None = None) -> bool:
    if not plot:
        return False
    t_now = float(now if now is not None else time.time())
    return float(plot.get("boost_until") or 0) > t_now


def can_farm_at(outdoor_tiles: list, x: int, y: int, cell_blocks) -> bool:
    """无实体阻挡才可经营（允许草地等非 solid）。"""
    if y < 0 or x < 0 or y >= len(outdoor_tiles) or x >= len(outdoor_tiles[0]):
        return False
    return not cell_blocks(outdoor_tiles, x, y)


def _tile_key(x: int, y: int) -> str:
    return f"{int(x)},{int(y)}"


def try_till(
    farm: list[list[dict | None]],
    outdoor_tiles: list,
    x: int,
    y: int,
    *,
    till_hits: dict,
    cell_kind,
    try_place,
    clear_at,
) -> tuple[bool, str]:
    """锄地：先除掉上面小花/灌木；草地需锄两下变成土地；顺带清空作物。"""
    if y < 0 or x < 0 or y >= len(farm) or x >= len(farm[0]):
        return False, "超出范围"
    farm[y][x] = None
    kind = cell_kind(outdoor_tiles, x, y)
    # 上面的小花/灌木先清掉
    if kind in ("flower", "bush"):
        clear_at(outdoor_tiles, x, y)
        try_place(outdoor_tiles, "grass", x, y)
        till_hits.pop(_tile_key(x, y), None)
        return True, "已除掉上面的东西"
    if kind == "land":
        till_hits.pop(_tile_key(x, y), None)
        return True, "土地已整理，可以播种"
    if kind == "grass" or kind is None:
        key = _tile_key(x, y)
        hits = int(till_hits.get(key) or 0) + 1
        if hits >= 2:
            try_place(outdoor_tiles, "land", x, y)
            till_hits.pop(key, None)
            return True, "草地已翻成土地，可以播种了"
        till_hits[key] = hits
        return True, "再锄一下，草地就会变成土地"
    return False, "这里不能锄成田"


def try_plant(
    farm: list[list[dict | None]],
    wallet: dict,
    outdoor_tiles: list,
    x: int,
    y: int,
    seed_id: str,
    *,
    cell_kind,
) -> tuple[bool, str]:
    if seed_id not in SEED_TO_CROP:
        return False, "请先选择种子"
    if y < 0 or x < 0 or y >= len(farm) or x >= len(farm[0]):
        return False, "超出范围"
    if cell_kind(outdoor_tiles, x, y) != "land":
        return False, "请先把草地锄成土地（锄两下）"
    if farm[y][x] is not None:
        return False, "这里已有作物"
    items = wallet.setdefault("items", {})
    if int(items.get(seed_id, 0)) <= 0:
        return False, f"{ITEM_LABELS.get(seed_id, seed_id)}不足"
    items[seed_id] = int(items.get(seed_id, 0)) - 1
    now = int(time.time())
    farm[y][x] = {
        "crop": SEED_TO_CROP[seed_id],
        "planted_at": now,
        "maturity": 0.0,
        "last_tick": float(now),
        "boost_until": 0.0,
        "water_day": "",
        "water_count": 0,
        "watered": 0,
    }
    return True, "已播种"


def try_water(
    farm: list[list[dict | None]],
    x: int,
    y: int,
    *,
    wallet: dict | None = None,
    allow_dew: bool = False,
) -> tuple[bool, str]:
    if y < 0 or x < 0 or y >= len(farm) or x >= len(farm[0]):
        return False, "超出范围"
    plot = farm[y][x]
    if not plot:
        return False, "空地无需浇水"
    now = time.time()
    advance_plot_maturity(plot, now=now)
    _refresh_wilt_flag(plot, now=now)
    if plot.get("wilted"):
        return False, "已枯萎，请堆肥回收"
    if plot_ready(plot, now=now):
        return False, "已成熟，请收获"
    day = _day_key(now)
    if str(plot.get("water_day") or "") != day:
        plot["water_day"] = day
        plot["water_count"] = 0
    count = int(plot.get("water_count") or 0)
    if count >= WATER_MAX_PER_DAY:
        if allow_dew and wallet is not None and consume_dew_for_extra_water(wallet):
            pass  # 用水滴突破今日上限
        else:
            return False, "今天已经浇过两次了（可用水滴加浇）"
    plot["water_count"] = count + 1
    plot["watered"] = plot["water_count"]
    plot["boost_until"] = now + WATER_BOOST_SEC
    plot.pop("wilted", None)
    return True, "浇水！一小时内成长速度×2"


def try_harvest(
    farm: list[list[dict | None]],
    wallet: dict,
    x: int,
    y: int,
    *,
    extra_chance: float = 0.0,
) -> tuple[bool, str]:
    if y < 0 or x < 0 or y >= len(farm) or x >= len(farm[0]):
        return False, "超出范围"
    plot = farm[y][x]
    if not plot:
        return False, "没有作物"
    _refresh_wilt_flag(plot)
    if plot.get("wilted"):
        return try_compost(farm, wallet, x, y)
    if not plot_ready(plot):
        return False, "还没成熟"
    crop = str(plot.get("crop") or "")
    meta = CROP_DEFS.get(crop)
    if not meta:
        farm[y][x] = None
        return False, "未知作物"
    item_id = str(meta["item"])
    items = wallet.setdefault("items", {})
    # 轻品质：浇过水更容易多收 1
    bonus = 1 if int(plot.get("water_count") or 0) >= 1 and plot_boost_active(plot) is False else 0
    if float(plot.get("boost_until") or 0) > 0:
        bonus = 1
    gain = 1 + (1 if bonus and (hash(str(plot.get("planted_at"))) % 3 == 0) else 0)
    # 好友同家园微加成：额外一颗（低概率，不替代肝度）
    if gain <= 1 and float(extra_chance) > 0 and (hash(str(plot.get("planted_at")) + "bond") % 100) < int(float(extra_chance) * 100):
        gain += 1
    items[item_id] = int(items.get(item_id, 0)) + gain
    farm[y][x] = None
    star = "★" if gain > 1 else ""
    tip = f"收获了{ITEM_LABELS.get(item_id, item_id)}×{gain}{star}"
    if gain > 1 and float(extra_chance) > 0:
        tip += "（好友微加成）"
    return True, tip


def try_chop_start_or_hit(
    outdoor_tiles: list,
    wallet: dict,
    x: int,
    y: int,
    *,
    chop_jobs: dict,
    tree_regrow: list,
    cell_kind,
    clear_at,
    try_place,
    rng,
) -> tuple[bool, str, dict | None]:
    """砍树：首次对树掷骰决定次数；砍完得木材，48h 后可再生。"""
    kind = cell_kind(outdoor_tiles, x, y)
    key = _tile_key(x, y)
    job = chop_jobs.get(key) if isinstance(chop_jobs.get(key), dict) else None
    if kind != "tree" and not job:
        return False, "这里没有可砍的树（需树木素材）", None
    if kind == "tree" and not job:
        need = int(rng.randint(CHOP_DICE_MIN, CHOP_DICE_MAX))
        chop_jobs[key] = {"need": need, "done": 1, "x": int(x), "y": int(y)}
        if need <= 1:
            clear_at(outdoor_tiles, x, y)
            try_place(outdoor_tiles, "grass", x, y)
            chop_jobs.pop(key, None)
            items = wallet.setdefault("items", {})
            items["wood"] = int(items.get("wood", 0)) + 1
            tree_regrow.append({"x": int(x), "y": int(y), "ready_at": time.time() + TREE_REGROW_SEC})
            return True, f"掷出 {need}！一斧砍倒，木材+1（48h可再生）", {"dice": need}
        return True, f"掷出 {need}！砍树 1/{need}", {"dice": need}
    assert job is not None
    job["done"] = int(job.get("done") or 0) + 1
    need = max(1, int(job.get("need") or 1))
    done = int(job["done"])
    if done < need:
        return True, f"砍树 {done}/{need}", None
    # 砍倒
    clear_at(outdoor_tiles, x, y)
    try_place(outdoor_tiles, "grass", x, y)
    chop_jobs.pop(key, None)
    items = wallet.setdefault("items", {})
    items["wood"] = int(items.get("wood", 0)) + 1
    tree_regrow.append(
        {"x": int(x), "y": int(y), "ready_at": time.time() + TREE_REGROW_SEC}
    )
    return True, "树倒了！木材+1（48小时后可再生）", None


def process_tree_regrow(
    outdoor_tiles: list,
    tree_regrow: list,
    *,
    cell_kind,
    try_place,
    now: float | None = None,
) -> int:
    """到期的树重新长出来。返回再生数量。"""
    t_now = float(now if now is not None else time.time())
    remain: list = []
    n = 0
    for item in list(tree_regrow):
        if not isinstance(item, dict):
            continue
        ready = float(item.get("ready_at") or 0)
        x, y = int(item.get("x") or 0), int(item.get("y") or 0)
        if ready > t_now:
            remain.append(item)
            continue
        if cell_kind(outdoor_tiles, x, y) in (None, "grass", "land", "path", "brick"):
            try_place(outdoor_tiles, "tree", x, y)
            n += 1
        else:
            # 格上有东西则稍后再试
            item["ready_at"] = t_now + 3600
            remain.append(item)
    tree_regrow[:] = remain
    return n


def try_pick_flower(
    outdoor_tiles: list,
    wallet: dict,
    x: int,
    y: int,
    *,
    cell_kind,
    clear_at,
    try_place,
) -> tuple[bool, str]:
    if cell_kind(outdoor_tiles, x, y) != "flower":
        return False, "这里没有小花"
    clear_at(outdoor_tiles, x, y)
    try_place(outdoor_tiles, "grass", x, y)
    items = wallet.setdefault("items", {})
    items["flower_cut"] = int(items.get("flower_cut", 0)) + 1
    return True, "采到花了！可插花瓶，或面板背包戴头顶"


def try_put_flower_in_vase(
    indoor_tiles: list,
    wallet: dict,
    x: int,
    y: int,
    *,
    cell_kind,
    make_filled_vase,
    vase_filled=None,
) -> tuple[bool, str]:
    if cell_kind(indoor_tiles, x, y) != "vase":
        return False, "请点在花瓶上"
    if callable(vase_filled) and vase_filled(indoor_tiles, x, y):
        return False, "花瓶里已有花，先拔出来再插"
    items = wallet.setdefault("items", {})
    if int(items.get("flower_cut", 0)) <= 0:
        return False, "还没有采下的花"
    items["flower_cut"] = int(items.get("flower_cut", 0)) - 1
    make_filled_vase(indoor_tiles, x, y)
    return True, "花已插进花瓶"


def try_take_flower_from_vase(
    indoor_tiles: list,
    wallet: dict,
    x: int,
    y: int,
    *,
    cell_kind,
    vase_filled,
    empty_vase,
    vase_color: str | None = None,
) -> tuple[bool, str]:
    """从已插花的花瓶拔出，花回背包。"""
    if cell_kind(indoor_tiles, x, y) != "vase":
        return False, "请点在花瓶上"
    if not vase_filled(indoor_tiles, x, y):
        return False, "花瓶里没有花"
    if not empty_vase(indoor_tiles, x, y, color=vase_color):
        return False, "拔花失败"
    items = wallet.setdefault("items", {})
    items["flower_cut"] = int(items.get("flower_cut", 0)) + 1
    return True, "已拔出花，放回背包"


def find_adjacent_water(tiles: list, x: int, y: int, cell_kind) -> tuple[int, int] | None:
    """四邻中找一格水面；用于岸边钓鱼。"""
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nx, ny = int(x) + dx, int(y) + dy
        try:
            if cell_kind(tiles, nx, ny) == "water":
                return nx, ny
        except Exception:
            continue
    return None


def find_adjacent_tree(
    tiles: list,
    x: int,
    y: int,
    cell_kind,
    chop_jobs: dict | None = None,
) -> tuple[int, int] | None:
    """四邻中找一棵树；优先正在砍的那棵。"""
    found: list[tuple[int, int]] = []
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nx, ny = int(x) + dx, int(y) + dy
        try:
            if cell_kind(tiles, nx, ny) == "tree":
                found.append((nx, ny))
        except Exception:
            continue
    if not found:
        return None
    if isinstance(chop_jobs, dict):
        for nx, ny in found:
            if isinstance(chop_jobs.get(_tile_key(nx, ny)), dict):
                return nx, ny
    return found[0]


def roll_fish_result(rng) -> tuple[bool, str, str]:
    """返回 (成功?, 提示, 奖励类型 coin|fish|fail)。"""
    r = rng.random()
    if r < 0.45:
        return True, "钓到鲜鱼！", "fish"
    if r < 0.7:
        return True, "钓到小东西，换成金币 +2", "coin"
    return False, "鱼跑了……", "fail"


def buy_item(wallet: dict, item_id: str, amount: int = 1) -> tuple[bool, str]:
    price = SHOP_PRICES.get(item_id)
    if price is None:
        return False, "无法购买"
    amount = max(1, int(amount))
    cost = price * amount
    coins = int(wallet.get("coins") or 0)
    if coins < cost:
        return False, f"金币不足（需 {cost}）"
    wallet["coins"] = coins - cost
    items = wallet.setdefault("items", {})
    items[item_id] = int(items.get(item_id, 0)) + amount
    return True, f"购入 {ITEM_LABELS.get(item_id, item_id)} ×{amount}"


def sell_item(wallet: dict, item_id: str, amount: int = 1) -> tuple[bool, str]:
    price = SELL_PRICES.get(item_id)
    if price is None:
        return False, "不可出售"
    amount = max(1, int(amount))
    items = wallet.setdefault("items", {})
    have = int(items.get(item_id, 0))
    if have < amount:
        return False, "数量不足"
    items[item_id] = have - amount
    wallet["coins"] = int(wallet.get("coins") or 0) + price * amount
    return True, f"售出 +{price * amount} 金币"


def can_afford_recipe(wallet: dict, recipe: dict) -> bool:
    items = wallet.get("items") if isinstance(wallet.get("items"), dict) else {}
    costs = recipe.get("costs") or {}
    for k, n in costs.items():
        if int(items.get(k, 0)) < int(n):
            return False
    return True


def try_craft(wallet: dict, crafted: list[str], recipe_id: str) -> tuple[bool, str, Any]:
    """
    成功返回 (True, msg, result_payload)
    result_payload: ("food", id) | ("furniture", kind) | None
    """
    recipe = next((r for r in CRAFT_RECIPES if r["id"] == recipe_id), None)
    if recipe is None:
        return False, "未知配方", None
    if not can_afford_recipe(wallet, recipe):
        return False, "材料不足", None
    kind_t, out_id = recipe["result"]
    if kind_t == "furniture" and out_id in crafted:
        return False, "已解锁该家具", None
    items = wallet.setdefault("items", {})
    for k, n in (recipe.get("costs") or {}).items():
        items[k] = int(items.get(k, 0)) - int(n)
        if items[k] <= 0:
            items[k] = 0
    if kind_t == "furniture":
        if out_id not in crafted:
            crafted.append(out_id)
        return True, f"已解锁家具：{out_id}", ("furniture", out_id)
    if kind_t == "food":
        return True, f"合成食物：{out_id}", ("food", out_id)
    if kind_t == "item":
        items[out_id] = int(items.get(out_id, 0)) + 1
        return True, f"获得 {ITEM_LABELS.get(out_id, out_id)}", ("item", out_id)
    return False, "配方无效", None


def grant_coins_to_wallet(wallet: dict, n: int) -> int:
    n = max(0, int(n))
    wallet["coins"] = int(wallet.get("coins") or 0) + n
    return int(wallet["coins"])


def spend_coins_from_wallet(wallet: dict, n: int) -> bool:
    n = max(0, int(n))
    coins = int(wallet.get("coins") or 0)
    if coins < n:
        return False
    wallet["coins"] = coins - n
    return True


def item_summary(wallet: dict, *, limit: int = 6) -> str:
    items = wallet.get("items") if isinstance(wallet.get("items"), dict) else {}
    parts = []
    for k, label in ITEM_LABELS.items():
        n = int(items.get(k, 0))
        if n > 0:
            parts.append(f"{label}{n}")
        if len(parts) >= limit:
            break
    return " ".join(parts) if parts else "空"


def ensure_daily_orders(wallet: dict, *, today: str | None = None) -> list[dict]:
    day = today or _day_key()
    if str(wallet.get("farm_orders_ymd") or "") == day and isinstance(wallet.get("farm_orders"), list):
        return list(wallet["farm_orders"])
    dig = sum(int(c) for c in day if c.isdigit()) or 1
    season = current_season()
    favored = str(season.get("favored") or "")
    # 一单随季节变化、一单轮换；既有季节感，也不把作物锁死在当季。
    favored_pool = [o for o in ORDER_POOL if favored in str(o.get("id") or "") or (favored == "fish" and o.get("item") == "fish")]
    picks: list[dict] = []
    for i in range(2):
        source = favored_pool if i == 0 and favored_pool else list(ORDER_POOL)
        o = dict(source[(dig + i * 3) % len(source)])
        o["done"] = False
        if i == 0:
            o["label"] = f"{season['event']}·{o['label']}"
        picks.append(o)
    wallet["farm_orders_ymd"] = day
    wallet["farm_orders"] = picks
    return picks


def try_fulfill_order(wallet: dict, order_id: str) -> tuple[bool, str]:
    orders = wallet.get("farm_orders") if isinstance(wallet.get("farm_orders"), list) else []
    target = None
    for o in orders:
        if str(o.get("id")) == str(order_id):
            target = o
            break
    if not target:
        return False, "找不到订单"
    if target.get("done"):
        return False, "这份订单已完成"
    item = str(target.get("item") or "")
    need = max(1, int(target.get("need") or 1))
    items = wallet.setdefault("items", {})
    if int(items.get(item, 0)) < need:
        return False, f"{ITEM_LABELS.get(item, item)}不足（需要 {need}）"
    items[item] = int(items.get(item, 0)) - need
    pay = max(1, int(target.get("pay") or 1))
    grant_coins_to_wallet(wallet, pay)
    target["done"] = True
    return True, f"交付成功！+{pay} 金币"


def ensure_ranch_pet(wallet: dict) -> dict:
    pet = wallet.get("ranch_pet")
    if not isinstance(pet, dict):
        pet = dict(DEFAULT_RANCH_PET)
        wallet["ranch_pet"] = pet
    return pet


def ranch_pet_status(wallet: dict) -> str:
    pet = ensure_ranch_pet(wallet)
    name = str(pet.get("name") or "团子")
    mood = int(pet.get("mood") or 0)
    feel = "开心" if mood >= 70 else ("平静" if mood >= 40 else "有点闷")
    return f"{name} · 心情 {mood}（{feel}）"


def pet_ranch_animal(wallet: dict, *, today: str | None = None) -> tuple[bool, str]:
    day = today or _day_key()
    pet = ensure_ranch_pet(wallet)
    if str(pet.get("last_pet_ymd") or "") == day:
        return False, "今天已经摸过啦"
    pet["last_pet_ymd"] = day
    pet["mood"] = min(100, int(pet.get("mood") or 0) + 8)
    return True, f"摸摸{pet.get('name') or '团子'}！心情 +8"


def feed_ranch_animal(wallet: dict, *, today: str | None = None) -> tuple[bool, str]:
    day = today or _day_key()
    pet = ensure_ranch_pet(wallet)
    if str(pet.get("last_feed_ymd") or "") == day:
        return False, "今天已经喂过啦"
    items = wallet.setdefault("items", {})
    feed_item = None
    for cand in ("crop_wheat", "crop_berry", "crop_corn", "jam_berry"):
        if int(items.get(cand, 0)) > 0:
            feed_item = cand
            break
    if not feed_item:
        return False, "没有可喂的作物/果酱"
    items[feed_item] = int(items.get(feed_item, 0)) - 1
    pet["last_feed_ymd"] = day
    pet["mood"] = min(100, int(pet.get("mood") or 0) + 12)
    return True, f"喂了{ITEM_LABELS.get(feed_item, feed_item)}，心情 +12"


def ranch_mood_offline_bonus(wallet: dict) -> int:
    pet = ensure_ranch_pet(wallet)
    mood = int(pet.get("mood") or 0)
    if mood >= 80:
        return 2
    if mood >= 50:
        return 1
    return 0
