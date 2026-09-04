"""把伊得语音同步进手机 assets（并回写电脑版 bundled/Vpetvoice）。

来源优先级：
  1. 工程 bundled/Vpetvoice（已是 wav/mp3 的分类目录）
  2. 桌面 VpetEiden/voice（可含 mp4，会抽音转 wav）

手机版会清空苍叶遗留的 Vpet/Allmate/chain，再写入伊得资源。
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

MOBILE_ROOT = Path(__file__).resolve().parents[1]
REPO = MOBILE_ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from media_bundled import (  # noqa: E402
    AUDIO_MEDIA_EXTENSIONS,
    extract_audio_wav,
    is_audio_media,
    is_video_container,
)

DESKTOP_VOICE = Path.home() / "Desktop" / "VpetEiden" / "voice"
BUNDLED_VOICE = REPO / "bundled" / "Vpetvoice"
MOBILE_VOICE = MOBILE_ROOT / "app" / "src" / "main" / "assets" / "voice"

KNOWN_CATS = {
    "normal", "call", "eat", "walk", "work", "sleep", "dizzy", "game",
    "hurt", "hungry", "error", "end", "hi", "kick", "yuqi", "forget",
    "email", "interjection", "你好",
}
PREFIX_RE = re.compile(r"^((?:\d+)|(?:[a-zA-Z]))(?:[\s._\-]+)(.+)$")
SAFE_CHARS = re.compile(r'[\\/:*?"<>|?!]')


def classify_flat(stem: str) -> str:
    t = stem
    if any(k in t for k in ("晕", "耳边", "眼前")):
        return "dizzy"
    if any(k in t for k in ("梦中", "睡觉", "该睡")):
        return "sleep"
    if any(k in t for k in ("工作", "劳动", "祭坛", "过劳")):
        return "work"
    if any(k in t for k in ("饿", "能量产品", "维持身材")):
        return "hungry"
    if any(k in t for k in ("医院", "头", "摸我")):
        if "摸" in t:
            return "yuqi"
        return "hurt"
    if any(k in t for k in ("无视", "存在")):
        return "yuqi"
    return "normal"


def safe_stem(name: str) -> str:
    stem = Path(name).stem
    stem = stem.replace("（2）", "").replace("(2)", "").strip()
    stem = stem.strip("「」\"' ")
    stem = SAFE_CHARS.sub("", stem)
    stem = re.sub(r"\s+", " ", stem).strip(" .")
    if len(stem) > 72:
        stem = stem[:72].rstrip()
    return stem or "clip"


def iter_media(root: Path):
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if is_audio_media(path) or is_video_container(path):
            yield path


def relative_category(path: Path, root: Path) -> str | None:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 3 and parts[0].lower() == "vpet" and parts[1] in KNOWN_CATS:
        return parts[1]
    if len(parts) >= 2 and parts[0] in KNOWN_CATS:
        return parts[0]
    return None


def source_bucket(path: Path, root: Path) -> str:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return "vpet"
    top = rel.parts[0].lower() if rel.parts else ""
    if top == "allmate":
        return "allmate"
    if top == "laimu":
        return "laimu"
    return "vpet"


def collect_sources() -> list[tuple[str, str, Path]]:
    """(bucket, category, src_path)"""
    items: list[tuple[str, str, Path]] = []
    seen: set[str] = set()

    def add(bucket: str, category: str, src: Path) -> None:
        key = safe_stem(src.name).casefold()
        if key in seen:
            return
        seen.add(key)
        items.append((bucket, category, src))

    for root in (BUNDLED_VOICE, DESKTOP_VOICE):
        if not root.is_dir():
            continue
        for src in iter_media(root):
            if src.name.lower() == "readme.txt":
                continue
            bucket = source_bucket(src, root)
            cat = relative_category(src, root)
            if bucket == "vpet" and not cat:
                cat = classify_flat(src.stem)
            if bucket != "vpet":
                cat = cat or "misc"
            add(bucket, cat, src)
    return items


def materialize(src: Path, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if is_video_container(src) or src.suffix.lower() != ".wav":
        return extract_audio_wav(src, dest)
    dest.write_bytes(src.read_bytes())
    return dest.is_file()


def replace_tree(dst: Path, keep_names: set[str]) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in list(dst.iterdir()):
        if child.name.lower() in keep_names:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def write_chain_index(mobile_root: Path) -> None:
    index = {"vpet": {}, "allmate": {}}
    chain_dir = mobile_root / "chain"
    chain_dir.mkdir(parents=True, exist_ok=True)

    def harvest(src_root: Path, source: str, dest_prefix: str) -> None:
        if not src_root.is_dir():
            return
        files = sorted(src_root.rglob("*.wav")) if source == "vpet" else sorted(src_root.glob("*.wav"))
        for f in files:
            m = PREFIX_RE.match(f.stem)
            if not m:
                continue
            raw = m.group(1)
            key = raw.lower() if raw.isalpha() else raw
            if key in index[source]:
                continue
            kind = "digit" if key.isdigit() else "letter"
            name = f"{dest_prefix}_{kind}_{key}.wav"
            shutil.copy2(f, chain_dir / name)
            index[source][key] = f"voice/chain/{name}"

    harvest(mobile_root / "Vpet", "vpet", "vpet")
    harvest(mobile_root / "Allmate", "allmate", "allmate")
    (mobile_root / "chain_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    clips = collect_sources()
    if not clips:
        print("未找到伊得语音。请把 wav/mp3（或带音轨的 mp4）放到：")
        print(f"  {DESKTOP_VOICE}")
        print("或按场景分类放到：")
        print(f"  {BUNDLED_VOICE / 'Vpet'}")
        return 1

    staging = MOBILE_ROOT / "build" / "_voice_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)

    ok = 0
    fail = 0
    for bucket, category, src in clips:
        if not src.is_file():
            print("MISSING", src)
            fail += 1
            continue
        stem = safe_stem(src.name)
        if bucket == "vpet":
            rel = Path("Vpet") / category / f"{stem}.wav"
        elif bucket == "allmate":
            rel = Path("Allmate") / f"{stem}.wav"
        else:
            rel = Path(bucket) / f"{stem}.wav"
        print(f"convert {src.name} -> {rel}")
        if not materialize(src, staging / rel):
            print("FAIL", src)
            fail += 1
            continue
        ok += 1

    replace_tree(BUNDLED_VOICE, {"readme.txt"})
    replace_tree(MOBILE_VOICE, set())
    for wav in staging.rglob("*.wav"):
        rel = wav.relative_to(staging)
        for root in (BUNDLED_VOICE, MOBILE_VOICE):
            out = root / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(wav.read_bytes())

    write_chain_index(MOBILE_VOICE)
    shutil.rmtree(staging, ignore_errors=True)
    print(f"done: {ok} clips, {fail} failed")
    print(f"mobile -> {MOBILE_VOICE}")
    print(f"desktop bundled -> {BUNDLED_VOICE}")
    return 0 if fail == 0 and ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
