"""浠庢闈㈤粯璁?JPG 澶栧湀缁垮箷鎶犲浘锛屽鍑烘墜鏈虹敤閫忔槑 PNG锛涘苟鍚屾 app 鍥炬爣銆?""
from pathlib import Path
from collections import deque
import shutil
from PIL import Image

src_dir = Path(r"C:\Users\36255\Desktop\VpetEidenPet\assets\cutout\sprites")
out_dir = Path(r"C:\Users\36255\Desktop\VpetEidenPet\VpetMobile\app\src\main\assets\sprites")
shared = Path(r"C:\Users\36255\Desktop\VpetEidenPet\VpetMobile\assets_shared\sprites")
out_dir.mkdir(parents=True, exist_ok=True)
shared.mkdir(parents=True, exist_ok=True)

for p in list(out_dir.glob("nc*")) + list(shared.glob("nc*")):
    p.unlink()

files = [
    "stand.jpg",
    "hi1.jpg",
    "hi2.jpg",
    "sleep1.jpg",
    "sleep2.jpg",
    "happy.jpg",
    "walkfront1.jpg",
    "walkfront2.jpg",
    "play_game1.jpg",
    "play_game2.jpg",
    "watch_video1.jpg",
    "video.jpg",
    "allmate.jpg",
]


def is_chroma_green(r: int, g: int, b: int, a: int = 255) -> bool:
    # 涓庢闈?pet.py _is_chroma_green / _remove_green 涓€鑷达細鍙姞澶栧湀杩為€氶敭鑹?    if a < 8:
        return False
    if g > 200 and r < 90 and b < 90:
        return True
    return g > 100 and g >= r + 15 and g >= b + 25


def remove_outer_green(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
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
        if not is_chroma_green(r, g, b, a):
            continue
        visited[y][x] = True
        px[x, y] = (r, g, b, 0)
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return rgba


# 鍙姞澶栧湀缁垮箷骞惰鍖呭洿鐩掞紝涓嶇缉鏀撅紙鏄剧ず灏哄鐢?App 杩愯鏃舵帶鍒讹級
for name in files:
    src = src_dir / name
    if not src.exists():
        print("MISSING", name)
        continue
    keyed = remove_outer_green(Image.open(src))
    bbox = keyed.getbbox()
    if bbox:
        keyed = keyed.crop(bbox)
    out_name = name.replace(".jpg", ".png")
    keyed.save(out_dir / out_name, "PNG")
    keyed.save(shared / out_name, "PNG")
    shutil.copy2(src, shared / name)
    print(out_name, keyed.size)

icon_src = Path(r"C:\Users\36255\Desktop\VpetEidenPet\app_icon.png")
res = Path(r"C:\Users\36255\Desktop\VpetEidenPet\VpetMobile\app\src\main\res")
# 鍚姩鍥炬爣鏀圭敱 tools/gen_launcher_icons.py 鐢熸垚锛堥€忔槑鎶犲浘锛夛紱姝ゅ浠呭悓姝ラ€氱煡灏忓浘
if icon_src.is_file():
    icon = Image.open(icon_src).convert("RGBA")
    drawable = res / "drawable"
    drawable.mkdir(parents=True, exist_ok=True)
    # 鑻ヤ粛鏄棫娣辫壊搴曪紝灏介噺鍘绘帀杩戦粦涓嶉€忔槑搴?    px = icon.load()
    w, h = icon.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 200 and r <= 24 and g <= 28 and b <= 40:
                px[x, y] = (0, 0, 0, 0)
    icon.resize((96, 96), Image.Resampling.LANCZOS).save(
        drawable / "ic_pet_notify.png", "PNG"
    )
    print("notify icon synced from app_icon (transparent-safe)")
else:
    print("skip icons: app_icon.png missing")
print("done")

