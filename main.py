import customtkinter as ctk
from tkinter import messagebox
import json
import threading
import traceback
import os
import sys

import io
import contextlib

# Ensure config.json exists with defaults BEFORE importing bot
def ensure_config():
    config_path = "config.json"
    default_config = {
        "token": "",
        "guild_id": "",
        "message": "@everyone This server is being tested!",
        "channel_name": "raid-channel",
        "channel_count": 100,
        "messages_per_channel": 10,
        "role_count": 100,
        "create_admin_role": False,
        "ping_everyone": True,
        "ping_here": False
    }
    
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default {config_path}")
        except Exception as e:
            print(f"Error creating default config: {e}")
            sys.exit(1)
    else:
        # Check if existing config is valid JSON
        try:
            with open(config_path, "r") as f:
                json.load(f)
        except (json.JSONDecodeError, Exception):
            # Corrupted, overwrite with defaults
            try:
                with open(config_path, "w") as f:
                    json.dump(default_config, f, indent=4)
                print(f"Config was corrupted. Recreated default {config_path}")
            except Exception as e:
                print(f"Error recreating config: {e}")
                sys.exit(1)

ensure_config()


# Now import bot safely
try:
    import bot
except ImportError as e:
    print(f"Error importing bot module: {e}")
    print("Make sure bot.py is in the same directory.")
    sys.exit(1)


