import tkinter as tk
from tkinter import messagebox
import json
import threading
import traceback
import os
import sys

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
        self.root = root
        self.root.title("Discord Raid Bot (Test Only)")
        self.root.geometry("600x650")
        
        # Variables with default values (will be loaded from config)
        self.token = tk.StringVar()
        self.guild_id = tk.StringVar()
        self.message = tk.StringVar()
        self.channel_name = tk.StringVar()
        self.channel_count = tk.IntVar(value=100)
        self.messages_per_channel = tk.IntVar(value=10)
        self.role_count = tk.IntVar(value=100)
        self.create_admin_role = tk.BooleanVar(value=False)
        self.ping_everyone = tk.BooleanVar()
        self.ping_here = tk.BooleanVar()
        
        # GUI Layout
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Token
        tk.Label(main_frame, text="Bot Token:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tk.Entry(main_frame, textvariable=self.token, width=50, show="*").grid(row=row, column=1, pady=5)
        row += 1
        
        # Server ID
        tk.Label(main_frame, text="Server ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tk.Entry(main_frame, textvariable=self.guild_id, width=50).grid(row=row, column=1, pady=5)
        row += 1
        
        # Message
        tk.Label(main_frame, text="Message to Spam:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tk.Entry(main_frame, textvariable=self.message, width=50).grid(row=row, column=1, pady=5)
        row += 1
        
        # Channel base name
        tk.Label(main_frame, text="Channel Base Name:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tk.Entry(main_frame, textvariable=self.channel_name, width=50).grid(row=row, column=1, pady=5)
        row += 1
        
        # Channel count
        tk.Label(main_frame, text="Number of Channels:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(main_frame, from_=0, to=500, textvariable=self.channel_count, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Messages per channel
        tk.Label(main_frame, text="Messages per Channel:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(main_frame, from_=0, to=1000, textvariable=self.messages_per_channel, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Role count
        tk.Label(main_frame, text="Number of Roles to Create:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(main_frame, from_=0, to=250, textvariable=self.role_count, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Admin role toggle
        tk.Checkbutton(main_frame, text="Create Admin Role and give to everyone", variable=self.create_admin_role).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Ping options
        tk.Checkbutton(main_frame, text="Ping @everyone", variable=self.ping_everyone).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        tk.Checkbutton(main_frame, text="Ping @here", variable=self.ping_here).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Start button
        self.start_button = tk.Button(main_frame, text="Start Raid", command=self.start_raid,
                                       bg="red", fg="white", font=("Arial", 12))
        self.start_button.grid(row=row, column=0, columnspan=2, pady=20)
        row += 1
        
        # Status
        self.status_label = tk.Label(main_frame, text="Status: Idle", font=("Arial", 10))
        self.status_label.grid(row=row, column=0, columnspan=2)
        
        # Load existing config into GUI
        self.load_config()
    
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
        self.start_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Starting bot...")
        
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
            self.status_label.config(text="Status: Bot is running...")
            self.root.after(1000, self.check_bot_status)
        else:
            self.status_label.config(text="Status: Bot finished.")
            self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = RaidBotGUI(root)
        root.mainloop()
    except Exception as e:
        print("An error occurred while starting the GUI:")
        traceback.print_exc()
        input("Press Enter to exit...")