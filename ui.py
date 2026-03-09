import os
import tkinter as tk
from tkinter import filedialog, messagebox

from player_logic import load_json_files_from_folder, search_players


class PlayerSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hytale PlayerFinder")
        self.root.geometry("1300x800")

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.folder_path = ""
        self.player_data = []
        self.filtered_items = []

        self.build_ui()
        self.auto_load_playerbase()

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.folder_label = tk.Label(
            top_frame,
            text="No folder selected",
            anchor="w",
            justify="left"
        )
        self.folder_label.pack(fill="x")

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(
            button_frame,
            text="Select playerBase folder",
            command=self.select_folder
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Reload JSON files",
            command=self.load_json_files
        ).pack(side="left", padx=5)

        search_frame = tk.Frame(self.root)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search player:").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side="left", padx=5)

        self.result_count_label = tk.Label(search_frame, text="0 results")
        self.result_count_label.pack(side="left", padx=10)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="y")

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.result_list = tk.Listbox(left_frame, width=55, height=40)
        self.result_list.pack(side="left", fill="y")
        self.result_list.bind("<<ListboxSelect>>", self.on_select_result)

        list_scroll = tk.Scrollbar(left_frame, command=self.result_list.yview)
        list_scroll.pack(side="left", fill="y")
        self.result_list.config(yscrollcommand=list_scroll.set)

        self.details_text = tk.Text(right_frame, wrap="word")
        self.details_text.pack(side="left", fill="both", expand=True)

        text_scroll = tk.Scrollbar(right_frame, command=self.details_text.yview)
        text_scroll.pack(side="left", fill="y")
        self.details_text.config(yscrollcommand=text_scroll.set)

    def auto_load_playerbase(self):
        default_playerbase = os.path.join(self.base_dir, "playerBase")

        if os.path.isdir(default_playerbase):
            self.folder_path = default_playerbase
            self.folder_label.config(text=f"Selected folder: {default_playerbase}")
            self.load_json_files()

    def select_folder(self):
        folder = filedialog.askdirectory(
            title="Select playerBase folder",
            initialdir=self.base_dir
        )

        if folder:
            self.folder_path = folder
            self.folder_label.config(text=f"Selected folder: {folder}")
            self.load_json_files()

    def load_json_files(self):
        if not self.folder_path:
            messagebox.showwarning("Warning", "Please select a playerBase folder first.")
            return

        self.player_data = []
        self.filtered_items = []
        self.result_list.delete(0, tk.END)
        self.details_text.delete("1.0", tk.END)

        try:
            self.player_data, errors, total_files = load_json_files_from_folder(self.folder_path)
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
            return

        self.update_result_list(self.player_data)

        msg = f"{len(self.player_data)} JSON file(s) loaded out of {total_files}."
        if errors:
            msg += f"\n\n{len(errors)} error(s) detected."

        if errors:
            messagebox.showwarning(
                "Loading completed",
                msg + "\n\nFirst errors:\n" + "\n".join(errors[:10])
            )

    def on_search(self, *args):
        filtered = search_players(self.player_data, self.search_var.get())
        self.update_result_list(filtered)

    def update_result_list(self, items):
        self.result_list.delete(0, tk.END)
        self.filtered_items = items

        for item in items:
            main_name = item.get("display_name") or item.get("nameplate_name") or "Unknown"
            secondary_name = (
                item.get("nameplate_name")
                if item.get("nameplate_name") and item.get("nameplate_name") != main_name
                else ""
            )

            if secondary_name:
                display = f"{main_name} ({secondary_name})  |  {item.get('file_name', 'N/A')}"
            else:
                display = f"{main_name}  |  {item.get('file_name', 'N/A')}"

            self.result_list.insert(tk.END, display)

        count = len(items)
        self.result_count_label.config(text=f"{count} result{'s' if count != 1 else ''}")
        self.details_text.delete("1.0", tk.END)

    def on_select_result(self, event):
        selection = self.result_list.curselection()
        if not selection:
            return

        index = selection[0]
        item = self.filtered_items[index]

        self.details_text.delete("1.0", tk.END)

        lines = []

        lines.append("=== PLAYER IDENTITY ===\n")
        lines.append(f"Display Name: {item.get('display_name', 'N/A') or 'N/A'}")
        lines.append(f"Nameplate: {item.get('nameplate_name', 'N/A') or 'N/A'}")
        lines.append(f"Normalized Name: {item.get('normalized_display', 'N/A') or item.get('normalized_nameplate', 'N/A') or 'N/A'}")
        lines.append(f"Player UUID: {item.get('player_uuid', 'N/A')}")
        lines.append(f"Player Version: {item.get('player_version', 'N/A')}")
        lines.append(f"Game Mode: {item.get('game_mode', 'N/A')}")
        lines.append(f"Block Placement Override: {item.get('block_placement_override', 'N/A')}")
        lines.append(f"File: {item.get('file_name', 'N/A')}")
        lines.append(f"Full Path: {item.get('file_path', 'N/A')}\n")

        lines.append("=== CURRENT TRANSFORM ===")
        pos = item.get("current_position", {}) or {}
        rot = item.get("current_rotation", {}) or {}
        vel = item.get("velocity", {}) or {}
        lines.append(f"Position X: {pos.get('X', 'N/A')}")
        lines.append(f"Position Y: {pos.get('Y', 'N/A')}")
        lines.append(f"Position Z: {pos.get('Z', 'N/A')}")
        lines.append(f"Rotation Pitch: {rot.get('Pitch', 'N/A')}")
        lines.append(f"Rotation Yaw: {rot.get('Yaw', 'N/A')}")
        lines.append(f"Rotation Roll: {rot.get('Roll', 'N/A')}")
        lines.append(f"Velocity X: {vel.get('X', 'N/A')}")
        lines.append(f"Velocity Y: {vel.get('Y', 'N/A')}")
        lines.append(f"Velocity Z: {vel.get('Z', 'N/A')}")
        lines.append("")

        lines.append("=== LAST SAVED POSITION (DEFAULT WORLD) ===")
        last_pos = item.get("last_position", {}) or {}
        if last_pos:
            lines.append(f"X: {last_pos.get('X', 'N/A')}")
            lines.append(f"Y: {last_pos.get('Y', 'N/A')}")
            lines.append(f"Z: {last_pos.get('Z', 'N/A')}")
            lines.append(f"Pitch: {last_pos.get('Pitch', 'N/A')}")
            lines.append(f"Yaw: {last_pos.get('Yaw', 'N/A')}")
            lines.append(f"Roll: {last_pos.get('Roll', 'N/A')}")
        else:
            lines.append("No last position found.")
        lines.append("")

        lines.append("=== PLAYERDATA / WORLD ===")
        lines.append(f"BlockIdVersion: {item.get('block_id_version', 'N/A')}")
        lines.append(f"World: {item.get('world_name', 'N/A')}")
        lines.append(f"Known Recipes Count: {len(item.get('known_recipes', []))}")
        lines.append(f"Discovered Zones Count: {len(item.get('discovered_zones', []))}")
        lines.append(f"Discovered Instances Count: {len(item.get('discovered_instances', []))}")
        lines.append(f"Active Objective UUIDs Count: {len(item.get('active_objective_uuids', []))}")
        lines.append(f"First Spawn (default): {item.get('first_spawn', 'N/A')}")
        lines.append(f"Last Movement States: {item.get('last_movement_states', {})}")
        lines.append("")

        lines.append("=== DEATHS / MARKERS ===")
        lines.append(f"Total deaths: {item.get('death_count', 0)}")
        last_death = item.get("last_death")
        if last_death:
            transform = last_death.get("Transform", {})
            lines.append("Last recorded death:")
            lines.append(f"Day: {last_death.get('Day', 'N/A')}")
            lines.append(f"X: {transform.get('X', 'N/A')}")
            lines.append(f"Y: {transform.get('Y', 'N/A')}")
            lines.append(f"Z: {transform.get('Z', 'N/A')}")
            lines.append(f"MarkerId: {last_death.get('MarkerId', 'N/A')}")
        else:
            lines.append("No deaths recorded.")

        lines.append(f"User Markers Count: {item.get('marker_count', 0)}")
        lines.append("")

        lines.append("=== INVENTORY SUMMARY ===")
        lines.append(f"Inventory Version: {item.get('inventory_version', 'N/A')}")
        lines.append(f"Active Hotbar Slot: {item.get('active_hotbar_slot', 'N/A')}")
        lines.append(f"Active Tools Slot: {item.get('active_tools_slot', 'N/A')}")
        lines.append(f"Active Utility Slot: {item.get('active_utility_slot', 'N/A')}")
        lines.append(f"Sort Type: {item.get('sort_type', 'N/A')}")
        lines.append("")
        lines.append(f"Storage: {item.get('storage_count', 0)} / Capacity {item.get('storage_capacity', 0)}")
        lines.append(f"Armor: {item.get('armor_count', 0)} / Capacity {item.get('armor_capacity', 0)}")
        lines.append(f"HotBar: {item.get('hotbar_count', 0)} / Capacity {item.get('hotbar_capacity', 0)}")
        lines.append(f"Utility: {item.get('utility_count', 0)} / Capacity {item.get('utility_capacity', 0)}")
        lines.append(f"Backpack: {item.get('backpack_count', 0)} / Capacity {item.get('backpack_capacity', 0)}")
        lines.append(f"Tool: {item.get('tool_count', 0)} / Capacity {item.get('tool_capacity', 0)}")
        lines.append("")

        lines.append("=== VANILLA STATS ===")
        lines.append(f"EntityStats Version: {item.get('entity_stats_version', 'N/A')}")
        lines.append(f"Health: {item.get('health', 'N/A')}")
        lines.append(f"Mana: {item.get('mana', 'N/A')}")
        lines.append(f"Stamina: {item.get('stamina', 'N/A')}")
        lines.append(f"Oxygen: {item.get('oxygen', 'N/A')}")
        lines.append(f"Ammo: {item.get('ammo', 'N/A')}")
        lines.append(f"Immunity: {item.get('immunity', 'N/A')}")
        lines.append(f"Signature Charges: {item.get('signature_charges', 'N/A')}")
        lines.append(f"Signature Energy: {item.get('signature_energy', 'N/A')}")
        lines.append(f"Magic Charges: {item.get('magic_charges', 'N/A')}")
        lines.append(f"Gliding Active: {item.get('gliding_active', 'N/A')}")
        lines.append(f"Deployable Preview: {item.get('deployable_preview', 'N/A')}")
        lines.append(f"Stamina Regen Delay: {item.get('stamina_regen_delay', 'N/A')}")
        lines.append(f"Unknown Stat: {item.get('unknown_stat', 'N/A')}")
        lines.append("")

        lines.append("=== PLAYER MEMORIES ===")
        lines.append(f"Capacity: {item.get('player_memories_capacity', 0)}")
        lines.append(f"Stored Memories: {item.get('memory_count', 0)}")
        memories = item.get("player_memories", [])
        if memories:
            for i, memory in enumerate(memories, start=1):
                lines.append(
                    f"{i}. Id={memory.get('Id', 'N/A')} | "
                    f"NPCRole={memory.get('NPCRole', 'N/A')} | "
                    f"TranslationKey={memory.get('TranslationKey', 'N/A')} | "
                    f"FoundLocation={memory.get('FoundLocationNameKey', 'N/A')} | "
                    f"CapturedTimestamp={memory.get('CapturedTimestamp', 'N/A')}"
                )
        else:
            lines.append("No player memories found.")
        lines.append("")

        lines.append("=== HOTBAR MANAGER / UNIQUE USAGES ===")
        lines.append(f"Saved Hotbars Slots: {item.get('saved_hotbars_count', 0)}")
        lines.append(f"Current Hotbar Index: {item.get('current_hotbar_index', 'N/A')}")
        lines.append(f"Unique Item Usage Count: {item.get('unique_item_usage_count', 0)}")
        usages = item.get("unique_item_usages", [])
        if usages:
            for value in usages:
                lines.append(f"- {value}")
        else:
            lines.append("No unique item usages found.")
        lines.append("")

        lines.append("=== INSTANCE / RETURN POINT ===")
        lines.append(f"Return World UUID: {item.get('return_world', 'N/A')}")
        lines.append(f"Return On Reconnect: {item.get('return_on_reconnect', 'N/A')}")
        rp = item.get("return_point", {}) or {}
        if rp:
            lines.append(f"Return X: {rp.get('X', 'N/A')}")
            lines.append(f"Return Y: {rp.get('Y', 'N/A')}")
            lines.append(f"Return Z: {rp.get('Z', 'N/A')}")
            lines.append(f"Return Pitch: {rp.get('Pitch', 'N/A')}")
            lines.append(f"Return Yaw: {rp.get('Yaw', 'N/A')}")
            lines.append(f"Return Roll: {rp.get('Roll', 'N/A')}")
        else:
            lines.append("No return point found.")
        lines.append("")

        lines.append("=== OTHER VANILLA DATA ===")
        lines.append(f"HitboxCollisionConfigIndex: {item.get('hitbox_collision_index', 'N/A')}")
        lines.append(f"SelectionHistory: {item.get('selection_history', 'N/A')}")
        lines.append(f"Head Rotation: {item.get('head_rotation', {})}")
        lines.append(f"ReputationData: {item.get('reputation_data', {})}")
        lines.append("")

        lines.append("=== AUTO-DETECTED EXTRA FIELDS (MODS / UNKNOWN DATA) ===")
        dynamic_fields = item.get("dynamic_fields", [])
        if dynamic_fields:
            for key, value in dynamic_fields[:400]:
                lines.append(f"{key}: {value}")
        else:
            lines.append("No extra unknown fields detected.")

        self.details_text.insert("1.0", "\n".join(lines))