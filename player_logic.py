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
        "level", "lvl", "xp", "experience", "exp", "health", "mana", "stamina",
        "signature", "reputation", "achievement", "zone", "position", "death",
        "combo", "rank", "skill", "stat", "inventory", "armor", "hotbar",
        "tool", "utility", "backpack", "memory", "objective", "instance",
    ]

    results = []
    for key, value in flat_data.items():
        key_lower = key.lower()
        if any(word in key_lower for word in keywords):
            results.append((key, value))
    return results


def safe_stat_value(stats, key):
    return try_get(stats, key, "Value", default="N/A")


def format_uuid(uuid_data):
    if isinstance(uuid_data, dict):
        return uuid_data.get("$binary") or str(uuid_data)
    return uuid_data or "N/A"


# garde les items triés par slot pour l'affichage

def normalize_items(items_dict):
    if not isinstance(items_dict, dict):
        return []

    normalized = []
    for slot, item in items_dict.items():
        if not isinstance(item, dict):
            continue
        normalized.append({
            "slot": str(slot),
            "id": item.get("Id", "N/A"),
            "quantity": item.get("Quantity", 0),
            "durability": item.get("Durability", 0),
            "max_durability": item.get("MaxDurability", 0),
            "raw": item,
        })

    def slot_sort_key(entry):
        try:
            return int(entry["slot"])
        except Exception:
            return 999999

    normalized.sort(key=slot_sort_key)
    return normalized


