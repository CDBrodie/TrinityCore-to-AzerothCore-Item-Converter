#TrinityCore to AzerothCore Item Migrator by CDBrodie
#GNU Public Licence GPL-3.0
#https://github.com/CDBrodie/TrinityCore-to-AzerothCore-Item-Converter/

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import json
import os

class ItemMigrator:
    def __init__(self, root):
        self.root = root
        self.root.title("TrinityCore to AzerothCore Item Migrator")
        self.connection = None
        self.items_data = []
        self.selected_items = []
        self.quality_names = {
            0: "Poor", 1: "Common", 2: "Uncommon", 3: "Rare", 4: "Epic", 5: "Legendary", 6: "Artifact", 7: "Heirloom"
        }
        self.quality_colors = {
            0: "#444444",  # Dark grey for Poor
            1: "#000000",  # Black for Common
            2: "#1eff00",  # Green for Uncommon
            3: "#0070dd",  # Blue for Rare
            4: "#a335ee",  # Purple for Epic
            5: "#ff8000",  # Orange for Legendary
            6: "#e6cc80",  # Light gold for Artifact
            7: "#e6cc80"   # Gold for Heirloom
        }
        self.subtype_names = {
            0: "Consumable", 1: "Container", 2: "Weapon", 3: "Gem", 4: "Armor",
            5: "Reagent", 6: "Projectile", 7: "Trade Goods", 8: "Generic", 9: "Recipe",
            10: "Money", 11: "Quiver", 12: "Quest", 13: "Key", 14: "Permanent", 15: "Miscellaneous", 16: "Glyph"
        }
        # Weapon slot mappings (class=2)
        self.weapon_slots = {
            0: "One-Handed Axe", 1: "Two-Handed Axe", 2: "Bow", 3: "Gun", 4: "One-Handed Mace",
            5: "Two-Handed Mace", 6: "Polearm", 7: "One-Handed Sword", 8: "Two-Handed Sword",
            9: "Obsolete", 10: "Staff", 11: "Exotic", 12: "Exotic", 13: "Fist Weapon", 14: "Miscellaneous",
            15: "Dagger", 16: "Thrown", 17: "Spear", 18: "Crossbow", 19: "Wand", 20: "Fishing Pole"
        }
        # Armor slot mappings (class=4)
        self.armor_slots = {
            0: "Miscellaneous", 1: "Cloth", 2: "Leather", 3: "Mail", 4: "Plate", 5: "Buckler",
            6: "Shield", 7: "Libram", 8: "Idol", 9: "Totem", 10: "Sigil"
        }
        # Inventory type mappings (where the item is equipped)
        self.inventory_slots = {
            0: "Non-equipable", 1: "Head", 2: "Neck", 3: "Shoulder", 4: "Shirt", 5: "Chest",
            6: "Waist", 7: "Legs", 8: "Feet", 9: "Wrists", 10: "Hands", 11: "Finger",
            12: "Trinket", 13: "One-Hand", 14: "Shield", 15: "Ranged", 16: "Back",
            17: "Two-Hand", 18: "Bag", 19: "Tabard", 20: "Robe", 21: "Main Hand",
            22: "Off Hand", 23: "Holdable", 24: "Ammo", 25: "Thrown", 26: "Ranged"
        }
        self.stat_names = {
            0: "Mana", 1: "Health", 3: "Agility", 4: "Strength", 5: "Intellect", 6: "Spirit", 7: "Stamina",
            12: "Defense Rating", 13: "Dodge Rating", 14: "Parry Rating", 15: "Block Rating", 16: "Hit Melee Rating",
            17: "Hit Ranged Rating", 18: "Hit Spell Rating", 19: "Crit Melee Rating", 20: "Crit Ranged Rating",
            21: "Crit Spell Rating", 22: "Hit Taken Melee Rating", 23: "Hit Taken Ranged Rating", 24: "Hit Taken Spell Rating",
            25: "Crit Taken Melee Rating", 26: "Crit Taken Ranged Rating", 27: "Crit Taken Spell Rating", 28: "Haste Melee Rating",
            29: "Haste Ranged Rating", 30: "Haste Spell Rating", 31: "Hit Rating", 32: "Crit Rating", 33: "Hit Taken Rating",
            34: "Crit Taken Rating", 35: "Resilience Rating", 36: "Haste Rating", 37: "Expertise Rating", 38: "Attack Power",
            39: "Ranged Attack Power", 40: "Feral Attack Power", 41: "Spell Healing Done", 42: "Spell Damage Done", 43: "Mana Regeneration",
            44: "Armor Penetration Rating", 45: "Spell Power", 46: "Health Regen", 47: "Spell Penetration", 48: "Block Value"
        }
        self.create_widgets()
        self.load_config()

    def get_item_slot(self, item_class, item_subclass, inventory_type):
        """Determine the slot/type for an item based on its class, subclass, and inventory type"""
        if item_class == 2:  # Weapon
            return self.weapon_slots.get(item_subclass, f"Unknown Weapon ({item_subclass})")
        elif item_class == 4:  # Armor
            # For armor, use inventory type to determine slot
            return self.inventory_slots.get(inventory_type, f"Unknown Armor ({inventory_type})")
        else:
            return "N/A"

    def create_widgets(self):
        # Database connection frame
        db_frame = ttk.LabelFrame(self.root, text="Database Connection")
        db_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Label(db_frame, text="Host:").grid(row=0, column=0, sticky="w")
        self.host_entry = ttk.Entry(db_frame, width=15)
        self.host_entry.grid(row=0, column=1, sticky="w", padx=2)
        
        ttk.Label(db_frame, text="Port:").grid(row=0, column=2, sticky="w")
        self.port_entry = ttk.Entry(db_frame, width=8)
        self.port_entry.grid(row=0, column=3, sticky="w", padx=2)
        self.port_entry.insert(0, "3306")
        
        ttk.Label(db_frame, text="Database:").grid(row=0, column=4, sticky="w")
        self.database_entry = ttk.Entry(db_frame, width=15)
        self.database_entry.grid(row=0, column=5, sticky="w", padx=2)
        
        ttk.Label(db_frame, text="Username:").grid(row=1, column=0, sticky="w")
        self.username_entry = ttk.Entry(db_frame, width=15)
        self.username_entry.grid(row=1, column=1, sticky="w", padx=2)
        
        ttk.Label(db_frame, text="Password:").grid(row=1, column=2, sticky="w")
        self.password_entry = ttk.Entry(db_frame, width=15)  # Unmasked
        self.password_entry.grid(row=1, column=3, sticky="w", padx=2)
        
        self.connect_btn = ttk.Button(db_frame, text="Connect", command=self.connect_database)
        self.connect_btn.grid(row=1, column=4, padx=2)
        self.disconnect_btn = ttk.Button(db_frame, text="Disconnect", command=self.disconnect_database, state="disabled")
        self.disconnect_btn.grid(row=1, column=5, padx=2)

        # Filter frame
        filter_frame = ttk.LabelFrame(self.root, text="Item Filters")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        ttk.Label(filter_frame, text="Min ID:").grid(row=0, column=0, sticky="w")
        self.min_id_entry = ttk.Entry(filter_frame, width=10)
        self.min_id_entry.grid(row=0, column=1, padx=2)
        self.min_id_entry.insert(0, "50000")
        ttk.Label(filter_frame, text="Max ID:").grid(row=0, column=2, sticky="w")
        self.max_id_entry = ttk.Entry(filter_frame, width=10)
        self.max_id_entry.grid(row=0, column=3, padx=2)
        self.max_id_entry.insert(0, "60000")

        ttk.Label(filter_frame, text="Name contains:").grid(row=0, column=4, sticky="w")
        self.name_entry = ttk.Entry(filter_frame, width=15)
        self.name_entry.grid(row=0, column=5, padx=2)

        ttk.Label(filter_frame, text="Subtype:").grid(row=0, column=6, sticky="w")
        self.subtype_var = tk.StringVar()
        self.subtype_combo = ttk.Combobox(filter_frame, textvariable=self.subtype_var, width=14, state="readonly")
        self.subtype_combo['values'] = ["Any"] + [v for k, v in sorted(self.subtype_names.items())]
        self.subtype_combo.current(0)
        self.subtype_combo.grid(row=0, column=7, padx=2)

        ttk.Label(filter_frame, text="Quality:").grid(row=1, column=0, sticky="w")
        self.quality_var = tk.StringVar()
        self.quality_combo = ttk.Combobox(filter_frame, textvariable=self.quality_var, width=12, state="readonly")
        self.quality_combo['values'] = ["Any"] + [v for k, v in sorted(self.quality_names.items())]
        self.quality_combo.current(0)
        self.quality_combo.grid(row=1, column=1, padx=2)

        ttk.Label(filter_frame, text="Slot:").grid(row=1, column=2, sticky="w")
        self.slot_var = tk.StringVar()
        self.slot_combo = ttk.Combobox(filter_frame, textvariable=self.slot_var, width=16, state="readonly")
        # Combine all possible slots
        all_slots = ["Any", "N/A"] + sorted(set(self.weapon_slots.values()) | set(self.inventory_slots.values()))
        self.slot_combo['values'] = all_slots
        self.slot_combo.current(0)
        self.slot_combo.grid(row=1, column=3, padx=2)

        self.load_btn = ttk.Button(filter_frame, text="Load Items", command=self.load_items, state="disabled")
        self.load_btn.grid(row=1, column=4, padx=2)
        
        # Table and details
        table_frame = ttk.Frame(self.root)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        columns = ("Select", "ID", "Name", "Quality", "Subtype", "Slot", "Level")
        self.items_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        self.items_tree.heading("Select", text="☐")
        self.items_tree.heading("ID", text="ID")
        self.items_tree.heading("Name", text="Name")
        self.items_tree.heading("Quality", text="Quality")
        self.items_tree.heading("Subtype", text="Subtype")
        self.items_tree.heading("Slot", text="Slot")
        self.items_tree.heading("Level", text="Level")
        self.items_tree.column("Select", width=50, anchor="center")
        self.items_tree.column("ID", width=80, anchor="center")
        self.items_tree.column("Name", width=200, anchor="w")
        self.items_tree.column("Quality", width=100, anchor="center")
        self.items_tree.column("Subtype", width=120, anchor="center")
        self.items_tree.column("Slot", width=140, anchor="center")
        self.items_tree.column("Level", width=80, anchor="center")
        for quality, color in self.quality_colors.items():
            self.items_tree.tag_configure(f"quality_{quality}", foreground=color)
        self.items_tree.grid(row=0, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.items_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.items_tree.configure(yscrollcommand=v_scrollbar.set)
        self.items_tree.bind("<Button-1>", self.on_item_click)
        self.items_tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # Details panel
        details_frame = ttk.LabelFrame(self.root, text="Item Details")
        details_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
        self.details_text = tk.Text(details_frame, wrap=tk.WORD, width=35, height=20, font=("Consolas", 9), state="disabled")
        self.details_text.pack(fill="both", expand=True)

        # Controls
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.select_all_btn = ttk.Button(control_frame, text="Select All", command=self.select_all_items, state="disabled")
        self.select_all_btn.pack(side=tk.LEFT, padx=2)
        self.deselect_all_btn = ttk.Button(control_frame, text="Deselect All", command=self.deselect_all_items, state="disabled")
        self.deselect_all_btn.pack(side=tk.LEFT, padx=2)
        self.export_btn = ttk.Button(control_frame, text="Export Selected", command=self.export_items, state="disabled")
        self.export_btn.pack(side=tk.LEFT, padx=2)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(control_frame, textvariable=self.status_var, relief="sunken", padding="5")
        self.status_bar.pack(side=tk.RIGHT, fill="x", expand=True)

    def update_status(self, message, status_type="info"):
        self.status_var.set(message)
        # Set status bar colors based on type
        if status_type == "success":
            self.status_bar.configure(background="#d4edda", foreground="#155724")  # Green
        elif status_type == "error":
            self.status_bar.configure(background="#f8d7da", foreground="#721c24")  # Red
        elif status_type == "warning":
            self.status_bar.configure(background="#fff3cd", foreground="#856404")  # Orange
        else:  # info
            self.status_bar.configure(background="#d1ecf1", foreground="#0c5460")  # Blue

    def load_config(self):
        try:
            if os.path.exists("db_config.json"):
                with open("db_config.json", "r") as f:
                    config = json.load(f)
                    self.host_entry.insert(0, config.get("host", ""))
                    self.port_entry.delete(0, tk.END)
                    self.port_entry.insert(0, config.get("port", "3306"))
                    self.database_entry.insert(0, config.get("database", ""))
                    self.username_entry.insert(0, config.get("username", ""))
                    self.password_entry.insert(0, config.get("password", ""))
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        try:
            config = {
                "host": self.host_entry.get(),
                "port": self.port_entry.get(),
                "database": self.database_entry.get(),
                "username": self.username_entry.get(),
                "password": self.password_entry.get()
            }
            with open("db_config.json", "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def connect_database(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host_entry.get(),
                port=int(self.port_entry.get()),
                database=self.database_entry.get(),
                user=self.username_entry.get(),
                password=self.password_entry.get()
            )
            if self.connection.is_connected():
                self.update_status("Connected to database successfully", "success")
                self.connect_btn.config(state="disabled")
                self.disconnect_btn.config(state="normal")
                self.load_btn.config(state="normal")
                self.save_config()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{e}")
            self.update_status("Connection failed", "error")

    def disconnect_database(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            self.update_status("Disconnected from database", "info")
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.load_btn.config(state="disabled")
            self.select_all_btn.config(state="disabled")
            self.deselect_all_btn.config(state="disabled")
            self.export_btn.config(state="disabled")
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            self.items_data.clear()
            self.selected_items.clear()

    def load_items(self):
        if not self.connection or not self.connection.is_connected():
            messagebox.showerror("Error", "Not connected to database")
            return
        try:
            min_id = int(self.min_id_entry.get())
            max_id = int(self.max_id_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid ID range")
            return
        name_filter = self.name_entry.get().strip().lower()
        subtype_filter = self.subtype_var.get()
        quality_filter = self.quality_var.get()
        slot_filter = self.slot_var.get()
        try:
            cursor = self.connection.cursor()
            query = f"""
            SELECT entry, class, subclass, name, displayid, Quality, ItemLevel, stackable, BuyPrice, SellPrice, RequiredLevel, \
                   stat_type1, stat_value1, stat_type2, stat_value2, stat_type3, stat_value3, stat_type4, stat_value4, stat_type5, stat_value5, \
                   stat_type6, stat_value6, stat_type7, stat_value7, stat_type8, stat_value8, stat_type9, stat_value9, stat_type10, stat_value10, \
                   dmg_min1, dmg_max1, delay, armor, holy_res, fire_res, nature_res, frost_res, shadow_res, arcane_res, description, InventoryType
            FROM item_template 
            WHERE entry >= {min_id} AND entry <= {max_id} 
            ORDER BY entry
            """
            cursor.execute(query)
            results = cursor.fetchall()
            # Apply filters in Python for name, subtype, quality, slot
            filtered_results = []
            for row in results:
                item_name = row[3].lower()
                item_subtype = self.subtype_names.get(row[2], f"Unknown ({row[2]})")
                item_quality = self.quality_names.get(row[5], f"Unknown ({row[5]})")
                item_slot = self.get_item_slot(row[1], row[2], row[42])  # class, subclass, InventoryType
                
                if name_filter and name_filter not in item_name:
                    continue
                if subtype_filter != "Any" and subtype_filter != item_subtype:
                    continue
                if quality_filter != "Any" and quality_filter != item_quality:
                    continue
                if slot_filter != "Any" and slot_filter != item_slot:
                    continue
                filtered_results.append(row)
            results = filtered_results
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            self.items_data.clear()
            self.selected_items.clear()
            for row in results:
                item_data = {
                    'entry': row[0], 'class': row[1], 'subclass': row[2], 'name': row[3], 'displayid': row[4], 'Quality': row[5],
                    'ItemLevel': row[6], 'stackable': row[7], 'BuyPrice': row[8], 'SellPrice': row[9], 'RequiredLevel': row[10],
                    'stat_type1': row[11], 'stat_value1': row[12], 'stat_type2': row[13], 'stat_value2': row[14],
                    'stat_type3': row[15], 'stat_value3': row[16], 'stat_type4': row[17], 'stat_value4': row[18],
                    'stat_type5': row[19], 'stat_value5': row[20], 'stat_type6': row[21], 'stat_value6': row[22],
                    'stat_type7': row[23], 'stat_value7': row[24], 'stat_type8': row[25], 'stat_value8': row[26],
                    'stat_type9': row[27], 'stat_value9': row[28], 'stat_type10': row[29], 'stat_value10': row[30],
                    'dmg_min1': row[31], 'dmg_max1': row[32], 'delay': row[33], 'armor': row[34], 'holy_res': row[35],
                    'fire_res': row[36], 'nature_res': row[37], 'frost_res': row[38], 'shadow_res': row[39], 'arcane_res': row[40],
                    'description': row[41], 'InventoryType': row[42]
                }
                self.items_data.append(item_data)
                quality_name = self.quality_names.get(item_data['Quality'], f"Unknown ({item_data['Quality']})")
                subtype_name = self.subtype_names.get(item_data['subclass'], f"Unknown ({item_data['subclass']})")
                slot_name = self.get_item_slot(item_data['class'], item_data['subclass'], item_data['InventoryType'])
                item_id = self.items_tree.insert("", "end", values=(
                    "☐", item_data['entry'], item_data['name'], quality_name, subtype_name, slot_name, item_data['ItemLevel']
                ), tags=(f"quality_{item_data['Quality']}",))
            cursor.close()
            self.update_status(f"Loaded {len(results)} items", "success")
            self.select_all_btn.config(state="normal")
            self.deselect_all_btn.config(state="normal")
            self.export_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load items:\n{e}")
            self.update_status("Failed to load items")

    def on_item_click(self, event):
        region = self.items_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.items_tree.identify_row(event.y)
            if item:
                self.toggle_item_selection(item)

    def toggle_item_selection(self, item):
        current_values = list(self.items_tree.item(item, "values"))
        item_id = int(current_values[1])
        if current_values[0] == "☐":
            current_values[0] = "☑"
            # Add the actual item data to selected_items
            for data in self.items_data:
                if data['entry'] == item_id and data not in self.selected_items:
                    self.selected_items.append(data)
                    break
        else:
            current_values[0] = "☐"
            # Remove the item data from selected_items
            self.selected_items = [d for d in self.selected_items if d['entry'] != item_id]
        self.items_tree.item(item, values=current_values)
        self.update_status(f"{len(self.selected_items)} items selected")

    def select_all_items(self):
        self.selected_items.clear()
        for item in self.items_tree.get_children():
            current_values = list(self.items_tree.item(item, "values"))
            current_values[0] = "☑"
            self.items_tree.item(item, values=current_values)
            item_id = int(current_values[1])
            for data in self.items_data:
                if data['entry'] == item_id and data not in self.selected_items:
                    self.selected_items.append(data)
                    break
        self.update_status(f"All {len(self.selected_items)} items selected")

    def deselect_all_items(self):
        for item in self.items_tree.get_children():
            current_values = list(self.items_tree.item(item, "values"))
            current_values[0] = "☐"
            self.items_tree.item(item, values=current_values)
        self.selected_items.clear()
        self.update_status("All items deselected")

    def on_item_select(self, event):
        selection = self.items_tree.selection()
        if selection:
            item = selection[0]
            item_values = self.items_tree.item(item, "values")
            item_id = item_values[1]
            item_data = None
            for data in self.items_data:
                if str(data['entry']) == str(item_id):
                    item_data = data
                    break
            if item_data:
                self.show_item_details(item_data)

    def show_item_details(self, item_data):
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)
        details = f"Item ID: {item_data['entry']}\n"
        details += f"Name: {item_data['name']}\n"
        details += f"Quality: {self.quality_names.get(item_data['Quality'], 'Unknown')}\n"
        details += f"Subtype: {self.subtype_names.get(item_data['subclass'], 'Unknown')}\n"
        details += f"Slot: {self.get_item_slot(item_data['class'], item_data['subclass'], item_data['InventoryType'])}\n"
        details += f"Item Level: {item_data['ItemLevel']}\n"
        details += f"Required Level: {item_data['RequiredLevel']}\n"
        details += f"Max Stack: {item_data['stackable']}\n"
        if item_data['BuyPrice'] > 0:
            details += f"Buy Price: {item_data['BuyPrice']}\n"
        if item_data['SellPrice'] > 0:
            details += f"Sell Price: {item_data['SellPrice']}\n"
        stats_found = False
        for i in range(1, 11):
            stat_type = item_data.get(f'stat_type{i}', 0)
            stat_value = item_data.get(f'stat_value{i}', 0)
            if stat_type > 0 and stat_value != 0:
                if not stats_found:
                    details += "\nStats:\n"
                    stats_found = True
                stat_name = self.stat_names.get(stat_type, f"Unknown Stat {stat_type}")
                details += f"  {stat_name}: {stat_value:+d}\n"
        if item_data['dmg_min1'] > 0 or item_data['dmg_max1'] > 0:
            details += f"\nDamage: {item_data['dmg_min1']}-{item_data['dmg_max1']}\n"
            if item_data['delay'] > 0:
                details += f"Speed: {item_data['delay'] / 1000:.2f}\n"
        if item_data['armor'] > 0:
            details += f"\nArmor: {item_data['armor']}\n"
        resistances = []
        if item_data['holy_res'] > 0:
            resistances.append(f"Holy: {item_data['holy_res']}")
        if item_data['fire_res'] > 0:
            resistances.append(f"Fire: {item_data['fire_res']}")
        if item_data['nature_res'] > 0:
            resistances.append(f"Nature: {item_data['nature_res']}")
        if item_data['frost_res'] > 0:
            resistances.append(f"Frost: {item_data['frost_res']}")
        if item_data['shadow_res'] > 0:
            resistances.append(f"Shadow: {item_data['shadow_res']}")
        if item_data['arcane_res'] > 0:
            resistances.append(f"Arcane: {item_data['arcane_res']}")
        if resistances:
            details += f"\nResistances: {', '.join(resistances)}\n"
        if item_data['description']:
            details += f"\nDescription:\n{item_data['description']}\n"
        self.details_text.insert(1.0, details)
        self.details_text.config(state="disabled")

    def export_items(self):
        if not self.selected_items:
            messagebox.showwarning("Warning", "No items selected for export")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")],
            title="Save SQL Export"
        )
        if not filename:
            return
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("-- TrinityCore to AzerothCore Item Migration\n")
                f.write("-- Generated by Item Migrator Tool\n\n")
                for item_data in self.selected_items:
                    f.write(f"-- {item_data['name']} (ID: {item_data['entry']})\n")
                    f.write("INSERT INTO `item_template` (")
                    columns = []
                    values = []
                    for key, value in item_data.items():
                        columns.append(f"`{key}`")
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, str):
                            escaped_value = value.replace("'", "\\'")
                            values.append(f"'{escaped_value}'")
                        else:
                            values.append(str(value))
                    f.write(", ".join(columns))
                    f.write(") VALUES (")
                    f.write(", ".join(values))
                    f.write(");\n\n")
            messagebox.showinfo("Success", f"Exported {len(self.selected_items)} items to {filename}")
            self.update_status(f"Exported {len(self.selected_items)} items successfully")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export items:\n{e}")
            self.update_status("Export failed")

def main():
    root = tk.Tk()
    app = ItemMigrator(root)
    root.mainloop()

if __name__ == "__main__":
    main()