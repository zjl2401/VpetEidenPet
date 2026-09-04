"""导出伊得使魔艾斯特立绘到 assets/sprites（供 CompanionFollower 使用）。"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT.parent
OUT = ROOT / "app" / "src" / "main" / "assets" / "sprites"

NAMES = ("Aster1.png", "Aster2.png", "Aster3.png", "Aster4.png", "allmateAster.png", "allmateMorvay.png", "allmate.png")

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        for base in (DESKTOP / "assets" / "cutout" / "sprites", DESKTOP / "assets" / "cutout" / "minipet", DESKTOP / "bundled" / "Vpetgame" / "assets"):
            src = base / name.replace(".png", ".jpg") if not (base / name).exists() else base / name
            if not src.exists() and (base / name).exists():
                src = base / name
            if src.exists() or (base / name).exists():
                src = base / name if (base / name).exists() else src
                break
        else:
            src = DESKTOP / "assets" / "cutout" / "sprites" / name
        if not src.is_file():
            print("skip", name)
            continue
        dst = OUT / name
        shutil.copy2(src, dst)
        print("ok", dst.name)

if __name__ == "__main__":
    main()