def extract_player_info(data, file_name, file_path):
    components = data.get("Components", {})

    nameplate_name = try_get(components, "Nameplate", "Text", default="")
    display_name = try_get(components, "DisplayName", "DisplayName", "RawText", default="")

    normalized_nameplate = normalize_player_name(nameplate_name)
    normalized_display = normalize_player_name(display_name)

    current_position = try_get(components, "Transform", "Position", default={}) or {}
    current_rotation = try_get(components, "Transform", "Rotation", default={}) or {}
    velocity = try_get(components, "Velocity", "Velocity", default={}) or {}
    head_rotation = try_get(components, "HeadRotation", "Rotation", default={}) or {}

    player_component = components.get("Player", {}) or {}
    player_data = player_component.get("PlayerData", {}) or {}

    world_name = player_data.get("World", "default") or "default"
    per_world_data = player_data.get("PerWorldData", {}) or {}
    per_world_current = per_world_data.get(world_name, {}) or {}
    per_world_default = per_world_data.get("default", {}) or {}

    last_position = per_world_current.get("LastPosition", {}) or per_world_default.get("LastPosition", {}) or {}
    death_positions = per_world_current.get("DeathPositions", []) or per_world_default.get("DeathPositions", []) or []
    user_markers = per_world_current.get("UserMarkers", []) or per_world_default.get("UserMarkers", []) or []
    last_movement_states = per_world_current.get("LastMovementStates", {}) or per_world_default.get("LastMovementStates", {}) or {}
    first_spawn = per_world_current.get("FirstSpawn")
    if first_spawn is None:
        first_spawn = per_world_default.get("FirstSpawn", "N/A")

    inventory = player_component.get("Inventory", {}) or {}

    storage = inventory.get("Storage", {}) or {}
    armor = inventory.get("Armor", {}) or {}
    hotbar = inventory.get("HotBar", {}) or {}
    utility = inventory.get("Utility", {}) or {}
    backpack = inventory.get("Backpack", {}) or {}
    tool = inventory.get("Tool", {}) or {}

    storage_items = normalize_items(storage.get("Items", {}))
    armor_items = normalize_items(armor.get("Items", {}))
    hotbar_items = normalize_items(hotbar.get("Items", {}))
    utility_items = normalize_items(utility.get("Items", {}))
    backpack_items = normalize_items(backpack.get("Items", {}))
    tool_items = normalize_items(tool.get("Items", {}))

    hotbar_manager = player_component.get("HotbarManager", {}) or {}
    saved_hotbars = hotbar_manager.get("SavedHotbars", []) or []

    entity_stats = components.get("EntityStats", {}) or {}
    stats = entity_stats.get("Stats", {}) or {}

    player_memories_component = components.get("PlayerMemories", {}) or {}
    player_memories = player_memories_component.get("Memories", []) or []

    unique_item_usages_component = components.get("UniqueItemUsages", {}) or {}
    unique_item_usages = unique_item_usages_component.get("UniqueItemUsed", []) or []

    instance_component = components.get("Instance", {}) or {}

    discovered_zones = player_data.get("DiscoveredZones", []) or []
    discovered_instances = player_data.get("DiscoveredInstances", []) or []
    known_recipes = player_data.get("KnownRecipes", []) or []
    active_objective_uuids = player_data.get("ActiveObjectiveUUIDs", []) or []
    reputation_data = player_data.get("ReputationData", {}) or {}

    death_positions_simple = []
    for death in death_positions:
        if not isinstance(death, dict):
            continue
        transform = death.get("Transform", {}) or {}
        death_positions_simple.append({
            "day": death.get("Day", "N/A"),
            "marker_id": death.get("MarkerId", "N/A"),
            "x": transform.get("X", "N/A"),
            "y": transform.get("Y", "N/A"),
            "z": transform.get("Z", "N/A"),
            "pitch": transform.get("Pitch", "N/A"),
            "yaw": transform.get("Yaw", "N/A"),
            "roll": transform.get("Roll", "N/A"),
            "raw": death,
        })

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
            str(file_name),
        ]).lower(),
        "player_uuid": format_uuid(player_component.get("UUID") or try_get(components, "UUID", "UUID", default="N/A")),
        "player_version": player_component.get("Version", "N/A"),
        "game_mode": player_component.get("GameMode", "N/A"),
        "block_placement_override": player_component.get("BlockPlacementOverride", "N/A"),
        "current_position": current_position,
        "current_rotation": current_rotation,
        "velocity": velocity,
        "head_rotation": head_rotation,
        "block_id_version": player_data.get("BlockIdVersion", "N/A"),
        "world_name": world_name,
        "known_recipes": known_recipes,
        "discovered_zones": discovered_zones,
        "discovered_instances": discovered_instances,
        "active_objective_uuids": active_objective_uuids,
        "first_spawn": first_spawn,
        "last_movement_states": last_movement_states,
        "last_position": last_position,
        "death_positions": death_positions_simple,
        "last_death": death_positions[-1] if death_positions else None,
        "death_count": len(death_positions_simple),
        "marker_count": len(user_markers),
        "inventory_version": inventory.get("Version", "N/A"),
        "active_hotbar_slot": inventory.get("ActiveHotbarSlot", "N/A"),
        "active_tools_slot": inventory.get("ActiveToolsSlot", "N/A"),
        "active_utility_slot": inventory.get("ActiveUtilitySlot", "N/A"),
        "sort_type": inventory.get("SortType", "N/A"),
        "storage_capacity": storage.get("Capacity", 0),
        "armor_capacity": armor.get("Capacity", 0),
        "hotbar_capacity": hotbar.get("Capacity", 0),
        "utility_capacity": utility.get("Capacity", 0),
        "backpack_capacity": backpack.get("Capacity", 0),
        "tool_capacity": tool.get("Capacity", 0),
        "storage_items": storage_items,
        "armor_items": armor_items,
        "hotbar_items": hotbar_items,
        "utility_items": utility_items,
        "backpack_items": backpack_items,
        "tool_items": tool_items,
        "storage_count": len(storage_items),
        "armor_count": len(armor_items),
        "hotbar_count": len(hotbar_items),
        "utility_count": len(utility_items),
        "backpack_count": len(backpack_items),
        "tool_count": len(tool_items),
        "entity_stats_version": entity_stats.get("Version", "N/A"),
        "health": safe_stat_value(stats, "Health"),
        "mana": safe_stat_value(stats, "Mana"),
        "stamina": safe_stat_value(stats, "Stamina"),
        "oxygen": safe_stat_value(stats, "Oxygen"),
        "ammo": safe_stat_value(stats, "Ammo"),
        "immunity": safe_stat_value(stats, "Immunity"),
        "signature_charges": safe_stat_value(stats, "SignatureCharges"),
        "signature_energy": safe_stat_value(stats, "SignatureEnergy"),
        "magic_charges": safe_stat_value(stats, "MagicCharges"),
        "gliding_active": safe_stat_value(stats, "GlidingActive"),
        "deployable_preview": safe_stat_value(stats, "DeployablePreview"),
        "stamina_regen_delay": safe_stat_value(stats, "StaminaRegenDelay"),
        "unknown_stat": safe_stat_value(stats, "Unknown"),
        "player_memories_capacity": player_memories_component.get("Capacity", 0),
        "player_memories": player_memories,
        "memory_count": len(player_memories),
        "saved_hotbars_count": len([x for x in saved_hotbars if x]),
        "current_hotbar_index": hotbar_manager.get("CurrentHotbar", "N/A"),
        "unique_item_usages": unique_item_usages,
        "unique_item_usage_count": len(unique_item_usages),
        "return_world": instance_component.get("ReturnWorldUUID", "N/A"),
        "return_on_reconnect": instance_component.get("ReturnOnReconnect", "N/A"),
        "return_point": instance_component.get("ReturnPosition", {}) or {},
        "hitbox_collision_index": try_get(components, "HitboxCollision", "HitboxCollisionConfigIndex", default="N/A"),
        "selection_history": try_get(components, "BuilderTools", "SelectionHistory", default="N/A"),
        "reputation_data": reputation_data,
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
