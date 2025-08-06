import subprocess
from pathlib import Path

def test_build_custom_apk():
    script = Path(__file__).resolve().parents[1] / "build" / "build_apk_tools.sh"
    apk_path = subprocess.check_output([str(script)]).decode().strip()
    assert Path(apk_path).is_file()
    subprocess.check_call([apk_path, "--version"])
