import os
import json
from player_logic import extract_player_info, normalize_player_name

def load_all_players(folder_path):
    players = []
    errors = []
    if not os.path.exists(folder_path):
        return [], ["Folder not found"], 0
        
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    for file_name in files:
        path = os.path.join(folder_path, file_name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                players.append(extract_player_info(data, file_name, path))
        except Exception as e:
            errors.append(f"{file_name}: {str(e)}")
            
    players.sort(key=lambda x: (x["display_name"] or x["file_name"]).lower())
    return players, errors, len(files)

def filter_players(player_list, query):
    query = normalize_player_name(query)
    if not query:
        return player_list
    return [p for p in player_list if query in p["search_text"]]