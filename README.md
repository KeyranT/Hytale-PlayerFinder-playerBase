# Hytale PlayerFinder (playerBase)

PlayerFinder is a lightweight Python tool designed to quickly search and inspect player data inside Hytale JSON save files.

It automatically scans all files inside a `playerBase` folder, lets you search players by name, and displays both detailed vanilla data and automatically detected extra fields from unknown or modded JSON structures.

This tool is especially useful for server administrators who need to quickly locate, review, and inspect player save data.

---

## Features

- Search for a player by name
- Automatically scans all `.json` files in the `playerBase` folder
- Detects players even if their name contains a level tag  
  Example: `ImNotDev - Lvl.1`
- Displays the file where the player data was found
- Loads the local `playerBase` folder automatically if it exists next to the script
- Detailed hardcoded vanilla Hytale player data display
- Automatically detects and displays extra unknown fields from mods or custom data
- Simple interface with a search bar
- Works with large player databases

---

## Project Structure

```text
project-folder
│
├─ main.py
├─ ui.py
├─ player_logic.py
├─ playerBase
│   ├─ player1.json
│   ├─ player2.json
│   └─ player3.json
```

The `playerBase` folder must contain the JSON files for each player.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/USERNAME/Hytale-PlayerFinder-playerBase.git
cd Hytale-PlayerFinder-playerBase
```

### 2. Install Python

Python **3.10 or newer** is recommended.

You can download Python here:

```text
https://www.python.org/downloads/
```

No external libraries are required.  
This project uses only Python standard libraries:

- `os`
- `json`
- `re`
- `tkinter`

---

## Usage

First, download the player data from your Hytale world or server.

The player save files can usually be found here:

```text
hytale/server/universe/players
```

Copy all the JSON files from this folder into the `playerBase` folder of this project.

Example:

```text
project-folder
│
├─ main.py
├─ ui.py
├─ player_logic.py
├─ playerBase
│   ├─ player1.json
│   ├─ player2.json
│   └─ player3.json
```

---

Then run the application with:

```bash
python main.py
```

Then:

1. enter the player name
2. the program scans all loaded JSON files
3. matching player data will be displayed in the interface

The search also works if the player name contains a level tag.

Example search:

```text
ImNotDev
```

Will also match:

```text
ImNotDev - Lvl.1
```

---

## What the Tool Displays

PlayerFinder is designed to show:

### Hardcoded vanilla Hytale data
- display name
- nameplate
- UUID
- player version
- game mode
- position and rotation
- last saved position
- deaths
- world data
- discovered zones
- inventory summary
- stats such as health, mana, stamina, oxygen, and more
- player memories
- hotbar manager data
- unique item usages
- return point / instance data

### Automatically detected extra fields
Any additional unknown JSON fields that are not part of the hardcoded vanilla structure are displayed automatically at the bottom of the details panel.

This is useful for:
- modded servers
- custom save structures
- unknown JSON additions
- admin-side inspection of unexpected values

---

## Automatic Folder Loading

If a folder named `playerBase` exists in the same directory as the project files, the tool will automatically load it at startup.

This means you can often just place your JSON files in:

```text
playerBase/
```

and run:

```bash
python main.py
```

without selecting the folder manually.

---

## Windows Executable

A **precompiled Windows executable** is already included inside the `dist` folder.

```text
dist/playerFinder.exe
```

This version can be used **without installing Python**.

Simply run the `.exe` file and the program will start.

---

## Modifying the Tool

If you want to modify or improve the tool, you can edit the source files:

- `main.py`
- `ui.py`
- `player_logic.py`

---

## Build the Executable Yourself

Install PyInstaller:

```bash
pip install pyinstaller
```

Then compile the executable:

```bash
python -m PyInstaller --onefile --windowed main.py
```

This will generate a new executable in:

```text
dist/main.exe
```

If you want the executable to keep the `playerFinder.exe` name, use:

```bash
python -m PyInstaller --onefile --windowed --name playerFinder main.py
```

This will generate:

```text
dist/playerFinder.exe
```

---

## Technologies Used

- Python
- JSON parsing
- Tkinter (GUI)

---

## Contribution

Contributions are welcome.

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a Pull Request

---

## License

This project is open-source and free to use.
