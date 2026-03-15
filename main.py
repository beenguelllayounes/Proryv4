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

# Ensure config exists before importing bot
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
        self.root.title("Proryv4")
        self.root.geometry("500x450")
        
        # Variables with default values (will be loaded from config)
        self.token = tk.StringVar()
        self.guild_id = tk.StringVar()
        self.message = tk.StringVar()
        self.channel_name = tk.StringVar()
        self.ping_everyone = tk.BooleanVar()
        self.ping_here = tk.BooleanVar()
        
        # GUI Layout
        tk.Label(root, text="Bot Token:").pack(pady=5)
        tk.Entry(root, textvariable=self.token, width=50, show="*").pack()
        
        tk.Label(root, text="Server ID:").pack(pady=5)
        tk.Entry(root, textvariable=self.guild_id, width=50).pack()
        
        tk.Label(root, text="Message to Spam:").pack(pady=5)
        tk.Entry(root, textvariable=self.message, width=50).pack()
        
        tk.Label(root, text="Channel Base Name:").pack(pady=5)
        tk.Entry(root, textvariable=self.channel_name, width=50).pack()
        
        tk.Checkbutton(root, text="Ping @everyone", variable=self.ping_everyone).pack()
        tk.Checkbutton(root, text="Ping @here", variable=self.ping_here).pack()
        
        self.start_button = tk.Button(root, text="Start Raid (30s)", command=self.start_raid,
                                       bg="red", fg="white", font=("Arial", 12))
        self.start_button.pack(pady=20)
        
        self.status_label = tk.Label(root, text="Status: Idle", font=("Arial", 10))
        self.status_label.pack()
        
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
        
        self.save_config()
        self.start_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Starting bot...")
        
        # Run bot in a separate thread with error logging
        self.bot_thread = threading.Thread(target=self.run_bot_thread)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        self.check_bot_status()
    
    def run_bot_thread(self):
        """Wrapper to catch exceptions in bot thread and print them."""
        try:
            bot.run_bot()  # This will read config.json at runtime
        except Exception as e:
            print(f"Error in bot thread: {e}")
            traceback.print_exc()
    
    def check_bot_status(self):
        if self.bot_thread.is_alive():
            self.status_label.config(text="Status: Bot is running... (will stop after 30s)")
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