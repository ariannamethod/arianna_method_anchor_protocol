import subprocess
from pathlib import Path


def test_build_custom_apk():
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "build" / "build_apk_tools.sh"
    subprocess.check_call([str(script)])
    apk_path = repo_root / "for-codex-alpine-apk-tools" / "src" / "apk"
    assert apk_path.is_file()
    subprocess.check_call([str(apk_path), "--version"])
