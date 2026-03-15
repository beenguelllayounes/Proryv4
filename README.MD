# Discord Raid Bot (Educational/Testing Only)

**WARNING:** This bot is intended to be used only for **educational purposes** to show the potential harm Discord bots can cause.  
**DO NOT USE THIS BOT ON A SERVER WITHOUT PERMISSION FROM THE SERVER OWNER.** This will violate the Discord Terms of Service, which may result in account termination or even criminal prosecution.

## Features
- Deletes all existing channels in a specified server.
- Creates 100 new channels with a specified base name.
- Creates 100 new roles.
- Sends a customizable message with optional @everyone/@here pings 30 times.
- Simple Tkinter GUI to input bot token, server ID, and settings.
- Automatically stops after 30 seconds to prevent prolonged damage.

## Requirements
- Python 3.8+
- discord.py library - install with `pip install discord.py`

## Usage
1. Clone or download the project files.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the GUI with `python main.py`.
4. Enter bot token, server ID, and settings.
5. Click "Start Raid (30s)".
6. The bot will run for 30 seconds before stopping automatically.

## How It Works
- The bot logs in with the provided token.
- Deletes all existing channels in the specified server.
- Creates 100 new channels.
- Creates 100 new roles.
- Continuously sends the specified message to the channel.
- All actions are paced to stay within Discord's rate limits (approx. 4 actions per second).

## Disclaimer
This software is provided for **educational purposes only**. The author is not responsible for any misuse or damage caused by this tool. Use at your own risk and only on servers you own or have explicit permission to test.