#!/usr/bin/env python3
"""把桌面 VpetEiden/sound、voice 同步进工程并转成 wav。

sound → assets/sfx/、bundled/Vpetsound/
voice → bundled/Vpetvoice/Vpet/normal/（文件名即字幕；去「」与重复 (2)）
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from media_bundled import extract_audio_wav, is_supported_media, is_video_container

ROOT = Path(__file__).resolve().parent
DESKTOP_EIDEN = Path.home() / "Desktop" / "VpetEiden"
SRC_SOUND = DESKTOP_EIDEN / "sound"
SRC_VOICE = DESKTOP_EIDEN / "voice"

SFX_DIRS = (ROOT / "assets" / "sfx", ROOT / "bundled" / "Vpetsound")
VOICE_DST = ROOT / "bundled" / "Vpetvoice" / "Vpet" / "normal"

_QUOTE_WRAP = re.compile(r"^[「『\"“]+(.+?)[」』\"”]+$")
_DUP_SUFFIX = re.compile(r"\s*\(\d+\)\s*$")


def _clean_voice_stem(stem: str) -> str:
    text = (stem or "").strip()
    text = _DUP_SUFFIX.sub("", text).strip()
    m = _QUOTE_WRAP.match(text)
    if m:
        text = m.group(1).strip()
    # Windows 非法文件名字符
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    return text[:180] or "voice"


def _iter_media(folder: Path):
    if not folder.is_dir():
        return
    for path in sorted(folder.iterdir()):
        if path.is_file() and is_supported_media(path):
            yield path


def _sync_one(src: Path, dst_wav: Path, *, force: bool = False) -> str:
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    if dst_wav.is_file() and not force:
        try:
            if dst_wav.stat().st_mtime >= src.stat().st_mtime:
                return "skip"
        except Exception:
            pass
    if src.suffix.lower() == ".wav":
        shutil.copy2(src, dst_wav)
        return "copy"
    if extract_audio_wav(src, dst_wav):
        return "convert"
    return "fail"


def sync_sound() -> None:
    files = list(_iter_media(SRC_SOUND))
    if not files:
        print(f"无音效源：{SRC_SOUND}")
        return
    print(f"同步音效 {len(files)} ← {SRC_SOUND}")
    for src in files:
        stem = src.stem.strip()
        for dst_root in SFX_DIRS:
            dst = dst_root / f"{stem}.wav"
            status = _sync_one(src, dst)
            print(f"  [{status}] {dst.relative_to(ROOT)}")


def sync_voice() -> None:
    files = list(_iter_media(SRC_VOICE))
    if not files:
        print(f"无语音源：{SRC_VOICE}")
        return
    VOICE_DST.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    print(f"同步语音 {len(files)} ← {SRC_VOICE}")
    for src in files:
        stem = _clean_voice_stem(src.stem)
        key = stem.lower()
        if key in seen:
            print(f"  [dup-skip] {src.name}")
            continue
        seen.add(key)
        dst = VOICE_DST / f"{stem}.wav"
        status = _sync_one(src, dst)
        print(f"  [{status}] normal/{dst.name[:48]}{'…' if len(dst.name) > 48 else ''}")


def main() -> int:
    sync_sound()
    sync_voice()
    print("完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