class RaidBotGUI:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root = root
        self.root.title("Discord Raid Bot (Test Only)")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        # Variables with default values (will be loaded from config)
        self.token = ctk.StringVar()
        self.guild_id = ctk.StringVar()
        self.message = ctk.StringVar()
        self.channel_name = ctk.StringVar()
        self.channel_count = ctk.IntVar(value=100)
        self.messages_per_channel = ctk.IntVar(value=10)
        self.role_count = ctk.IntVar(value=100)
        self.create_admin_role = ctk.BooleanVar(value=False)
        self.ping_everyone = ctk.BooleanVar()
        self.ping_here = ctk.BooleanVar()

        # Appearance mode toggle
        self.appearance_mode = ctk.StringVar(value="Dark")
        self.toggle_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.toggle_frame.pack(padx=0, pady=(8, 0), anchor="ne")
        self.toggle_label = ctk.CTkLabel(self.toggle_frame, text="Appearance:", font=("Segoe UI", 11, "bold"))
        self.toggle_label.pack(side="left", padx=(0, 4))
        self.toggle_switch = ctk.CTkSwitch(self.toggle_frame, text="Light/Dark", variable=self.appearance_mode, onvalue="Light", offvalue="Dark", command=self.toggle_appearance, font=("Segoe UI", 11, "bold"))
        self.toggle_switch.pack(side="left")
        self.toggle_switch.deselect()  # Start in dark mode

        # Tabbed interface
        self.tabview = ctk.CTkTabview(self.root, width=680, height=660)
        self.tabview.pack(padx=10, pady=10)
        self.tab_main = self.tabview.add("Main Controls")
        self.tab_logs = self.tabview.add("Logs")

        # Main Controls Layout
        self._build_main_tab()
        self._build_logs_tab()
    def toggle_appearance(self):
        mode = self.appearance_mode.get()
        ctk.set_appearance_mode(mode)

        # Load existing config into GUI
        self.load_config()

        # Redirect stdout/stderr to log box
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def _build_main_tab(self):
        font_label = ("Segoe UI", 13, "bold")
        font_entry = ("Segoe UI", 13)
        font_button = ("Segoe UI", 14, "bold")
        pady = 8
        row = 0
        frame = self.tab_main

        ctk.CTkLabel(frame, text="Bot Token:", font=font_label).grid(row=row, column=0, sticky="w", pady=pady)
        ctk.CTkEntry(frame, textvariable=self.token, width=250, show="*", font=font_entry).grid(row=row, column=1, pady=pady)
        row += 1

        ctk.CTkLabel(frame, text="Server ID:", font=font_label).grid(row=row, column=0, sticky="w", pady=pady)
        ctk.CTkEntry(frame, textvariable=self.guild_id, width=250, font=font_entry).grid(row=row, column=1, pady=pady)
        row += 1

        ctk.CTkLabel(frame, text="Message to Spam:", font=font_label).grid(row=row, column=0, sticky="w", pady=pady)
        ctk.CTkEntry(frame, textvariable=self.message, width=250, font=font_entry).grid(row=row, column=1, pady=pady)
        row += 1

        ctk.CTkLabel(frame, text="Channel Base Name:", font=font_label).grid(row=row, column=0, sticky="w", pady=pady)
        ctk.CTkEntry(frame, textvariable=self.channel_name, width=250, font=font_entry).grid(row=row, column=1, pady=pady)
        row += 1

        # Number of Channels with live value
        ctk.CTkLabel(frame, text="Number of Channels:", font=font_label).grid(row=row, column=0, sticky="w", pady=pady)
        slider_channels = ctk.CTkSlider(frame, from_=0, to=500, variable=self.channel_count, number_of_steps=500, width=180)
        slider_channels.grid(row=row, column=1, sticky="w", pady=pady)
        self.label_channels_val = ctk.CTkLabel(frame, text=str(self.channel_count.get()), font=font_label, width=40)
        self.label_channels_val.grid(row=row, column=2, sticky="w", padx=8)
        self.channel_count.trace_add("write", lambda *a: self.label_channels_val.configure(text=str(self.channel_count.get())))
        row += 1

        # Messages per Channel with live value
        ctk.CTkLabel(frame, text="Messages per Channel:", font=font_label).grid(row=row, column=0, sticky="w", pady=pady)
        slider_msgs = ctk.CTkSlider(frame, from_=0, to=1000, variable=self.messages_per_channel, number_of_steps=1000, width=180)
        slider_msgs.grid(row=row, column=1, sticky="w", pady=pady)
        self.label_msgs_val = ctk.CTkLabel(frame, text=str(self.messages_per_channel.get()), font=font_label, width=40)
        self.label_msgs_val.grid(row=row, column=2, sticky="w", padx=8)
        self.messages_per_channel.trace_add("write", lambda *a: self.label_msgs_val.configure(text=str(self.messages_per_channel.get())))
        row += 1

        # Number of Roles to Create with live value
        ctk.CTkLabel(frame, text="Number of Roles to Create:", font=font_label).grid(row=row, column=0, sticky="w", pady=pady)
        slider_roles = ctk.CTkSlider(frame, from_=0, to=250, variable=self.role_count, number_of_steps=250, width=180)
        slider_roles.grid(row=row, column=1, sticky="w", pady=pady)
        self.label_roles_val = ctk.CTkLabel(frame, text=str(self.role_count.get()), font=font_label, width=40)
        self.label_roles_val.grid(row=row, column=2, sticky="w", padx=8)
        self.role_count.trace_add("write", lambda *a: self.label_roles_val.configure(text=str(self.role_count.get())))
        row += 1

        ctk.CTkCheckBox(frame, text="Create Admin Role and give to everyone", variable=self.create_admin_role, font=font_label).grid(row=row, column=0, columnspan=3, sticky="w", pady=pady)
        row += 1

        ctk.CTkCheckBox(frame, text="Ping @everyone", variable=self.ping_everyone, font=font_label).grid(row=row, column=0, columnspan=3, sticky="w", pady=pady)
        row += 1
        ctk.CTkCheckBox(frame, text="Ping @here", variable=self.ping_here, font=font_label).grid(row=row, column=0, columnspan=3, sticky="w", pady=pady)
        row += 1

        self.start_button = ctk.CTkButton(frame, text="Start Raid", command=self.start_raid, fg_color="#d90429", hover_color="#ef233c", text_color="white", font=font_button, width=180, height=38)
        self.start_button.grid(row=row, column=0, columnspan=3, pady=18)
        row += 1

        self.status_label = ctk.CTkLabel(frame, text="Status: Idle", font=("Segoe UI", 12, "bold"), text_color="#8ecae6")
        self.status_label.grid(row=row, column=0, columnspan=3, pady=8)

    def _build_logs_tab(self):
        self.log_textbox = ctk.CTkTextbox(self.tab_logs, width=650, height=600, font=("Consolas", 11), wrap="word")
        self.log_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_textbox.configure(state="disabled")

    def write(self, msg):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", msg)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        # Also print to original stdout for debugging
        self._orig_stdout.write(msg)

    def flush(self):
        pass
    
    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.token.set(config.get("token", ""))
                self.guild_id.set(config.get("guild_id", ""))
                self.message.set(config.get("message", "@everyone This server is being tested!"))
                self.channel_name.set(config.get("channel_name", "raid-channel"))
                self.channel_count.set(config.get("channel_count", 100))
                self.messages_per_channel.set(config.get("messages_per_channel", 10))
                self.role_count.set(config.get("role_count", 100))
                self.create_admin_role.set(config.get("create_admin_role", False))
                self.ping_everyone.set(config.get("ping_everyone", True))
                self.ping_here.set(config.get("ping_here", False))
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        config = {
            "token": self.token.get(),
            "guild_id": self.guild_id.get(),
            "message": self.message.get(),
            "channel_name": self.channel_name.get(),
            "channel_count": self.channel_count.get(),
            "messages_per_channel": self.messages_per_channel.get(),
            "role_count": self.role_count.get(),
            "create_admin_role": self.create_admin_role.get(),
            "ping_everyone": self.ping_everyone.get(),
            "ping_here": self.ping_here.get()
        }
        try:
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def start_raid(self):
        if not self.token.get() or not self.guild_id.get():
            messagebox.showerror("Error", "Token and Server ID are required.")
            return

        # Basic validation for counts
        if self.channel_count.get() < 0 or self.messages_per_channel.get() < 0 or self.role_count.get() < 0:
            messagebox.showerror("Error", "Counts must be non-negative.")
            return

        self.save_config()
        self.start_button.configure(state="disabled", fg_color="#8d99ae")
        self.status_label.configure(text="Status: Starting bot...", text_color="#ffd166")

        # Run bot in a separate thread with error logging
        self.bot_thread = threading.Thread(target=self.run_bot_thread)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        self.check_bot_status()
    
    def run_bot_thread(self):
        try:
            bot.run_bot()
        except Exception as e:
            print(f"Error in bot thread: {e}")
            traceback.print_exc()
    
    def check_bot_status(self):
        if self.bot_thread.is_alive():
            self.status_label.configure(text="Status: Bot is running...", text_color="#06d6a0")
            self.root.after(1000, self.check_bot_status)
        else:
            self.status_label.configure(text="Status: Bot finished.", text_color="#8ecae6")
            self.start_button.configure(state="normal", fg_color="#d90429")

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = RaidBotGUI(root)
        root.mainloop()
    except Exception as e:
        print("An error occurred while starting the GUI:")
        traceback.print_exc()
        input("Press Enter to exit...")