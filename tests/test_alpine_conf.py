import os
import subprocess
from pathlib import Path

import pytest

SCRIPTS = ["setup-apkcache", "setup-interfaces"]


@pytest.mark.parametrize("script", SCRIPTS)
def test_alpine_conf_scripts(script):
    repo_root = Path(__file__).resolve().parents[1]
    build_dir = repo_root / "for-codex-alpine-conf"
    script_path = build_dir / script
    lib_path = build_dir / "libalpine.sh"
    if not script_path.exists() or not lib_path.exists():
        pytest.skip("alpine-conf build artifacts missing")
    env = os.environ.copy()
    env["LIBDIR"] = str(build_dir)
    subprocess.check_call([str(script_path), "-h"], env=env)
