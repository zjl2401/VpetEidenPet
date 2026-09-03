"""像素风 UI 装饰：Vpetsign 素材 + 彩色配色。"""
from __future__ import annotations

import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageTk

# 装饰主色：彩虹（粉橙黄绿青紫），兼容旧粉蓝常量名
THEME_RAINBOW: tuple[str, ...] = (
    "#ff6b9d",
    "#ffb347",
    "#ffe066",
    "#66ddaa",
    "#66ccff",
    "#cc88ff",
)
THEME_BLUE = THEME_RAINBOW[4]
THEME_PINK = THEME_RAINBOW[0]
THEME_BLUE_DEEP = THEME_RAINBOW[5]
THEME_ORANGE = THEME_RAINBOW[1]
THEME_YELLOW = THEME_RAINBOW[2]
THEME_GREEN = THEME_RAINBOW[3]
THEME_WHITE = "#ffffff"
THEME_BLACK = "#3a2230"
THEME_BG_INNER_RGBA = (255, 244, 230, 242)
THEME_PANEL_INNER = "#fff4e6"
THEME_ITEM_BG = "#f6e4d0"

_VPETSIGN_DESKTOP = Path.home() / "Desktop" / "Vpetsign"
_SIGN_IMG_CACHE: dict[tuple[str, int, int], Image.Image] = {}
_SIGN_PHOTO_CACHE: dict[tuple[str, int, int], ImageTk.PhotoImage] = {}
_CRYSTAL_PHOTO_CACHE: dict[tuple[int, int], ImageTk.PhotoImage] = {}
_SIGN_FILE_LIST_CACHE: dict[str, list[Path]] = {}
_TRIMMED_SIGN_CACHE: dict[str, Image.Image] = {}


def resolve_signs_dir(bundle_dir: Path) -> Path:
    return bundle_dir / "assets" / "signs"


def _list_sign_files(signs_dir: Path) -> list[Path]:
    key = str(signs_dir.resolve()) if signs_dir.exists() else str(signs_dir)
    cached = _SIGN_FILE_LIST_CACHE.get(key)
    if cached is not None:
        return cached
    files: list[Path] = []
    if signs_dir.is_dir():
        pngs = sorted(signs_dir.glob("*.png"))
        if pngs:
            files = pngs
    if not files and _VPETSIGN_DESKTOP.is_dir():
        files = sorted(_VPETSIGN_DESKTOP.glob("*.jpg"))
    _SIGN_FILE_LIST_CACHE[key] = files
    return files


def load_sign_image(signs_dir: Path, index: int) -> Image.Image | None:
    files = _list_sign_files(signs_dir)
    if not files:
        return None
    idx = max(0, min(len(files) - 1, int(index)))
    path = files[idx]
    path_key = str(path.resolve()) if path.exists() else str(path)
    cached = _TRIMMED_SIGN_CACHE.get(path_key)
    if cached is not None:
        return cached
    try:
        img = Image.open(path).convert("RGBA")
        img = _clean_sign_cutout(img)
        _TRIMMED_SIGN_CACHE[path_key] = img
        return img
    except Exception:
        return None


def _is_sign_outer_key(r: int, g: int, b: int, a: int) -> bool:
    """外圈白底 / 半透明晕 / 近黑渗边（仅 flood 连通，不伤粉/黄描边）。"""
    if a < 40:
        return True
    mx, mn = max(r, g, b), min(r, g, b)
    # 近白底（含 JPEG 浅灰白、极浅粉底晕）
    if mn >= 228 and (mx - mn) <= 30:
        return True
    if mn >= 210 and (mx - mn) <= 26:
        return True
    if mn >= 200 and (mx - mn) <= 20 and a < 250:
        return True
    # 近黑脏边（预览/旧抠图残留）
    if mx <= 32 and (mx - mn) <= 16:
        return True
    # 灰白半透明晕
    if a < 170 and mn >= 150 and (mx - mn) <= 42:
        return True
    return False


