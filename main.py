#!/usr/bin/env python3
"""
Definition-file template
────────────────────────
WINDOWS
windows: C:/Users/<User>/AppData/Local/<Game>/
linux:   D:/ProtonPrefixes/<Game>/pfx/drive_c/users/<User>/AppData/Local/<Game>/

LINUX
windows: /run/media/<User>/<UUID>/Users/<User>/AppData/Local/<Game>/
linux:   /home/<user>/.local/share/<Game>/
"""

from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# User settings
GAMES_DIR = Path(__file__).with_name("Games")      # where the *.txt files live
TRASH_DIR = Path(__file__).with_name("Trash")      # overwritten data is backed up here
DT_FORMAT = "%Y-%m-%d  %I:%M %p"                   # 12-hour clock with AM/PM
NEWEST_TAG = "  (latest)"                        # marker for the fresher save

class DefinitionError(RuntimeError):
    """Raised when a game definition file is malformed."""


# Parse the definition file
def parse_definition(f: Path) -> Dict[str, Dict[str, str]]:
    sections, keys = {"WINDOWS", "LINUX"}, {"windows", "linux"}
    data: Dict[str, Dict[str, str]] = {s: {} for s in sections}
    current = None

    for raw in f.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        up = line.upper()
        if up in sections:
            current = up
            continue
        if current is None or ":" not in line:
            raise DefinitionError(f"{f.name}: malformed line → {line!r}")
        key, val = map(str.strip, line.split(":", 1))
        key = key.lower()
        if key not in keys:
            raise DefinitionError(f"{f.name}: unknown sub-key {key!r}")
        data[current][key] = val

    for s in sections:
        if set(data[s]) != keys:
            raise DefinitionError(
                f"{f.name}: section [{s}] must contain both 'windows:' and 'linux:'"
            )
    return data


# Menu helper
def choose(prompt: str, options: Tuple[str, ...]) -> int:
    for i, opt in enumerate(options, 1):
        print(f"{i}: {opt}")
    while True:
        ans = input(prompt).strip()
        if ans.isdigit() and 1 <= int(ans) <= len(options):
            return int(ans) - 1
        print("  » Enter the number in front of your choice.")


# Filesystem helpers
def backup(dst: Path, game: str) -> None:
    if not dst.exists():
        return
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dest = TRASH_DIR / stamp / game
    dest.mkdir(parents=True, exist_ok=True)
    shutil.move(str(dst), dest / dst.name)
    print(f"🔄 Previous data moved to {dest}")


def copy(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def latest_mtime(path: Path) -> Optional[datetime]:
    """Return newest modification time inside *path* (recursive)."""
    try:
        if not path.exists():
            return None
        if path.is_file():
            return datetime.fromtimestamp(path.stat().st_mtime)

        newest = datetime.fromtimestamp(path.stat().st_mtime)
        for p in path.rglob("*"):
            try:
                t = datetime.fromtimestamp(p.stat().st_mtime)
                if t > newest:
                    newest = t
            except FileNotFoundError:
                continue
        return newest
    except Exception:
        return None


def fmt_time(t: Optional[datetime], newest: bool) -> str:
    if t is None:
        return "N/A"
    # strip leading zero from hour (cosmetic)
    stamp = t.strftime(DT_FORMAT).lstrip("0")
    return stamp + (NEWEST_TAG if newest else "")


# Core sync logic
def perform(
    defs: Dict[str, Dict[str, str]], current_os: str, direction: str, game: str
) -> None:
    section = current_os.upper()  # WINDOWS or LINUX
    src_key, dst_key = (
        ("windows", "linux") if direction == "windows→linux" else ("linux", "windows")
    )

    src = Path(defs[section][src_key])
    dst = Path(defs[section][dst_key])

    print("\n=== SYNC SUMMARY ==================================================")
    print(f"  Game      : {game}")
    print(f"  Direction : {direction}")
    print(f"  Source    : {src}")
    print(f"  Target    : {dst}")
    print("===================================================================")

    if not src.exists():
        print("❌  Source path does not exist – aborting.")
        return

    backup(dst, game)
    try:
        copy(src, dst)
    except Exception as e:  # noqa: BLE001
        print(f"❌  Copy failed: {e}")
    else:
        print("✅  Sync complete.")


# Main entry point
def main() -> None:
    if not GAMES_DIR.is_dir():
        sys.exit(f"Definitions folder {GAMES_DIR} not found.")
    files = tuple(sorted(GAMES_DIR.glob("*.txt")))
    if not files:
        sys.exit(f"No *.txt files in {GAMES_DIR}")

    i = choose("\nSelect a game: ", tuple(p.stem for p in files))
    game_file = files[i]
    game_name = game_file.stem

    try:
        defs = parse_definition(game_file)
    except DefinitionError as e:
        sys.exit(f"Definition error → {e}")

    os_guess = "windows" if os.name == "nt" else "linux"
    print(f"\nDetected OS: {os_guess.upper()}")
    override = input("Press Enter or type 'windows'/'linux' to override: ").strip().lower()
    if override in {"windows", "linux"}:
        os_guess = override

    # Show timestamps once
    section = os_guess.upper()
    w_path = Path(defs[section]["windows"])
    l_path = Path(defs[section]["linux"])

    w_time = latest_mtime(w_path)
    l_time = latest_mtime(l_path)

    newer_is_win = (w_time and l_time and w_time > l_time) or (w_time and not l_time)
    newer_is_lin = (l_time and w_time and l_time > w_time) or (l_time and not w_time)

    print("\nSave timestamps")
    print(f"   Windows save : {fmt_time(w_time, newer_is_win)}")
    print(f"   Linux  save  : {fmt_time(l_time, newer_is_lin)}\n")

    # Simple direction menu
    d = choose(
        "Choose sync direction: ",
        ("windows→linux  (copy Windows save into Linux slot)",
         "linux→windows  (copy Linux save into Windows slot)")
    )
    direction = "windows→linux" if d == 0 else "linux→windows"
    perform(defs, os_guess, direction, game_name)


if __name__ == "__main__":
    try:
        TRASH_DIR.mkdir(exist_ok=True)
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
