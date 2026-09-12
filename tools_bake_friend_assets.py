#!/usr/bin/env python3
"""烘焙 friend 绿幕 JPG → assets/cutout/friend（不含占位选项图）。"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "assets" / "raw_green" / "friend"
CUT = ROOT / "assets" / "cutout" / "friend"


def _remove_green(img: Image.Image) -> Image.Image:
    try:
        import numpy as np
        from collections import deque

        arr = np.asarray(img.convert("RGBA"), dtype=np.uint8).copy()
        h, w = arr.shape[:2]
        r = arr[..., 0].astype(np.int16)
        g = arr[..., 1].astype(np.int16)
        b = arr[..., 2].astype(np.int16)
        a = arr[..., 3]
        key = (a > 8) & (
            ((g > 200) & (r < 90) & (b < 90))
            | ((g > 100) & (g >= r + 15) & (g >= b + 25))
        )
        visited = np.zeros((h, w), dtype=bool)
        q: deque[tuple[int, int]] = deque()
        for x in range(w):
            for y in (0, h - 1):
                if key[y, x] and not visited[y, x]:
                    visited[y, x] = True
                    q.append((x, y))
        for y in range(h):
            for x in (0, w - 1):
                if key[y, x] and not visited[y, x]:
                    visited[y, x] = True
                    q.append((x, y))
        while q:
            x, y = q.popleft()
            arr[y, x, 3] = 0
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and key[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    q.append((nx, ny))
        return Image.fromarray(arr, "RGBA")
    except Exception:
        rgba = img.convert("RGBA")
        px = rgba.load()
        w, h = rgba.size

        def is_g(rr, gg, bb):
            return ((gg > 200) and (rr < 90) and (bb < 90)) or (
                (gg > 100) and (gg >= rr + 15) and (gg >= bb + 25)
            )

        for y in range(h):
            for x in range(w):
                rr, gg, bb, aa = px[x, y]
                if aa > 8 and is_g(rr, gg, bb):
                    px[x, y] = (rr, gg, bb, 0)
        return rgba


def bake_folder(sub: str) -> None:
    src_dir = RAW / sub
    out_dir = CUT / sub
    out_dir.mkdir(parents=True, exist_ok=True)
    if not src_dir.is_dir():
        print(f"missing {src_dir}")
        return
    for src in sorted(src_dir.glob("*.jpg")) + sorted(src_dir.glob("*.jpeg")):
        out = out_dir / f"{src.stem}.png"
        rgba = _remove_green(Image.open(src))
        rgba.save(out, format="PNG", optimize=True)
        print(f"bake {sub}/{out.name} {rgba.size}")
        if sub == "action" and "lv1" in src.stem.lower():
            bbox = rgba.getbbox()
            crop = rgba.crop(bbox) if bbox else rgba
            icon = crop.copy()
            icon.thumbnail((48, 48), Image.NEAREST)
            icon_path = out_dir / f"{src.stem}_icon.png"
            icon.save(icon_path, format="PNG", optimize=True)
            print(f"  icon {icon_path.name} {icon.size}")


def detect_red_box(path: Path) -> tuple[int, int, int, int] | None:
    img = Image.open(path).convert("RGBA")
    px = img.load()
    w, h = img.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 200 and r > 200 and g < 80 and b < 80:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def main() -> int:
    bake_folder("action")
    bake_folder("talk")
    hash_png = CUT / "talk" / "selecttalk#.png"
    if hash_png.is_file():
        print(f"red_box {detect_red_box(hash_png)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
