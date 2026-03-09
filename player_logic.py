import os
import json
import re


def normalize_player_name(name):
    if not name:
        return ""

    name = str(name).strip().lower()
    name = re.sub(r"\s*-\s*(lvl|level)\.?\s*\d+\s*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def flatten_json(data, parent_key="", sep="."):
    items = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else str(key)
            items.extend(flatten_json(value, new_key, sep=sep).items())

    elif isinstance(data, list):
        for index, value in enumerate(data):
            new_key = f"{parent_key}[{index}]"
            items.extend(flatten_json(value, new_key, sep=sep).items())

    else:
        items.append((parent_key, data))

    return dict(items)


def try_get(data, *path, default=None):
    current = data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def extract_dynamic_interesting_fields(flat_data):
    keywords = [
        "level",
        "lvl",
        "xp",
        "experience",
        "exp",
        "health",
        "mana",
        "stamina",
        "signature",
        "reputation",
        "achievement",
        "zone",
        "position",
        "death",
        "combo",
        "rank",
        "skill",
        "stat",
    ]

    results = []
    for key, value in flat_data.items():
        key_lower = key.lower()
        if any(word in key_lower for word in keywords):
            results.append((key, value))

    return results


def extract_player_info(data, file_name, file_path):
    components = data.get("Components", {})

    nameplate_name = try_get(components, "Nameplate", "Text", default="")
    display_name = try_get(components, "DisplayName", "DisplayName", "RawText", default="")

    normalized_nameplate = normalize_player_name(nameplate_name)
    normalized_display = normalize_player_name(display_name)

    current_position = try_get(components, "Transform", "Position", default={})

    player_component = components.get("Player", {})
    player_data = player_component.get("PlayerData", {})
    per_world_default = try_get(player_data, "PerWorldData", "default", default={}) or {}

    last_position = per_world_default.get("LastPosition", {})
    death_positions = per_world_default.get("DeathPositions", []) or []
    user_markers = per_world_default.get("UserMarkers", []) or []

    last_death = death_positions[-1] if death_positions else None

    inventory = player_component.get("Inventory", {})
    storage_items = try_get(inventory, "Storage", "Items", default={}) or {}
    hotbar_items = try_get(inventory, "HotBar", "Items", default={}) or {}
    armor_items = try_get(inventory, "Armor", "Items", default={}) or {}
    utility_items = try_get(inventory, "Utility", "Items", default={}) or {}
    backpack_items = try_get(inventory, "Backpack", "Items", default={}) or {}

    discovered_zones = player_data.get("DiscoveredZones", []) or []

    flat_data = flatten_json(data)
    dynamic_fields = extract_dynamic_interesting_fields(flat_data)

    return {
        "file_name": file_name,
        "file_path": file_path,
        "nameplate_name": nameplate_name,
        "display_name": display_name,
        "normalized_nameplate": normalized_nameplate,
        "normalized_display": normalized_display,
        "search_text": " ".join([
            str(nameplate_name),
            str(display_name),
            str(normalized_nameplate),
            str(normalized_display),
            str(file_name)
        ]).lower(),
        "current_position": current_position,
        "last_position": last_position,
        "last_death": last_death,
        "death_count": len(death_positions),
        "storage_count": len(storage_items),
        "hotbar_count": len(hotbar_items),
        "armor_count": len(armor_items),
        "utility_count": len(utility_items),
        "backpack_count": len(backpack_items),
        "marker_count": len(user_markers),
        "zone_count": len(discovered_zones),
        "dynamic_fields": dynamic_fields,
        "flat_data": flat_data,
        "raw_data": data,
    }


def load_json_files_from_folder(folder_path):
    player_data = []
    errors = []
    total_files = 0

    try:
        file_names = os.listdir(folder_path)
    except Exception as e:
        raise RuntimeError(f"Unable to read folder: {e}") from e

    for file_name in file_names:
        if not file_name.lower().endswith(".json"):
            continue

        total_files += 1
        file_path = os.path.join(folder_path, file_name)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            extracted = extract_player_info(data, file_name, file_path)
            player_data.append(extracted)

        except Exception as e:
            errors.append(f"{file_name}: {e}")

    player_data.sort(key=lambda x: (x["display_name"] or x["nameplate_name"] or x["file_name"]).lower())
    return player_data, errors, total_files


def search_players(player_data, query_raw):
    query = normalize_player_name(query_raw)

    if not query:
        return player_data

    filtered = []
    for player in player_data:
        if (
            query in player["normalized_nameplate"]
            or query in player["normalized_display"]
            or query in player["search_text"]
        ):
            filtered.append(player)

    return filtered