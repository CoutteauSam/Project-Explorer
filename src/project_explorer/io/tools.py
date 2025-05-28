import subprocess
import os
import platform
from pathlib import Path

def open_path_in_explorer(path: Path) -> None:

    if not path.exists():
        return

    if os.name in ["nt", "ce"]:
        os.startfile(os.path.normpath(path))
    elif "darwin" in platform.system().casefold():
        subprocess.run(["open", str(path)], check=True)
    else:  # assume Linux or other POSIX-like
        subprocess.run(["xdg-open", str(path)], check=True)
