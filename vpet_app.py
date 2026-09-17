"""Vpet 桌面程序入口：默认打开托盘启动器；--pet 直接运行桌宠；--rpg 打开 RPG。"""

from __future__ import annotations

import importlib.util
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path


def _pet_log_path() -> Path:
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local" / "Vpet"
    else:
        base = Path.home() / ".vpet"
    base.mkdir(parents=True, exist_ok=True)
    return base / "pet.log"


def _log_pet_error(exc: BaseException) -> None:
    try:
        log_path = _pet_log_path()
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n--- {datetime.now().isoformat(timespec='seconds')} ---\n")
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=fh)
    except Exception:
        pass


def _show_pet_error(exc: BaseException) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Vpet 启动失败",
            f"{exc}\n\n详情已写入：{_pet_log_path()}",
            parent=root,
        )
        root.destroy()
    except Exception:
        pass


def _sync_sidecars_from_dev_src() -> None:
    """开发机：每次启动把 Desktop\\VpetEidenPet 源码拷进 _internal，保证热更不丢。"""
    try:
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).resolve().parent
            internal = Path(getattr(sys, "_MEIPASS", str(app_dir / "_internal")))
        else:
            app_dir = Path(__file__).resolve().parent
            internal = app_dir
        src = Path.home() / "Desktop" / "VpetEidenPet"
        if not (src / "pet.py").is_file():
            src = Path(r"C:\Users\36255\Desktop\VpetEidenPet")
        if not (src / "pet.py").is_file():
            return
        names = (
            "pet.py",
            "vpet_app.py",
            "vpet_launcher.py",
            "peer_friendship.py",
            "pet_outfit.py",
            "system_media_control.py",
            "app_scene_desktop.py",
            "owner_bond.py",
            "emote_registry.py",
            "character_profile.py",
            "companion_quotes.py",
            "voice_audio.py",
            "voice_system.py",
            "panel_decor.py",
            "home_farm.py",
            "home_cottage.py",
            "bundled_paths.py",
            "media_bundled.py",
            "office_assist.py",
        )
        dests = [internal]
        # onedir：_MEIPASS 常即 _internal；再兜一份 exe 旁 _internal
        side = app_dir / "_internal"
        if side.is_dir() and side.resolve() != internal.resolve():
            dests.append(side)
        copied = []
        for name in names:
            sp = src / name
            if not sp.is_file():
                continue
            for d in dests:
                try:
                    dp = d / name
                    dp.write_bytes(sp.read_bytes())
                    copied.append(str(dp))
                except Exception:
                    pass
        try:
            stamp = internal / "HOT_RELOAD_STAMP.txt"
            stamp.write_text(
                f"synced {datetime.now().isoformat(timespec='seconds')} files={len(copied)}\n",
                encoding="utf-8",
            )
        except Exception:
            pass
        try:
            log_path = _pet_log_path()
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(
                    f"\n--- {datetime.now().isoformat(timespec='seconds')} "
                    f"dev-sync src={src} n={len(copied)} ---\n"
                )
        except Exception:
            pass
    except Exception:
        pass


def _runtime_module_dirs() -> list[Path]:
    """打包后优先找 _internal / exe 旁的 sidecar .py，便于热更新 pet.py。"""
    dirs: list[Path] = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dirs.append(Path(meipass))
        dirs.append(Path(sys.executable).resolve().parent)
        # 明确加入 exe\_internal（有的布局 _MEIPASS 与源码侧车不同步时）
        internal = Path(sys.executable).resolve().parent / "_internal"
        if internal.is_dir():
            dirs.insert(0, internal)
    dirs.append(Path(__file__).resolve().parent)
    out: list[Path] = []
    seen: set[str] = set()
    for d in dirs:
        key = str(d).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


def _load_sidecar_module(name: str) -> bool:
    """若磁盘上有同名 .py，则覆盖冻结包内模块。成功返回 True。"""
    if name in sys.modules and not getattr(sys, "frozen", False):
        return False
    for base in _runtime_module_dirs():
        path = base / f"{name}.py"
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            try:
                log_path = _pet_log_path()
                with log_path.open("a", encoding="utf-8") as fh:
                    fh.write(
                        f"\n--- {datetime.now().isoformat(timespec='seconds')} sidecar {name} <- {path} ---\n"
                    )
            except Exception:
                pass
            return True
        except Exception as exc:
            sys.modules.pop(name, None)
            try:
                _log_pet_error(exc)
            except Exception:
                pass
            continue
    return False


def _bootstrap_sidecars() -> None:
    for name in (
        "peer_friendship",
        "pet_outfit",
        "home_cottage",
        "panel_decor",
        "bundled_paths",
        "media_bundled",
        "voice_audio",
        "voice_system",
        "pet_id_cloud",
        "app_scene_desktop",
        "owner_bond",
        "emote_registry",
        "character_profile",
        "companion_quotes",
        "rhythm_chart_editor",
        "friend_talk_anim",
        "friend_crossover",
        "vpet_launcher",
        "pet",
    ):
        _load_sidecar_module(name)


def _run_rpg() -> None:
    """独立进程打开 Silent Oath（模式→游戏→RPG）。"""
    from bundled_paths import LEGACY_GAME_ROOT, resolve_bundled

    root = resolve_bundled("Vpetgame", legacy=LEGACY_GAME_ROOT)
    game_py = root / "game.py"
    if not game_py.is_file():
        raise FileNotFoundError(f"未找到 RPG：{game_py}")
    os.chdir(root)
    import runpy

    runpy.run_path(str(game_py), run_name="__main__")


def main() -> None:
    _sync_sidecars_from_dev_src()
    _bootstrap_sidecars()
    # 顶层侧显式引用，避免 PyInstaller 漏打进 pet / 启动器（二者原先在分支内 import）
    import pet  # noqa: F401
    import vpet_launcher  # noqa: F401

    if "--rpg" in sys.argv:
        try:
            _run_rpg()
        except Exception as exc:
            _log_pet_error(exc)
            _show_pet_error(exc)
            raise SystemExit(1) from exc
        return
    if "--pet" in sys.argv:
        try:
            from pet import DesktopPet

            DesktopPet().run()
        except Exception as exc:
            _log_pet_error(exc)
            _show_pet_error(exc)
            raise SystemExit(1) from exc
        return
    from vpet_launcher import main as run_launcher

    run_launcher()


if __name__ == "__main__":
    main()
