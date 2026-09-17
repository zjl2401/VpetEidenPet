"""办公助手数据层：待办 / 剪贴板历史 / 常用语 / 快捷启动（离线优先）。"""
from __future__ import annotations

import json
import time
from pathlib import Path

MAX_CLIPBOARD = 40
MAX_TODOS = 80
MAX_PHRASES = 60
MAX_LAUNCHERS = 30

DEFAULT_PHRASES: list[dict] = [
    {"id": "mail_hi", "title": "邮件开头", "text": "您好，\n\n"},
    {"id": "mail_end", "title": "邮件结尾", "text": "祝好，\n"},
    {"id": "daily_tpl", "title": "日报模板", "text": "【今日完成】\n1.\n【进行中】\n1.\n【风险/需协助】\n无\n"},
    {"id": "meeting_late", "title": "会议稍晚", "text": "抱歉，我可能会晚到一两分钟，请先开始。"},
    {"id": "ack", "title": "收到确认", "text": "收到，我这边跟进。"},
]

DEFAULT_LAUNCHERS: list[dict] = [
    {"id": "explorer", "title": "资源管理器", "target": "explorer"},
    {"id": "notepad", "title": "记事本", "target": "notepad"},
]


def _read_json(path: Path, fallback):
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class OfficeStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.todo_path = data_dir / "office_todos.json"
        self.clip_path = data_dir / "office_clipboard.json"
        self.phrase_path = data_dir / "office_phrases.json"
        self.launch_path = data_dir / "office_launchers.json"
        self.todos: list[dict] = []
        self.clipboard: list[dict] = []
        self.phrases: list[dict] = []
        self.launchers: list[dict] = []
        self._last_clip = ""
        self.load_all()

    def load_all(self) -> None:
        raw = _read_json(self.todo_path, {"items": []})
        self.todos = list(raw.get("items") or [])[:MAX_TODOS]
        raw = _read_json(self.clip_path, {"items": []})
        self.clipboard = list(raw.get("items") or [])[:MAX_CLIPBOARD]
        raw = _read_json(self.phrase_path, {})
        phrases = list(raw.get("items") or [])
        if not phrases:
            phrases = [dict(p) for p in DEFAULT_PHRASES]
            _write_json(self.phrase_path, {"items": phrases})
        self.phrases = phrases[:MAX_PHRASES]
        raw = _read_json(self.launch_path, {})
        launchers = list(raw.get("items") or [])
        if not launchers:
            launchers = [dict(x) for x in DEFAULT_LAUNCHERS]
            _write_json(self.launch_path, {"items": launchers})
        self.launchers = launchers[:MAX_LAUNCHERS]

    def save_todos(self) -> None:
        _write_json(self.todo_path, {"items": self.todos[:MAX_TODOS]})

    def save_clipboard(self) -> None:
        _write_json(self.clip_path, {"items": self.clipboard[:MAX_CLIPBOARD]})

    def save_phrases(self) -> None:
        _write_json(self.phrase_path, {"items": self.phrases[:MAX_PHRASES]})

    def save_launchers(self) -> None:
        _write_json(self.launch_path, {"items": self.launchers[:MAX_LAUNCHERS]})

    def today_todos(self, *, include_done: bool = True) -> list[dict]:
        today = time.strftime("%Y-%m-%d")
        out = []
        for t in self.todos:
            day = str(t.get("day") or today)
            if day != today and not t.get("done"):
                # 未完成跨日仍显示
                out.append(t)
            elif day == today:
                if include_done or not t.get("done"):
                    out.append(t)
        return out

    def top_open_todos(self, n: int = 3) -> list[dict]:
        open_items = [t for t in self.today_todos(include_done=True) if not t.get("done")]
        return open_items[:n]

    def add_todo(self, text: str) -> dict:
        text = (text or "").strip()
        if not text:
            raise ValueError("empty")
        item = {
            "id": f"t{int(time.time() * 1000)}",
            "text": text[:200],
            "done": False,
            "day": time.strftime("%Y-%m-%d"),
            "created": int(time.time()),
        }
        self.todos.insert(0, item)
        self.todos = self.todos[:MAX_TODOS]
        self.save_todos()
        return item

    def toggle_todo(self, todo_id: str) -> None:
        for t in self.todos:
            if t.get("id") == todo_id:
                t["done"] = not bool(t.get("done"))
                self.save_todos()
                return

    def remove_todo(self, todo_id: str) -> None:
        self.todos = [t for t in self.todos if t.get("id") != todo_id]
        self.save_todos()

    def push_clipboard(self, text: str) -> bool:
        text = (text or "").strip("\x00")
        if not text or text == self._last_clip:
            return False
        # 忽略超长二进制式内容
        if len(text) > 8000:
            text = text[:8000]
        self._last_clip = text
        # 去重：已存在则挪到最前
        self.clipboard = [c for c in self.clipboard if c.get("text") != text]
        self.clipboard.insert(
            0,
            {
                "id": f"c{int(time.time() * 1000)}",
                "text": text,
                "ts": int(time.time()),
                "preview": text.replace("\n", " ")[:80],
            },
        )
        self.clipboard = self.clipboard[:MAX_CLIPBOARD]
        self.save_clipboard()
        return True

    def clear_clipboard(self) -> None:
        self.clipboard.clear()
        self.save_clipboard()

    def add_phrase(self, title: str, text: str) -> dict:
        item = {
            "id": f"p{int(time.time() * 1000)}",
            "title": (title or "未命名")[:40],
            "text": (text or "")[:2000],
        }
        self.phrases.insert(0, item)
        self.phrases = self.phrases[:MAX_PHRASES]
        self.save_phrases()
        return item

    def remove_phrase(self, phrase_id: str) -> None:
        self.phrases = [p for p in self.phrases if p.get("id") != phrase_id]
        self.save_phrases()

    def add_launcher(self, title: str, target: str) -> dict:
        item = {
            "id": f"l{int(time.time() * 1000)}",
            "title": (title or "快捷")[:40],
            "target": (target or "").strip()[:500],
        }
        self.launchers.insert(0, item)
        self.launchers = self.launchers[:MAX_LAUNCHERS]
        self.save_launchers()
        return item

    def remove_launcher(self, launcher_id: str) -> None:
        self.launchers = [x for x in self.launchers if x.get("id") != launcher_id]
        self.save_launchers()
