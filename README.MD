# Discord Raid Bot (Educational/Testing Only)

**WARNING:** This bot is designed for **educational purposes only** to demonstrate how Discord bots can be misused.  
**Never use this bot on a server without explicit permission from the server owner.** Unauthorized use violates Discord's Terms of Service and may lead to account termination or legal consequences.

## Features
- Deletes all existing channels in a target server.
- Creates a customizable number of new text channels.
- Creates a customizable number of new roles.
- Optionally creates an **administrator role** and assigns it to **every member** of the server.
- Spams a customizable message (with optional @everyone/@here pings) in all new channels.
- **~12 actions per second** – paced to stay within Discord's rate limits (adjustable).
- Simple Tkinter GUI to configure the bot.
- All settings are saved in `config.json` for persistence.

## Requirements
- Python 3.8+
- `discord.py` library (`pip install discord.py`)
- `tkinter` (usually included with Python)

## How to Create and Invite the Bot

### Step 1: Create a Discord Application
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application**, give it a name, and create it.
3. Go to the **Bot** tab on the left sidebar.
4. Click **Add Bot** and confirm.

### Step 2: Get the Bot Token
- Under the **Bot** tab, click **Reset Token** (or Copy) to reveal your bot token.  
  **Keep this token secret!** Anyone with it can control your bot.

### Step 3: Enable Privileged Gateway Intents
The bot needs certain intents to function properly. Under the **Bot** tab, scroll down to **Privileged Gateway Intents** and enable:
- **Presence Intent** (if you want to track member status – optional but safe to enable)
- **Server Members Intent** (required to fetch all members for admin role assignment)
- **Message Content Intent** (required to read message content – needed for spamming)

### Step 4: Invite the Bot to Your Server
1. Go to the **OAuth2** → **URL Generator** tab.
2. Under **Scopes**, select `bot`.
3. Under **Bot Permissions**, select the following permissions:
   - `Manage Channels` (to delete and create channels)
   - `Manage Roles` (to create roles and assign the admin role)
   - `Send Messages` (to spam messages)
   - `Mention @everyone, @here, and All Roles` (to ping everyone)
   - `Administrator` (optional, but if you want the bot to have full control; otherwise, grant individually)
4. Copy the generated URL, open it in your browser, and invite the bot to your server.
5. Ensure the bot has the necessary permissions in the server (you can also assign roles after joining).

## Installation & Usage

1. **Clone or download** the project files.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the GUI**:
   ```bash
   python main.py
   ```
4. **Fill in the fields**:
   - **Bot Token**: Paste your bot token.
   - **Server ID**: Right‑click your server icon in Discord → **Copy ID** (Developer Mode must be enabled in Discord settings).
   - **Message to Spam**: The text that will be sent repeatedly.
   - **Channel Base Name**: New channels will be named like `base-name-0`, `base-name-1`, etc.
   - **Number of Channels**: How many channels to create (0 to skip).
   - **Messages per Channel**: How many messages to send in **each** channel.
   - **Number of Roles**: How many roles to create (0 to skip).
   - **Create Admin Role and give to everyone**: If checked, the bot creates a role with administrator permissions and assigns it to every member of the server.
   - **Ping @everyone / @here**: Prepend the message with these mentions (be careful – this will notify the entire server).

5. Click **Start Raid**. The console will show progress and any errors. The bot will shut down automatically when all actions are completed.

## Configuration
All settings are saved in `config.json` and automatically loaded the next time you open the GUI. You can edit this file manually, but it's easier to use the GUI.

## Rate Limiting & Speed
The bot is programmed to perform approximately **~40 actions per second** (by adding a `0.03` second delay after each API call). This is a safe value to avoid hitting Discord's global rate limits. If you encounter rate limit errors, increase the delay in `bot.py` (look for `ACTION_DELAY`). If you want it faster, decrease the delay – but do so at your own risk; excessive speed may get your bot temporarily banned.

## Disclaimer
This software is provided for **educational purposes only**. The author is not responsible for any misuse or damage caused by this tool. Use at your own risk and **only on servers you own or have explicit permission to test**.

Unauthorized use of this bot on other servers violates Discord's Terms of Service and may result in:
- The bot being terminated.
- Your Discord account being disabled.
- Potential legal action from affected parties.

**Be responsible and ethical.**