def _drop_sign_noise_islands(rgba: Image.Image, *, min_keep_ratio: float = 0.08) -> Image.Image:
    """去掉与主体分离的小碎点（抠白后常见）。"""
    w, h = rgba.size
    px = rgba.load()
    vis = [[False] * w for _ in range(h)]
    components: list[list[tuple[int, int]]] = []

    for y in range(h):
        for x in range(w):
            if vis[y][x] or px[x, y][3] < 16:
                continue
            stack = [(x, y)]
            vis[y][x] = True
            comp: list[tuple[int, int]] = []
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if not (0 <= nx < w and 0 <= ny < h) or vis[ny][nx]:
                        continue
                    if px[nx, ny][3] < 16:
                        continue
                    vis[ny][nx] = True
                    stack.append((nx, ny))
            components.append(comp)

    if len(components) <= 1:
        return rgba
    components.sort(key=len, reverse=True)
    largest = len(components[0])
    keep = {p for comp in components if len(comp) >= max(12, int(largest * min_keep_ratio)) for p in comp}
    for y in range(h):
        for x in range(w):
            if px[x, y][3] >= 16 and (x, y) not in keep:
                px[x, y] = (0, 0, 0, 0)
    return rgba


def _clean_sign_cutout(img: Image.Image) -> Image.Image:
    """抠干净 Vpetsign 外圈：flood 去白底 + 剥一层近白软边，去碎点，再裁包围盒。"""
    rgba = img.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    vis = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    def try_push(x: int, y: int) -> None:
        if not (0 <= x < w and 0 <= y < h) or vis[y][x]:
            return
        r, g, b, a = px[x, y]
        if not _is_sign_outer_key(r, g, b, a):
            return
        vis[y][x] = True
        q.append((x, y))

    for x in range(w):
        try_push(x, 0)
        try_push(x, h - 1)
    for y in range(h):
        try_push(0, y)
        try_push(w - 1, y)

    while q:
        x, y = q.popleft()
        px[x, y] = (0, 0, 0, 0)
        try_push(x + 1, y)
        try_push(x - 1, y)
        try_push(x, y + 1)
        try_push(x, y - 1)

    # 与透明相邻的近白软边再剥一层；保留粉/黄实心描边
    kill: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            near_t = False
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0:
                    near_t = True
                    break
            if not near_t:
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            if a < 140:
                kill.append((x, y))
                continue
            # 仅剥近白 / 极浅灰（勿动粉描边：粉通常 g 明显更低）
            if mn >= 215 and (mx - mn) <= 36:
                kill.append((x, y))
                continue
            if mn >= 205 and (mx - mn) <= 22 and a < 250:
                kill.append((x, y))
                continue
    for x, y in kill:
        px[x, y] = (0, 0, 0, 0)

    rgba = _drop_sign_noise_islands(rgba)

    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                px[x, y] = (0, 0, 0, 0)

    bbox = rgba.getbbox()
    if bbox is None:
        return rgba
    return rgba.crop(bbox)


def _trim_sign_alpha(img: Image.Image) -> Image.Image:
    return _clean_sign_cutout(img)


def sign_photo(signs_dir: Path, index: int, size: int) -> ImageTk.PhotoImage | None:
    key = (str(signs_dir.resolve()), int(index), int(size))
    cached = _SIGN_PHOTO_CACHE.get(key)
    if cached is not None:
        return cached
    img = load_sign_image(signs_dir, index)
    if img is None:
        return None
    img = img.resize((max(8, size), max(8, size)), Image.NEAREST)
    photo = ImageTk.PhotoImage(img)
    _SIGN_PHOTO_CACHE[key] = photo
    return photo


def _strip_crystal_fringe(img: Image.Image) -> Image.Image:
    """抠掉水晶贴透明处的近白 / 近黑描边，保留内部切面色。"""
    out = img.convert("RGBA").copy()
    px = out.load()
    w, h = out.size
    neighbors = ((-1, 0), (1, 0), (0, -1), (0, 1))
    clear: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 20:
                continue
            is_white = r >= 220 and g >= 220 and b >= 220
            is_black = r <= 40 and g <= 40 and b <= 40
            if not (is_white or is_black):
                continue
            fringe = False
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h:
                    fringe = True
                    break
                if px[nx, ny][3] < 20:
                    fringe = True
                    break
            if fringe:
                clear.append((x, y))
    for x, y in clear:
        px[x, y] = (0, 0, 0, 0)
    return out


