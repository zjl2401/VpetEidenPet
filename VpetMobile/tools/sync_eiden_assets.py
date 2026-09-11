"""Sync Eiden desk work sprites + curated music into mobile assets."""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "app" / "src" / "main" / "assets" / "sprites"
MUSIC = ROOT / "app" / "src" / "main" / "assets" / "music"
DESK_BLACK = Path(r"C:\Users\36255\Desktop\VpetEiden\PNGblack")
DESK_MUSIC = Path(r"C:\Users\36255\Desktop\VpetEiden\music")


def convert_work() -> None:
    SPRITES.mkdir(parents=True, exist_ok=True)
    # 主立绘 work_0~5；细节 1/2/3work
    names = [f"work_{i}" for i in range(6)] + ["1work", "2work", "3work"]
    for name in names:
        src = DESK_BLACK / f"{name}.jpg"
        if not src.is_file():
            print("missing", src)
            continue
        im = Image.open(src).convert("RGBA")
        px = im.load()
        w, h = im.size
        out = Image.new("RGBA", im.size)
        opx = out.load()
        for y in range(h):
            for x in range(w):
                r, g, b, _a = px[x, y]
                if r < 18 and g < 18 and b < 18:
                    opx[x, y] = (0, 0, 0, 0)
                else:
                    opx[x, y] = (r, g, b, 255)
        dst = SPRITES / f"{name}.png"
        out.save(dst)
        print("work", name, dst.stat().st_size)


def sync_music() -> None:
    # Remove Aoba leftovers
    for child in list(MUSIC.iterdir()) if MUSIC.is_dir() else []:
        if child.is_dir() and child.name.lower().startswith(
            ("aoba", "koujaku", "mink", "mizuki", "noiz", "ren", "virus", "clear")
        ):
            shutil.rmtree(child, ignore_errors=True)
            print("removed", child.name)

    bgm = MUSIC / "BGM"
    theme = MUSIC / "主题曲"
    other = MUSIC / "其他"
    for d in (bgm, theme, other):
        d.mkdir(parents=True, exist_ok=True)

    picks_bgm = [f"pluviasilvae - BGM{i:03d}.mp3" for i in range(1, 9)]
    picks_theme = [
        "pluviasilvae - Summer Dream (instrumental).mp3",
        "pluviasilvae - Take Me to Your Paradise.mp3",
    ]
    picks_other = [
        "pluviasilvae - Summer Dream (Blade Ver.).mp3",
    ]

    def copy_list(names: list[str], dest: Path) -> None:
        for n in names:
            src = DESK_MUSIC / n
            if not src.is_file():
                print("skip missing", n)
                continue
            dst = dest / n
            if dst.is_file() and dst.stat().st_size == src.stat().st_size:
                print("keep", n)
                continue
            shutil.copy2(src, dst)
            print("music", dest.name, n, dst.stat().st_size)

    copy_list(picks_bgm, bgm)
    copy_list(picks_theme, theme)
    copy_list(picks_other, other)

    readme = MUSIC / "README.txt"
    readme.write_text(
        "伊得曲库精简包（对照桌面 VpetEiden/music）。\n"
        "BGM / 主题曲 / 其他；完整曲库过大不打进 APK。\n",
        encoding="utf-8",
    )
    print("music done")


if __name__ == "__main__":
    convert_work()
    sync_music()
