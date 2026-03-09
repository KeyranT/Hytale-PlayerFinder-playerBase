# Hytale PlayerFinder (playerBase)

PlayerFinder is a lightweight Python tool designed to quickly search for player data inside JSON save files.
It automatically scans all files inside a `playerBase` folder and displays the information related to the searched player.

This tool is particularly useful for server administrators who need to quickly locate and inspect player data.

---

## Features

* Search for a player by name
* Automatically scans all `.json` files in the `playerBase` folder
* Detects players even if their name contains a level tag (example: `ImNotDev - Lvl.1`)
* Displays the file where the player data was found
* Simple interface with a search bar
* Works with large player databases

---

## Expected Structure

```
project-folder
│
├─ playerFinder.py
├─ playerBase
│   ├─ player1.json
│   ├─ player2.json
│   └─ player3.json
```

The `playerBase` folder must contain the JSON files for each player.

---

## Installation

### 1. Clone the repository

```
git clone https://github.com/USERNAME/PlayerFinder.git
cd PlayerFinder
```

### 2. Install Python

Python **3.10 or newer** is recommended.

https://www.python.org/downloads/

---

## Usage

First, download the player data from your Hytale world or server.

The player save files can be found here:

```
hytale/server/universe/players
```

Copy all the JSON files from this folder into the `playerBase` folder of this project.

Example structure:

```
project-folder
│
├─ playerFinder.py
├─ playerBase
│   ├─ player1.json
│   ├─ player2.json
│   └─ player3.json
```

---

Then run the script:

```
python playerFinder.py
```

Then:

1. enter the player name
2. the program scans all JSON files
3. matching player data will be displayed

The search also works if the player name contains a level tag.

Example search:

```
ImNotDev
```

Will also match:

```
ImNotDev - Lvl.1
```

---

## Windows Executable

A **precompiled Windows executable** is already included inside the `dist` folder.

```
dist/playerFinder.exe
```

This version can be used **without installing Python**.

Simply run the `.exe` file and the program will start.

---

## Modifying the Tool

If you want to modify the tool or improve it, you can edit the Python source code (`playerFinder.py`) and recompile it yourself.

Install PyInstaller:

```
pip install pyinstaller
```

Then compile the executable:

```
python -m PyInstaller --onefile --windowed playerFinder.py
```

This will generate a new executable in:

```
dist/playerFinder.exe
```

---

## Technologies Used

* Python
* JSON parsing
* Tkinter (GUI)

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
