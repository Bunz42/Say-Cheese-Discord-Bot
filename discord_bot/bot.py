import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import _sqlite3

# Load the environment variables from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Defining intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

# We use the commands.Bot class, which is built for game/command bots
bot = commands.Bot(command_prefix='!', intents=intents)

# -----------------DATABASE SETUP-----------------
# Establish a connection to the SQLite database
db_connection = _sqlite3.connect('rat_collection.db')
db_cursor = db_connection.cursor()

# Create a table to store captured rats if it doesn't already exist
db_cursor.execute('''
CREATE TABLE IF NOT EXISTS rats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    rat_name TEXT NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
db_connection.commit()

@bot.event
async def on_ready():
    """Confirms the bot is logged in and ready."""
    print(f'{bot.user.name} has connected to Discord!')
    
    # NEW: Load our cog right after the bot connects!
    try:
        await bot.load_extension('cogs.spawning')
        print("Spawning Cog loaded successfully!")
    except Exception as e:
        print(f"Failed to load Spawning Cog: {e}")

bot.run(TOKEN)