"""Vpet 托盘启动器：点击图标即可生成一只桌宠；可选开机自启并自动显示桌宠。"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

LAUNCHER_PORT = 52848  # 伊得专用；苍叶为 52847，双开互不抢端口
APP_ROOT = Path(__file__).resolve().parent
STARTUP_LNK_NAME = "Vpet Eiden.lnk"


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return APP_ROOT


def _data_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return APP_ROOT


def _userdata_dir() -> Path:
    """与 pet._resolve_app_paths 对齐：便携包用 exe 旁 data，否则 LOCALAPPDATA\\Vpet\\userdata。"""
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
        if (app_dir / "PORTABLE").is_file() or (app_dir / "PORTABLE.txt").is_file():
            d = app_dir / "data"
            d.mkdir(parents=True, exist_ok=True)
            return d
        d = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())) / "Vpet" / "userdata"
        d.mkdir(parents=True, exist_ok=True)
        return d
    # 开发态：与 pet 同目录 data
    d = APP_ROOT / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _app_config_path() -> Path:
    return _userdata_dir() / "app_config.json"


def _load_app_config_light() -> dict:
    path = _app_config_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_app_config_light(patch: dict) -> None:
    path = _app_config_path()
    cfg = _load_app_config_light()
    cfg.update(patch)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def launch_at_login_enabled() -> bool:
    """默认开启：开机启动托盘并自动显示桌宠。"""
    cfg = _load_app_config_light()
    if "launch_at_login" not in cfg:
        return True
    return bool(cfg.get("launch_at_login"))


def spawn_on_launcher_start() -> bool:
    """启动器起来时是否自动新建一只桌宠（默认与开机自启一致）。"""
    cfg = _load_app_config_light()
    if "spawn_on_launcher_start" in cfg:
        return bool(cfg.get("spawn_on_launcher_start"))
    return launch_at_login_enabled()


def _windows_startup_dir() -> Path | None:
    if sys.platform != "win32":
        return None
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _startup_lnk_path() -> Path | None:
    folder = _windows_startup_dir()
    if folder is None:
        return None
    return folder / STARTUP_LNK_NAME


def _launcher_target() -> tuple[str, str]:
    """返回 (TargetPath, WorkingDirectory)。"""
    if getattr(sys, "frozen", False):
        exe = str(Path(sys.executable).resolve())
        return exe, str(Path(sys.executable).resolve().parent)
    # 开发：用当前解释器跑 vpet_app.py（进托盘）
    script = str((APP_ROOT / "vpet_app.py").resolve())
    return sys.executable, str(APP_ROOT), script  # type: ignore[return-value]


def sync_windows_startup(enabled: bool, *, force: bool = False) -> bool:
    """写入或删除「启动」文件夹快捷方式。成功返回 True。

    默认若快捷方式已存在则跳过 PowerShell（避免每次出宠都卡几百毫秒～数秒）。
    设置里改开机自启时应传 force=True。
    """
    if sys.platform != "win32":
        return False
    lnk = _startup_lnk_path()
    if lnk is None:
        return False
    if not enabled:
        try:
            if lnk.is_file():
                lnk.unlink()
            return True
        except OSError:
            return False
    try:
        lnk.parent.mkdir(parents=True, exist_ok=True)
        # 已有快捷方式：跳过重建（出宠路径高频调用）
        if not force and lnk.is_file():
            return True
        if getattr(sys, "frozen", False):
            target = str(Path(sys.executable).resolve())
            workdir = str(Path(sys.executable).resolve().parent)
            args = ""
            icon = Path(sys.executable).resolve().parent / "app_icon.ico"
        else:
            target = sys.executable
            workdir = str(APP_ROOT)
            args = str((APP_ROOT / "vpet_app.py").resolve())
            icon = APP_ROOT / "app_icon.ico"
        icon_ps = (
            f"$s.IconLocation = '{str(icon).replace(chr(39), chr(39)+chr(39))},0'; "
            if icon.is_file()
            else ""
        )
        # PowerShell 创建 .lnk，避免依赖 pywin32
        ps = (
            "$ws = New-Object -ComObject WScript.Shell; "
            f"$s = $ws.CreateShortcut('{str(lnk).replace(chr(39), chr(39)+chr(39))}'); "
            f"$s.TargetPath = '{target.replace(chr(39), chr(39)+chr(39))}'; "
            f"$s.WorkingDirectory = '{workdir.replace(chr(39), chr(39)+chr(39))}'; "
            f"$s.Arguments = '{args.replace(chr(39), chr(39)+chr(39))}'; "
            "$s.WindowStyle = 7; "
            "$s.Description = 'Vpet Eiden 开机自启'; "
            f"{icon_ps}"
            "$s.Save()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        return lnk.is_file()
    except Exception:
        return False


def set_launch_at_login(enabled: bool) -> None:
    """设置开机自启，并同步 Windows 启动项；开启时启动器也会自动出宠。"""
    enabled = bool(enabled)
    _save_app_config_light(
        {
            "launch_at_login": enabled,
            "spawn_on_launcher_start": enabled,
        }
    )
    sync_windows_startup(enabled, force=True)


def sync_desktop_shortcut(*, force: bool = True) -> bool:
    """桌面「Vpet Eiden.lnk」：保留热更启动脚本；勿每次启动改回裸 Vpet.exe。"""
    if sys.platform != "win32":
        return False
    desktop = Path.home() / "Desktop"
    if not desktop.is_dir():
        desktop = Path.home() / "桌面"
    if not desktop.is_dir():
        return False
    lnk = desktop / STARTUP_LNK_NAME
    # 已指向热更脚本 / 多开参数：一律保留
    if lnk.is_file():
        try:
            import win32com.client  # type: ignore

            shell = win32com.client.Dispatch("WScript.Shell")
            cur = shell.CreateShortcut(str(lnk))
            cur_target = str(getattr(cur, "TargetPath", "") or "").lower().replace("/", "\\")
            cur_args = str(getattr(cur, "Arguments", "") or "").lower()
            if (
                "start_eiden.bat" in cur_target
                or "start_eiden.vbs" in cur_target
                or (cur_target.endswith("vpet.exe") and "--pet" in cur_args and "eiden" in cur_args)
            ):
                return True
        except Exception:
            try:
                ps = (
                    "$s=(New-Object -ComObject WScript.Shell).CreateShortcut("
                    f"'{str(lnk).replace(chr(39), chr(39)+chr(39))}'); "
                    "$t=($s.TargetPath+' '+$s.Arguments).ToLower(); "
                    "if($t -like '*start_eiden.bat*' -or $t -like '*start_eiden.vbs*' -or "
                    "($t -like '*vpet.exe*' -and $t -like '*--pet*' -and $t -like '*eiden*')){'KEEP'}else{'REWRITE'}"
                )
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps],
                    capture_output=True,
                    text=True,
                    timeout=8,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
                )
                if "KEEP" in (r.stdout or ""):
                    return True
            except Exception:
                pass
    # 优先写热更启动器（每次开宠前同步源码）
    hot = None
    for name in ("start_eiden.vbs", "start_eiden.bat"):
        cand = Path(sys.executable).resolve().parent / name if getattr(sys, "frozen", False) else APP_ROOT.parent / name
        if getattr(sys, "frozen", False):
            cand = Path(sys.executable).resolve().parent / name
        else:
            # 开发态：工程旁 App 目录
            cand = (APP_ROOT.parent / "VpetEidenApp" / name) if (APP_ROOT.parent / "VpetEidenApp").is_dir() else (APP_ROOT / name)
        if cand.is_file():
            hot = cand
            break
    bat = APP_ROOT / "启动 Vpet.bat"
    if hot is not None:
        target = str(hot.resolve())
        workdir = str(hot.resolve().parent)
        args = ""
        icon = hot.resolve().parent / "app_icon.ico"
        alt = hot.resolve().parent / "app_icon_eiden.ico"
        if alt.is_file():
            icon = alt
    elif getattr(sys, "frozen", False):
        target = str(Path(sys.executable).resolve())
        workdir = str(Path(sys.executable).resolve().parent)
        args = ""
        icon = Path(sys.executable).resolve().parent / "app_icon.ico"
        alt = Path(sys.executable).resolve().parent / "app_icon_eiden.ico"
        if alt.is_file():
            icon = alt
    else:
        if not bat.is_file():
            return False
        target = str(bat.resolve())
        workdir = str(APP_ROOT)
        args = ""
        icon = APP_ROOT / "app_icon.ico"
    try:
        if not force and lnk.is_file():
            try:
                import win32com.client  # type: ignore

                shell = win32com.client.Dispatch("WScript.Shell")
                cur = shell.CreateShortcut(str(lnk))
                cur_target = str(getattr(cur, "TargetPath", "") or "")
                low = cur_target.lower().replace("/", "\\")
                # 热更脚本 / 已正确的 exe：不要覆盖
                if "start_eiden.bat" in low or "start_eiden.vbs" in low:
                    return True
                if "VpetEidenPet" not in cur_target.replace("/", "\\") and (
                    low.endswith("vpet.exe")
                    or "\\vpet\\" in low
                ):
                    force = True
                else:
                    return True
            except Exception:
                return True
        if not force:
            return True
        lnk.parent.mkdir(parents=True, exist_ok=True)
        icon_ps = (
            f"$s.IconLocation = '{str(icon).replace(chr(39), chr(39)+chr(39))},0'; "
            if icon.is_file()
            else ""
        )
        ps = (
            "$ws = New-Object -ComObject WScript.Shell; "
            f"$s = $ws.CreateShortcut('{str(lnk).replace(chr(39), chr(39)+chr(39))}'); "
            f"$s.TargetPath = '{target.replace(chr(39), chr(39)+chr(39))}'; "
            f"$s.WorkingDirectory = '{workdir.replace(chr(39), chr(39)+chr(39))}'; "
            f"$s.Arguments = '{args.replace(chr(39), chr(39)+chr(39))}'; "
            "$s.WindowStyle = 1; "
            "$s.Description = 'Vpet Eiden 伊得桌宠（启动前热更）· Ctrl+Alt+Q'; "
            f"{icon_ps}"
            "$s.Save()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        return lnk.is_file()
    except Exception:
        return False


def refresh_launch_shortcuts() -> None:
    """启动器起来时刷新桌面/开机快捷方式；有热更脚本时绝不写回裸 Vpet.exe。"""
    try:
        sync_desktop_shortcut(force=True)
    except Exception:
        pass
    # 再钉一次：防止旧逻辑/竞态把快捷方式改回 exe
    try:
        if sys.platform == "win32":
            app = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else (APP_ROOT.parent / "VpetEidenApp")
            hot = app / "start_eiden.vbs"
            if not hot.is_file():
                hot = app / "start_eiden.bat"
            desktop = Path.home() / "Desktop"
            if not desktop.is_dir():
                desktop = Path.home() / "桌面"
            lnk = desktop / STARTUP_LNK_NAME
            if hot.is_file() and desktop.is_dir():
                icon = app / "app_icon.ico"
                ps = (
                    "$ws=New-Object -ComObject WScript.Shell; "
                    f"$s=$ws.CreateShortcut('{str(lnk).replace(chr(39), chr(39)+chr(39))}'); "
                    f"$s.TargetPath='{str(hot.resolve()).replace(chr(39), chr(39)+chr(39))}'; "
                    f"$s.WorkingDirectory='{str(hot.resolve().parent).replace(chr(39), chr(39)+chr(39))}'; "
                    "$s.Arguments=''; $s.WindowStyle=1; "
                    "$s.Description='Vpet Eiden hot-reload'; "
                )
                if icon.is_file():
                    ps += f"$s.IconLocation='{str(icon).replace(chr(39), chr(39)+chr(39))},0'; "
                ps += "$s.Save()"
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
                )
    except Exception:
        pass
    try:
        if launch_at_login_enabled():
            sync_windows_startup(True, force=True)
    except Exception:
        pass


def ensure_launch_prefs_defaults() -> None:
    """首次无配置时写入默认：开机自启 + 启动器自动出宠。"""
    cfg = _load_app_config_light()
    changed = False
    if "launch_at_login" not in cfg:
        cfg["launch_at_login"] = True
        changed = True
    if "spawn_on_launcher_start" not in cfg:
        cfg["spawn_on_launcher_start"] = True
        changed = True
    if changed:
        _save_app_config_light(cfg)
    refresh_launch_shortcuts()


def _my_exe() -> str:
    return str(Path(sys.executable).resolve())


def _pet_spawn_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--pet", "--kind", "eiden"]
    return [sys.executable, str(APP_ROOT / "vpet_app.py"), "--pet", "--kind", "eiden"]


def _pet_log_path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Vpet"
    else:
        base = Path.home() / ".vpet"
    base.mkdir(parents=True, exist_ok=True)
    return base / "pet.log"


_last_spawn_ts = 0.0
_spawn_lock = threading.Lock()


def _show_spawn_feedback(ms: int = 1600) -> None:
    """点击快捷方式/托盘后立刻给反馈，避免 exe 冷启期间像没反应。"""

    def _run() -> None:
        try:
            import tkinter as tk
        except Exception:
            return
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.configure(bg="#1a2233")
            label = tk.Label(
                root,
                text="正在打开桌宠…",
                fg="#ffe08a",
                bg="#1a2233",
                font=("Segoe UI", 12),
                padx=18,
                pady=12,
            )
            label.pack()
            root.update_idletasks()
            w = max(root.winfo_reqwidth(), 160)
            h = max(root.winfo_reqheight(), 40)
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
            root.after(max(800, int(ms)), root.destroy)
            root.mainloop()
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


def spawn_pet(*, show_feedback: bool = True) -> None:
    """新建一只桌宠；连点时自动错开，减轻多开同时加载卡死/闪退。"""
    if show_feedback:
        _show_spawn_feedback()

    def _do_spawn() -> None:
        global _last_spawn_ts
        with _spawn_lock:
            now = time.time()
            # 仅连点错开；首次 spawn 不要空等 1.4s（_last_spawn_ts==0 时旧逻辑会白等）
            if _last_spawn_ts > 0:
                wait = 1.4 - (now - _last_spawn_ts)
                if wait > 0.05:
                    time.sleep(wait)
            _last_spawn_ts = time.time()
        cmd = _pet_spawn_command()
        cwd = str(_data_root())
        log_path = _pet_log_path()
        try:
            log_file = log_path.open("a", encoding="utf-8")
            log_file.write(f"\n--- spawn {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            log_file.flush()
        except OSError:
            log_file = subprocess.DEVNULL
        kwargs: dict = {
            "cwd": cwd,
            "close_fds": True,
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": log_file,
        }
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        subprocess.Popen(cmd, **kwargs)

    threading.Thread(target=_do_spawn, daemon=True).start()


def _launcher_exchange(payload: str, *, timeout: float = 0.5) -> str | None:
    try:
        with socket.create_connection(("127.0.0.1", LAUNCHER_PORT), timeout=timeout) as sock:
            sock.sendall(payload.encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)
            sock.settimeout(timeout)
            data = sock.recv(512)
            return data.decode("utf-8", errors="ignore").strip() or None
    except OSError:
        return None


def _stop_other_vpet_processes() -> None:
    """已废弃：开新宠/新启动器时不得强杀其它 Vpet.exe（自身多开与跨作品共存）。"""
    return


def _hold_launcher_lock() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", LAUNCHER_PORT))
    sock.listen(5)
    return sock


def _load_tray_icon():
    from PIL import Image, ImageDraw
    from collections import deque

    def _is_chroma_green(r: int, g: int, b: int, a: int = 255) -> bool:
        if a < 8:
            return False
        if g > 200 and r < 90 and b < 90:
            return True
        return g > 100 and g >= r + 15 and g >= b + 25

    def _key_and_fit(im: Image.Image, size: int) -> Image.Image:
        rgba = im.convert("RGBA")
        w, h = rgba.size
        px = rgba.load()
        visited = [[False] * w for _ in range(h)]
        q: deque[tuple[int, int]] = deque()
        for x in range(w):
            q.append((x, 0))
            q.append((x, h - 1))
        for y in range(h):
            q.append((0, y))
            q.append((w - 1, y))
        while q:
            x, y = q.popleft()
            if x < 0 or y < 0 or x >= w or y >= h or visited[y][x]:
                continue
            r, g, b, a = px[x, y]
            if not _is_chroma_green(r, g, b, a):
                continue
            visited[y][x] = True
            px[x, y] = (r, g, b, 0)
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
        bbox = rgba.getbbox()
        if bbox:
            rgba = rgba.crop(bbox)
        # 等比装入，不拉伸
        iw, ih = rgba.size
        scale = min(size / max(iw, 1), size / max(ih, 1))
        nw = max(1, int(round(iw * scale)))
        nh = max(1, int(round(ih * scale)))
        scaled = rgba.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(scaled, ((size - nw) // 2, (size - nh) // 2), scaled)
        return canvas

    root = _resource_root()
    for rel in (
        "app_icon.png",
        "assets/sprites/stand.jpg",
        "assets/sprites/stand.png",
        "gallery/stand.png",
        "app_icon1.png",
        "app_icon1.jpg",
    ):
        path = root / rel
        if path.exists():
            # 已生成的 app_icon 直接等比缩放；源 stand 则抠绿再装入
            img = Image.open(path).convert("RGBA")
            if path.name == "app_icon.png":
                return img.resize((64, 64), Image.Resampling.LANCZOS)
            return _key_and_fit(img, 64)
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle((12, 10, 52, 54), fill="#4488ff")
    draw.rectangle((22, 18, 42, 28), fill="#ffffff")
    return img


def run_tray(*, spawn_on_start: bool = True) -> None:
    import pystray

    if spawn_on_start:
        spawn_pet()

    lock_sock = _hold_launcher_lock()
    stop_event = threading.Event()
    tray_icon: pystray.Icon | None = None

    def on_spawn(_icon=None, _item=None) -> None:
        spawn_pet()

    def on_quit(icon, _item) -> None:
        stop_event.set()
        icon.stop()

    def accept_loop() -> None:
        while not stop_event.is_set():
            try:
                lock_sock.settimeout(1.0)
                client, _addr = lock_sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with client:
                try:
                    data = client.recv(512).decode("utf-8", errors="ignore").strip()
                except OSError:
                    data = ""
                if data.startswith("hello:"):
                    remote = data[6:]
                    local = _my_exe()
                    try:
                        client.sendall(b"same" if remote == local else b"stale")
                    except OSError:
                        pass
                    continue
                if data == "quit":
                    stop_event.set()
                    if tray_icon is not None:
                        try:
                            tray_icon.stop()
                        except Exception:
                            pass
                    return
                if data == "spawn" or data.startswith("spawn"):
                    spawn_pet(show_feedback=True)

    threading.Thread(target=accept_loop, daemon=True).start()

    menu = pystray.Menu(
        pystray.MenuItem("新建桌宠", on_spawn, default=True),
        pystray.MenuItem("退出启动器", on_quit),
    )
    tip = "Vpet 桌宠"
    if spawn_on_start:
        tip += "\n已自动显示桌宠；托盘可再新建"
    else:
        tip += "\n点击「新建桌宠」生成一只"
    tray_icon = pystray.Icon(
        "Vpet",
        _load_tray_icon(),
        tip,
        menu,
    )
    try:
        tray_icon.run()
    finally:
        stop_event.set()
        try:
            lock_sock.close()
        except OSError:
            pass


def main() -> None:
    ensure_launch_prefs_defaults()
    exe = _my_exe()
    reply = _launcher_exchange(f"hello:{exe}")
    if reply == "same":
        # 同一伊得启动器已在：只加一只宠，不另开托盘
        _launcher_exchange("spawn")
        return
    if reply == "stale":
        # 端口上已有其它路径的启动器：不关闭对方、不杀进程，请它再生成一只
        _launcher_exchange("spawn")
        return
    run_tray(spawn_on_start=spawn_on_launcher_start())


if __name__ == "__main__":
    main()
