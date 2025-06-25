# Save-Syncer

> Effortlessly sync your game save files between Windows and Linux for dual-boot setups.

**Save-Syncer** is a command-line Python tool designed for gamers who dual-boot Windows and Linux but want to keep game saves perfectly in sync—no more manual copying, no more risk of overwriting your progress.  
Works with both single files and entire folders, safely backs up overwritten data, and highlights which save is newer before syncing.

---

## Features

- **Two-way Sync:** Copy Windows saves to Linux, or Linux saves to Windows.
- **Smart Timestamp Comparison:** Shows last modified times for each save (including all files inside save directories).
- **Automatic Backups:** Previous saves are never lost—backed up before each sync.
- **Supports Any Game:** Flexible, user-editable config format—works for both file and folder saves.
- **Safe, Simple, Transparent:** No cloud, no third-party accounts, no hidden behaviour.

---

## Usage Example

```plaintext
1: Sifu
Select a game: 1

Detected OS: LINUX
Press Enter or type 'windows'/'linux' to override:

Save timestamps
   Windows save : 2025-06-20  11:02 PM  <-- latest
   Linux  save  : 2025-06-20  10:12 PM

1: windows→linux  (copy Windows save into Linux slot)
2: linux→windows  (copy Linux save into Windows slot)
Choose sync direction: 1

=== SYNC SUMMARY ==================================================
  Game      : Sifu
  Direction : windows→linux
  Source    : /mnt/shared/W/Sifu/
  Target    : /home/sushi/.local/share/Sifu/
===================================================================
:arrows_counterclockwise: Previous data moved to Trash/2025-06-20_23-08-31/Sifu
:white_check_mark:  Sync complete.
````

---

## Setup

### 1. Requirements

* Python 3.7 or newer (standard library only, no external dependencies)
* Works on Windows, Linux, or WSL
* yt_dlp library

### 2. Installation

1. **Clone the repo:**

   ```bash
   git clone https://github.com/yourusername/Save-Syncer.git
   cd Save-Syncer
   ```

2. **Organize your files:**

   * Place `main.py` in the root of the repo (or wherever you like).
   * Create a folder named `Games/` (case-sensitive!).
   * For each game, create a `.txt` file in `Games/` describing the Windows and Linux save paths (see below).

3. **Optional:** Add `Save-Syncer` to your `$PATH` or create a desktop shortcut for fast launching.

### 3. Game Save Definition Files

Each `.txt` file in `Games/` must follow this format:

```ini
WINDOWS
windows: C:/Users/<User>/AppData/Local/<Game>/
linux:   D:/ProtonPrefixes/<Game>/pfx/drive_c/users/<User>/AppData/Local/<Game>/

LINUX
windows: /run/media/<User>/<UUID>/Users/<User>/AppData/Local/<Game>/
linux:   /home/<user>/.local/share/<Game>/
```

**How it works:**

* The `WINDOWS` section: These are paths you would use while running Windows.
* The `LINUX` section: These are paths you would use while running Linux.
* Under each heading, `windows:` is the path to the Windows save, and `linux:` is the path to the Linux save, both in the style and mount format of the current OS.

> :bulb: *You can use full paths to folders or files. The script copies everything inside if you provide a folder.*

---

## How It Works

* Launch the script in a terminal:

  ```bash
  python3 main.py
  ```
* Pick your game from the list.
* The script shows which save was modified most recently, so you know which direction to sync.
* Select the sync direction.
* The script moves the current target save to a time-stamped `Trash/` backup and replaces it with the chosen source.

---

## Safety Notes

* **Backups:** Before any overwrite, the old save is moved to `Trash/` inside the project folder with a timestamp and game name. Nothing is deleted until you delete it yourself.
* **No Cloud:** All syncs are local, fast, and private.

---

## Contributing

PRs are welcome! If you find a bug, want to add features, or improve the UI, open an issue or submit a pull request.