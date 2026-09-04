"""兼容旧入口：转发到 sync_eiden_voices.py。"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("sync_eiden_voices.py")), run_name="__main__")
