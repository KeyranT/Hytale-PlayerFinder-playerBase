import os
import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox


def normalize_player_name(name):
    if not name:
        return ""

    name = str(name).strip().lower()

    # Retire les suffixes du style :
    # " - Lvl.1"
    # " - lvl 25"
    # " - Level 10"
    name = re.sub(r"\s*-\s*(lvl|level)\.?\s*\d+\s*$", "", name, flags=re.IGNORECASE)

    # Retire les espaces multiples
    name = re.sub(r"\s+", " ", name).strip()

    return name


class PlayerSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recherche joueurs JSON - playerBase")
        self.root.geometry("1100x700")

        self.folder_path = ""
        self.player_data = []
        self.filtered_items = []

        self.build_ui()

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.folder_label = tk.Label(
            top_frame,
            text="Aucun dossier sélectionné",
            anchor="w",
            justify="left"
        )
        self.folder_label.pack(fill="x")

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(
            button_frame,
            text="Choisir le dossier playerBase",
            command=self.select_folder
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Recharger les JSON",
            command=self.load_json_files
        ).pack(side="left", padx=5)

        search_frame = tk.Frame(self.root)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Rechercher un joueur :").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side="left", padx=5)

        self.result_count_label = tk.Label(search_frame, text="0 résultat")
        self.result_count_label.pack(side="left", padx=10)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="y")

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.result_list = tk.Listbox(left_frame, width=50, height=35)
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

    def select_folder(self):
        folder = filedialog.askdirectory(title="Sélectionner le dossier playerBase")
        if folder:
            self.folder_path = folder
            self.folder_label.config(text=f"Dossier sélectionné : {folder}")
            self.load_json_files()

    def load_json_files(self):
        if not self.folder_path:
            messagebox.showwarning("Attention", "Choisis d'abord un dossier playerBase.")
            return

        self.player_data = []
        self.filtered_items = []
        self.result_list.delete(0, tk.END)
        self.details_text.delete("1.0", tk.END)

        errors = []
        total_files = 0

        try:
            file_names = os.listdir(self.folder_path)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire le dossier :\n{e}")
            return

        for file_name in file_names:
            if not file_name.lower().endswith(".json"):
                continue

            total_files += 1
            file_path = os.path.join(self.folder_path, file_name)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                extracted = self.extract_info(data, file_name, file_path)
                self.player_data.append(extracted)

            except Exception as e:
                errors.append(f"{file_name} : {e}")

        self.player_data.sort(key=lambda x: (x["display_name"] or x["nameplate_name"] or x["file_name"]).lower())
        self.update_result_list(self.player_data)

        msg = f"{len(self.player_data)} fichier(s) JSON chargé(s) sur {total_files}."
        if errors:
            msg += f"\n\n{len(errors)} erreur(s) détectée(s)."

        if errors:
            messagebox.showwarning(
                "Chargement terminé",
                msg + "\n\nPremières erreurs :\n" + "\n".join(errors[:10])
            )

    def extract_info(self, data, file_name, file_path):
        components = data.get("Components", {})

        nameplate_name = components.get("Nameplate", {}).get("Text", "")
        display_name = (
            components.get("DisplayName", {})
            .get("DisplayName", {})
            .get("RawText", "")
        )

        normalized_nameplate = normalize_player_name(nameplate_name)
        normalized_display = normalize_player_name(display_name)

        transform = components.get("Transform", {})
        current_position = transform.get("Position", {})

        player_component = components.get("Player", {})
        player_data = player_component.get("PlayerData", {})
        per_world_default = player_data.get("PerWorldData", {}).get("default", {})

        last_position = per_world_default.get("LastPosition", {})
        death_positions = per_world_default.get("DeathPositions", [])
        user_markers = per_world_default.get("UserMarkers", [])

        last_death = death_positions[-1] if death_positions else None

        inventory = player_component.get("Inventory", {})
        storage_items = inventory.get("Storage", {}).get("Items", {})
        hotbar_items = inventory.get("HotBar", {}).get("Items", {})
        armor_items = inventory.get("Armor", {}).get("Items", {})
        utility_items = inventory.get("Utility", {}).get("Items", {})
        backpack_items = inventory.get("Backpack", {}).get("Items", {})

        discovered_zones = player_data.get("DiscoveredZones", [])

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
            "raw_data": data,
        }

    def on_search(self, *args):
        query_raw = self.search_var.get()
        query = normalize_player_name(query_raw)

        if not query:
            filtered = self.player_data
        else:
            filtered = []
            for p in self.player_data:
                if (
                    query in p["normalized_nameplate"]
                    or query in p["normalized_display"]
                    or query in p["search_text"]
                ):
                    filtered.append(p)

        self.update_result_list(filtered)

    def update_result_list(self, items):
        self.result_list.delete(0, tk.END)
        self.filtered_items = items

        for item in items:
            main_name = item["display_name"] or item["nameplate_name"] or "Sans nom"
            secondary_name = item["nameplate_name"] if item["nameplate_name"] and item["nameplate_name"] != main_name else ""

            if secondary_name:
                display = f"{main_name} ({secondary_name})  |  {item['file_name']}"
            else:
                display = f"{main_name}  |  {item['file_name']}"

            self.result_list.insert(tk.END, display)

        count = len(items)
        self.result_count_label.config(text=f"{count} résultat{'s' if count != 1 else ''}")
        self.details_text.delete("1.0", tk.END)

    def on_select_result(self, event):
        selection = self.result_list.curselection()
        if not selection:
            return

        index = selection[0]
        item = self.filtered_items[index]

        self.details_text.delete("1.0", tk.END)

        lines = []

        lines.append("=== INFORMATIONS JOUEUR ===\n")
        lines.append(f"Nom affiché : {item['display_name'] or 'N/A'}")
        lines.append(f"Nameplate : {item['nameplate_name'] or 'N/A'}")
        lines.append(f"Nom normalisé : {item['normalized_display'] or item['normalized_nameplate'] or 'N/A'}")
        lines.append(f"Fichier : {item['file_name']}")
        lines.append(f"Chemin complet : {item['file_path']}\n")

        lines.append("=== POSITION ACTUELLE ===")
        pos = item["current_position"]
        if pos:
            lines.append(f"X : {pos.get('X', 'N/A')}")
            lines.append(f"Y : {pos.get('Y', 'N/A')}")
            lines.append(f"Z : {pos.get('Z', 'N/A')}")
        else:
            lines.append("Aucune position actuelle trouvée.")
        lines.append("")

        lines.append("=== DERNIÈRE POSITION SAUVEGARDÉE ===")
        last_pos = item["last_position"]
        if last_pos:
            lines.append(f"X : {last_pos.get('X', 'N/A')}")
            lines.append(f"Y : {last_pos.get('Y', 'N/A')}")
            lines.append(f"Z : {last_pos.get('Z', 'N/A')}")
            lines.append(f"Pitch : {last_pos.get('Pitch', 'N/A')}")
            lines.append(f"Yaw : {last_pos.get('Yaw', 'N/A')}")
            lines.append(f"Roll : {last_pos.get('Roll', 'N/A')}")
        else:
            lines.append("Aucune dernière position trouvée.")
        lines.append("")

        lines.append("=== MORTS ===")
        lines.append(f"Nombre total de morts : {item['death_count']}")
        if item["last_death"]:
            death = item["last_death"]
            transform = death.get("Transform", {})
            lines.append("Dernière mort enregistrée :")
            lines.append(f"Jour : {death.get('Day', 'N/A')}")
            lines.append(f"X : {transform.get('X', 'N/A')}")
            lines.append(f"Y : {transform.get('Y', 'N/A')}")
            lines.append(f"Z : {transform.get('Z', 'N/A')}")
            lines.append(f"MarkerId : {death.get('MarkerId', 'N/A')}")
        else:
            lines.append("Aucune mort enregistrée.")
        lines.append("")

        lines.append("=== INVENTAIRE ===")
        lines.append(f"Items dans Storage : {item['storage_count']}")
        lines.append(f"Items dans HotBar : {item['hotbar_count']}")
        lines.append(f"Items dans Armor : {item['armor_count']}")
        lines.append(f"Items dans Utility : {item['utility_count']}")
        lines.append(f"Items dans Backpack : {item['backpack_count']}")
        lines.append("")

        lines.append("=== AUTRES INFOS ===")
        lines.append(f"UserMarkers : {item['marker_count']}")
        lines.append(f"Zones découvertes : {item['zone_count']}")

        self.details_text.insert("1.0", "\n".join(lines))


if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerSearchApp(root)
    root.mainloop()