def make_crystal_image(size: int, seed: int = 0) -> Image.Image:
    """彩色水晶宝石（像素菱面，无黑/白外圈）。"""
    s = max(10, int(size))
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cols = THEME_RAINBOW
    c0 = cols[seed % len(cols)]
    c1 = cols[(seed + 2) % len(cols)]
    c2 = cols[(seed + 4) % len(cols)]
    m = s // 2
    d.polygon([(m, 1), (s - 2, m), (m, s - 2), (1, m)], fill=c0)
    d.polygon([(m, 1), (s - 2, m), (m, m)], fill=c1)
    d.polygon([(1, m), (m, s - 2), (m, m)], fill=c2)
    hi = max(1, s // 6)
    d.polygon(
        [
            (m, max(3, m - hi)),
            (m + max(1, hi // 2), m),
            (m, min(s - 4, m + hi)),
            (m - max(1, hi // 2), m),
        ],
        fill=c1,
    )
    img = _strip_crystal_fringe(img)
    img = _strip_crystal_fringe(img)
    return _strip_crystal_fringe(img)


def crystal_photo(size: int, seed: int = 0) -> ImageTk.PhotoImage:
    key = (int(size), int(seed))
    cached = _CRYSTAL_PHOTO_CACHE.get(key)
    if cached is not None:
        return cached
    photo = ImageTk.PhotoImage(make_crystal_image(size, seed))
    _CRYSTAL_PHOTO_CACHE[key] = photo
    return photo


def place_crystal_corners(wrap, *, bg: str, size: int = 14) -> None:
    """在彩虹壳四角放彩色水晶。"""
    import tkinter as tk

    photos: list[ImageTk.PhotoImage] = []
    # 四角贴在彩虹带上：Label 底色跟条带同色，避免透明菱角露出白/黑方底
    corner_bg = (
        THEME_RAINBOW[0],
        THEME_RAINBOW[-1],
        THEME_RAINBOW[-1],
        THEME_RAINBOW[0],
    )
    placements = (
        (0.0, 0.0, "nw", 3, 3, 0),
        (1.0, 0.0, "ne", -3, 3, 1),
        (0.0, 1.0, "sw", 3, -3, 2),
        (1.0, 1.0, "se", -3, -3, 3),
    )
    for i, (relx, rely, anchor, ox, oy, seed) in enumerate(placements):
        ph = crystal_photo(size, seed)
        lbl = tk.Label(wrap, image=ph, bg=corner_bg[i], bd=0, highlightthickness=0)
        lbl.image = ph  # type: ignore[attr-defined]
        lbl.place(relx=relx, rely=rely, anchor=anchor, x=ox, y=oy)
        photos.append(ph)
    wrap._vpet_crystals = photos  # type: ignore[attr-defined]


def decorate_panel_border(img: Image.Image, corner: int, signs_dir: Path) -> Image.Image:
    """在九宫格边框上叠加彩虹描边、水晶与四角标牌装饰。"""
    out = img.convert("RGBA").copy()
    draw = ImageDraw.Draw(out)
    w, h = out.size
    rainbow_rgba = tuple(
        (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255) for c in THEME_RAINBOW
    )
    band = max(3, min(6, max(3, corner // 3)))
    n = len(rainbow_rgba)

    for x in range(w):
        c = rainbow_rgba[(x // 4) % n]
        c2 = rainbow_rgba[(x // 4 + 3) % n]
        for t in range(band):
            draw.point((x, t), fill=c)
            draw.point((x, h - 1 - t), fill=c2)

    for y in range(h):
        c = rainbow_rgba[(y // 4) % n]
        c2 = rainbow_rgba[(y // 4 + 3) % n]
        for t in range(band):
            draw.point((t, y), fill=c)
            draw.point((w - 1 - t, y), fill=c2)

    placements = (
        (1, 2, 2),
        (9, w - corner - 18, h - corner - 16),
    )
    gem = min(16, max(10, corner - 2))
    for i, (gx, gy) in enumerate(((2, 2), (w - gem - 2, 2), (2, h - gem - 2), (w - gem - 2, h - gem - 2))):
        crystal = make_crystal_image(gem, i)
        out.alpha_composite(crystal, (max(0, gx), max(0, gy)))

    ornament = min(18, max(11, corner - 2))
    for sign_idx, px, py in placements:
        sign = load_sign_image(signs_dir, sign_idx)
        if sign is None:
            continue
        scaled = sign.resize((ornament, ornament), Image.NEAREST)
        sx = max(0, min(w - ornament, px))
        sy = max(0, min(h - ornament, py))
        out.alpha_composite(scaled, (sx, sy))

    return out


def draw_pixel_divider(canvas, width: int, *, height: int = 7, bg: str = THEME_PANEL_INNER) -> None:
    canvas.delete("all")
    canvas.config(height=height, bg=bg)
    w = max(40, int(width))
    n = len(THEME_RAINBOW)
    step = max(6, 8)
    for i in range(0, w, step):
        canvas.create_rectangle(
            i, 0, i + step, height - 1, fill=THEME_RAINBOW[(i // step) % n], outline=""
        )
    canvas.create_rectangle(0, height - 1, w, height, fill=THEME_WHITE, outline="")


def _default_signs_dir() -> Path:
    here = Path(__file__).resolve().parent
    bundled = here / "assets" / "signs"
    if bundled.is_dir() and any(bundled.glob("*.png")):
        return bundled
    if _VPETSIGN_DESKTOP.is_dir():
        return _VPETSIGN_DESKTOP
    return bundled


def _pack_rainbow_band(parent, *, fill: str, thickness: int, vertical: bool, reverse: bool = False) -> None:
    import tkinter as tk

    colors = tuple(reversed(THEME_RAINBOW)) if reverse else THEME_RAINBOW
    if vertical:
        bar = tk.Frame(parent, width=thickness, bg=colors[0])
        bar.pack(side=tk.LEFT if not reverse else tk.RIGHT, fill=tk.Y)
        bar.pack_propagate(False)
        for col in colors:
            tk.Frame(bar, bg=col).pack(fill=tk.BOTH, expand=True)
    else:
        bar = tk.Frame(parent, height=thickness, bg=colors[0])
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        for col in colors:
            tk.Frame(bar, bg=col).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


def pack_rainbow_accent(parent, *, height: int = 5, side: str | None = None) -> None:
    """顶/底一条加厚彩虹带（对话框、字幕条）。"""
    import tkinter as tk

    row = tk.Frame(parent, bg=THEME_WHITE, height=max(3, int(height)))
    pack_kw = {"fill": tk.X}
    if side:
        pack_kw["side"] = side
    row.pack(**pack_kw)
    row.pack_propagate(False)
    for col in THEME_RAINBOW:
        tk.Frame(row, bg=col).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


def draw_rainbow_accent(canvas, width: int, *, height: int = 4, y: int = 0) -> None:
    """在 Canvas 上画彩虹色带。"""
    w = max(1, int(width))
    h = max(2, int(height))
    n = len(THEME_RAINBOW)
    step = max(1, w // n)
    for i, col in enumerate(THEME_RAINBOW):
        x0 = i * step
        x1 = w if i == n - 1 else (i + 1) * step
        canvas.create_rectangle(x0, y, x1, y + h, fill=col, outline="")


def _pack_rainbow_shell(parent, *, bg: str, thickness: int = 6, expand: bool = True):
    """四边加厚彩虹描边，返回 (wrap, 内容区 body)。"""
    import tkinter as tk

    wrap = tk.Frame(parent, bg=bg)
    wrap.pack(fill=tk.BOTH, expand=expand)
    _pack_rainbow_band(wrap, fill=tk.X, thickness=thickness, vertical=False)
    mid = tk.Frame(wrap, bg=bg)
    mid.pack(fill=tk.BOTH, expand=True)
    _pack_rainbow_band(mid, fill=tk.Y, thickness=thickness, vertical=True)
    _pack_rainbow_band(mid, fill=tk.Y, thickness=thickness, vertical=True, reverse=True)
    body = tk.Frame(mid, bg=bg)
    body.pack(fill=tk.BOTH, expand=True)
    _pack_rainbow_band(wrap, fill=tk.X, thickness=thickness, vertical=False, reverse=True)
    wrap._vpet_chrome_body = body  # type: ignore[attr-defined]
    return wrap, body


def _pack_sign_strip(parent, *, bg: str, signs_dir: Path | None, size: int = 16) -> None:
    """顶栏：加厚彩虹条 + 中间一枚 Vpetsign。"""
    import tkinter as tk

    root_dir = signs_dir if signs_dir is not None else _default_signs_dir()
    bar = tk.Frame(parent, bg=bg)
    bar.pack(fill=tk.X)
    mid = sign_photo(root_dir, 3, size)
    stripe = tk.Frame(bar, bg=bg)
    stripe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    row = tk.Frame(stripe, bg=bg, height=7)
    row.pack(fill=tk.X)
    row.pack_propagate(False)
    for col in THEME_RAINBOW:
        tk.Frame(row, bg=col).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    tk.Frame(stripe, bg=THEME_WHITE, height=1).pack(fill=tk.X)
    if mid is not None:
        heart = tk.Label(stripe, image=mid, bg=bg, bd=0)
        heart.image = mid  # type: ignore[attr-defined]
        heart.place(relx=0.5, rely=0.5, anchor="center")
        bar._vpet_sign_mid = mid  # type: ignore[attr-defined]


def pack_menu_chrome(parent, *, bg: str, signs_dir: Path | None = None, lite: bool = False):
    """菜单外框：四边加厚彩虹描边。"""
    import tkinter as tk

    wrap, body = _pack_rainbow_shell(parent, bg=bg, thickness=7, expand=False)
    if not lite:
        _pack_sign_strip(body, bg=bg, signs_dir=signs_dir, size=12)
    else:
        _pack_rainbow_band(body, fill=tk.X, thickness=5, vertical=False)
    inner = tk.Frame(body, bg=bg, padx=5, pady=4)
    inner.pack(fill=tk.BOTH, expand=True)
    wrap._vpet_chrome_keep = body  # type: ignore[attr-defined]
    place_crystal_corners(wrap, bg=bg, size=13)
    return inner


def pack_panel_accent_bar(parent, *, bg: str, signs_dir: Path | None = None) -> None:
    """面板顶栏：彩虹条 + 一枚 Vpetsign。"""
    import tkinter as tk

    _pack_sign_strip(parent, bg=bg, signs_dir=signs_dir, size=14)
    tk.Frame(parent, bg=bg, height=2).pack(fill=tk.X)


def pack_panel_shell(parent, *, bg: str, signs_dir: Path | None = None, padx: int = 10, pady: int = 8):
    """面板壳：四边加厚彩虹描边 + 贴纸顶栏。"""
    import tkinter as tk

    wrap, body = _pack_rainbow_shell(parent, bg=bg, thickness=8, expand=True)
    inner = tk.Frame(body, bg=bg, padx=padx, pady=pady)
    inner.pack(fill=tk.BOTH, expand=True)
    pack_panel_accent_bar(inner, bg=bg, signs_dir=signs_dir)
    wrap._vpet_chrome_keep = body  # type: ignore[attr-defined]
    place_crystal_corners(wrap, bg=bg, size=16)
    return inner


# 彩虹为主，白点点缀 —— 菜单像素小图标与点击动画
_GLYPH_COLORS = THEME_RAINBOW + (THEME_WHITE,)
_GLYPH_PHOTO_CACHE: dict[tuple[str, int], ImageTk.PhotoImage] = {}


def _glyph_pattern(seed: int) -> list[tuple[int, int, str]]:
    """生成 8×8 像素图案坐标（相对原点）。"""
    colors = _GLYPH_COLORS
    c0 = colors[seed % len(colors)]
    c1 = colors[(seed + 1) % len(colors)]
    c2 = colors[(seed + 2) % len(colors)]
    style = seed % 6
    pts: list[tuple[int, int, str]] = []
    if style == 0:  # 菱形
        for x, y in ((3, 1), (2, 2), (4, 2), (1, 3), (5, 3), (2, 4), (4, 4), (3, 5)):
            pts.append((x, y, c0 if (x + y) % 2 == 0 else c1))
        pts.append((3, 3, c2))
    elif style == 1:  # 星点
        for x, y in ((3, 0), (3, 1), (2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (3, 4), (3, 5), (3, 6)):
            pts.append((x, y, c0 if y < 3 else c1))
        pts.append((3, 3, THEME_WHITE))
    elif style == 2:  # 心形小像素（彩虹分层）
        for i, (x, y) in enumerate(((2, 1), (4, 1), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (2, 4), (3, 4), (4, 4), (3, 5))):
            pts.append((x, y, colors[i % len(colors)]))
    elif style == 3:  # 对勾 / 箭头
        for x, y in ((1, 3), (2, 4), (3, 5), (4, 4), (5, 3), (6, 2)):
            pts.append((x, y, c0))
        pts.append((3, 3, c1))
    elif style == 4:  # 方框宝石
        for x in range(1, 7):
            pts.append((x, 1, c0))
            pts.append((x, 6, c1))
        for y in range(2, 6):
            pts.append((1, y, c0))
            pts.append((6, y, c1))
        pts.append((3, 3, colors[0]))
        pts.append((4, 3, THEME_WHITE))
        pts.append((3, 4, colors[2]))
        pts.append((4, 4, colors[4]))
    else:  # 波浪
        for i, (x, y) in enumerate(((1, 3), (2, 2), (3, 1), (4, 2), (5, 3), (6, 4), (2, 5), (4, 5), (5, 5))):
            pts.append((x, y, colors[i % len(colors)]))
    return pts


def make_menu_glyph_image(seed: int, size: int = 14) -> Image.Image:
    img = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    px = img.load()
    for x, y, col in _glyph_pattern(abs(int(seed))):
        if 0 <= x < 8 and 0 <= y < 8:
            r = int(col[1:3], 16)
            g = int(col[3:5], 16)
            b = int(col[5:7], 16)
            px[x, y] = (r, g, b, 255)
    # 细黑描边，贴合像素风
    out = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    base = img.load()
    out_px = out.load()
    for y in range(8):
        for x in range(8):
            if base[x, y][3] == 0:
                continue
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and base[nx, ny][3] == 0:
                    out_px[nx, ny] = (10, 12, 18, 220)
            out_px[x, y] = base[x, y]
    return out.resize((max(8, size), max(8, size)), Image.NEAREST)


def menu_glyph_photo(label: str, size: int = 14) -> ImageTk.PhotoImage:
    key = (label, int(size))
    cached = _GLYPH_PHOTO_CACHE.get(key)
    if cached is not None:
        return cached
    photo = ImageTk.PhotoImage(make_menu_glyph_image(hash(label) & 0xFFFF, size))
    _GLYPH_PHOTO_CACHE[key] = photo
    return photo


def play_pixel_click_burst(root, anchor_widget) -> None:
    """在按钮旁弹出短促像素粒子散开动画（彩虹）。失败时静默，勿阻断菜单命令。"""
    import tkinter as tk

    try:
        if not anchor_widget or not anchor_widget.winfo_exists():
            return
        ax = int(anchor_widget.winfo_rootx())
        ay = int(anchor_widget.winfo_rooty())
        aw = max(20, int(anchor_widget.winfo_width()))
        ah = max(16, int(anchor_widget.winfo_height()))

        size = 56
        win = tk.Toplevel(root)
        win.overrideredirect(True)
        try:
            setattr(win, "_vpet_no_glass", True)
        except Exception:
            pass
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass
        win.configure(bg="magenta")
        try:
            win.wm_attributes("-transparentcolor", "magenta")
        except Exception:
            pass
        canvas = tk.Canvas(win, width=size, height=size, bg="magenta", highlightthickness=0, bd=0)
        canvas.pack()
        cx, cy = size // 2, size // 2
        win.geometry(f"+{ax + aw // 2 - cx}+{ay + ah // 2 - cy}")

        particles = []
        for i, col in enumerate(_GLYPH_COLORS * 2):
            ang = (i / 10.0) * math.tau
            particles.append(
                {
                    "x": float(cx),
                    "y": float(cy),
                    "vx": 2.4 * math.cos(ang),
                    "vy": 2.4 * math.sin(ang),
                    "col": col,
                    "life": 10 + (i % 4),
                }
            )

        frame = {"n": 0}

        def tick() -> None:
            try:
                if not win.winfo_exists():
                    return
                canvas.delete("all")
                alive = False
                for p in particles:
                    if p["life"] <= 0:
                        continue
                    alive = True
                    px = int(p["x"])
                    py = int(p["y"])
                    s = 3 if p["life"] > 5 else 2
                    canvas.create_rectangle(px, py, px + s, py + s, fill=p["col"], outline="")
                    if p["life"] > 6:
                        canvas.create_rectangle(px + 1, py - 2, px + 2, py - 1, fill=THEME_WHITE, outline="")
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["vy"] += 0.18
                    p["life"] -= 1
                frame["n"] += 1
                if alive and frame["n"] < 18:
                    root.after(28, tick)
                else:
                    try:
                        win.destroy()
                    except Exception:
                        pass
            except Exception:
                try:
                    win.destroy()
                except Exception:
                    pass

        root.after(0, tick)
    except Exception:
        return
