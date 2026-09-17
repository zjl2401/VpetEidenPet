"""Sync desktop / VpetMobile assets into VpetFlutter/assets."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
MOBILE = REPO / "VpetMobile" / "app" / "src" / "main" / "assets"
DESK_BLACK = Path.home() / "Desktop" / "VpetEiden" / "PNGblack"
DESK_MUSIC = Path.home() / "Desktop" / "VpetEiden" / "music"
DESK_VOICE = Path.home() / "Desktop" / "VpetEiden" / "voice"

OUT_SPRITES = ROOT / "assets" / "sprites"
OUT_MUSIC = ROOT / "assets" / "music"
OUT_VOICE = ROOT / "assets" / "voice"
OUT_DATA = ROOT / "assets" / "data"

CORE_SPRITES = (
    "stand.png",
    "walkleft1.png",
    "walkleft2.png",
    "walkfront1.png",
    "walkfront2.png",
    "sleep1.png",
    "sleep2.png",
    "happy.png",
    "hi1.png",
    "hi2.png",
    "work_0.png",
    "work_1.png",
    "squat.png",
    "shy1.png",
    "wink.png",
    "border.png",
    "Aster1.png",
    "Morvay1.png",
    "flag.png",
    "box.png",
)


def ensure_dirs() -> None:
    for d in (OUT_SPRITES, OUT_MUSIC, OUT_VOICE, OUT_DATA):
        d.mkdir(parents=True, exist_ok=True)
    for cat in ("dizzy", "hurt", "normal", "sleep", "work", "yuqi", "misc"):
        (OUT_VOICE / cat).mkdir(parents=True, exist_ok=True)
        keep = OUT_VOICE / cat / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def sync_sprites() -> None:
    src_dir = MOBILE / "sprites"
    for name in CORE_SPRITES:
        src = src_dir / name
        if src.is_file():
            shutil.copy2(src, OUT_SPRITES / name)
            print("sprite", name)
        else:
            print("missing sprite", name)


def sync_music() -> None:
    bgm = OUT_MUSIC / "BGM"
    bgm.mkdir(parents=True, exist_ok=True)
    mobile_bgm = MOBILE / "music" / "BGM"
    if mobile_bgm.is_dir():
        for f in list(mobile_bgm.glob("*.mp3"))[:8]:
            shutil.copy2(f, bgm / f.name)
            print("music", f.name)
    elif DESK_MUSIC.is_dir():
        for i in range(1, 5):
            name = f"pluviasilvae - BGM{i:03d}.mp3"
            src = DESK_MUSIC / name
            if src.is_file():
                shutil.copy2(src, bgm / name)
                print("music desk", name)


def sync_voice_sample() -> None:
    mobile_voice = MOBILE / "voice"
    if not mobile_voice.is_dir():
        print("no mobile voice")
        return
    # Wipe prior copies — Chinese/ellipsis filenames break Flutter asset copy on Windows.
    if OUT_VOICE.exists():
        for old in OUT_VOICE.rglob("*"):
            if old.is_file() and old.name != ".gitkeep":
                old.unlink(missing_ok=True)
    by_cat: dict[str, int] = {}
    count = 0
    for f in sorted(mobile_voice.rglob("*.wav")):
        if count >= 20:
            break
        # Prefer path segment under Vpet/<category>/
        parts = f.relative_to(mobile_voice).parts
        cat = "misc"
        if len(parts) >= 2:
            cat = parts[-2]
        cat = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in cat) or "misc"
        n = by_cat.get(cat, 0) + 1
        by_cat[cat] = n
        dst_dir = OUT_VOICE / cat
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / f"{cat}_{n:02d}.wav"
        shutil.copy2(f, dst)
        count += 1
        print("voice", cat, "->", dst.name)


def write_seed_data() -> None:
    (OUT_DATA / "preset_dialogs.json").write_text(
        '[{"q":"今天过得怎么样？","a":["还不错啦。","有你在就很好。"]},'
        '{"q":"喜欢我吗？","a":["……突然问这个。","嗯。"]}]',
        encoding="utf-8",
    )
    (OUT_DATA / "vocab_en.json").write_text(
        '[{"en":"apple","zh":"苹果"},{"en":"moon","zh":"月亮"},{"en":"friend","zh":"朋友"}]',
        encoding="utf-8",
    )
    print("seed data ok")


def main() -> None:
    ensure_dirs()
    sync_sprites()
    sync_music()
    sync_voice_sample()
    write_seed_data()
    print("done ->", ROOT / "assets")


if __name__ == "__main__":
    main()
