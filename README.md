# Hytale-PlayerFinder-playerBase

PlayerFinder est un petit outil Python permettant de rechercher rapidement un joueur dans un dossier contenant des fichiers JSON de sauvegarde.
Il est conçu pour analyser automatiquement tous les fichiers dans un dossier `playerBase` et afficher les informations du joueur correspondant.

L'outil est particulièrement utile pour les administrateurs de serveur qui doivent retrouver rapidement les données d'un joueur.

---

## Fonctionnalités

* Recherche d'un joueur par nom
* Analyse automatique de tous les fichiers `.json`
* Détection du joueur même si le nom contient un niveau (ex: `Tubblemaker - Lvl.1`)
* Affichage du fichier où le joueur a été trouvé
* Interface simple avec barre de recherche
* Compatible avec de grandes bases de joueurs

---

## Structure attendue

```
project-folder
│
├─ playerFinder.py
├─ playerBase
│   ├─ player1.json
│   ├─ player2.json
│   └─ player3.json
```

Le dossier `playerBase` doit contenir tous les fichiers JSON des joueurs.

---

## Installation

### 1. Cloner le projet

```
git clone https://github.com/USERNAME/PlayerFinder.git
cd PlayerFinder
```

### 2. Installer Python

Python 3.10 ou plus récent est recommandé.

https://www.python.org/downloads/

---

## Utilisation

Lancer simplement le script :

```
python playerFinder.py
```

Ensuite :

1. entrer le nom du joueur
2. le programme recherche dans tous les fichiers JSON
3. les informations trouvées sont affichées

La recherche fonctionne même si le nom contient un niveau :

```
Tubblemaker
```

va aussi trouver :

```
Tubblemaker - Lvl.1
```

---

## Création d'un exécutable (.exe)

Pour créer un fichier portable :

Installer PyInstaller :

```
pip install pyinstaller
```

Compiler :

```
python -m PyInstaller --onefile --windowed playerFinder.py
```

Le fichier sera généré ici :

```
dist/playerFinder.exe
```

---

## Technologies utilisées

* Python
* JSON parsing
* Tkinter (interface)

---

## Contribution

Les contributions sont les bienvenues.

1. Fork le projet
2. Crée une branche
3. Fais tes modifications
4. Ouvre une Pull Request

---

## Licence

Projet open source libre d'utilisation.

