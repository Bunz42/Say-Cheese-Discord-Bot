import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import _sqlite3

# Load the environment variables from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# ------------------------------------- DATABASE SETUP ------------------------------------- #

# Establish a connection to the SQLite database
db_connection = _sqlite3.connect('rat_collection.db')
db_cursor = db_connection.cursor()

# Create a table to store captured rats in rat_collection.db
db_cursor.execute('''
CREATE TABLE IF NOT EXISTS rats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    rat_name TEXT,
    level INTEGER DEFAULT 1,
    captured_at TEXT,
    equipped INTEGER DEFAULT 0
)
''')

# Creating the economy table in rat_collection.db
db_cursor.execute('''
CREATE TABLE IF NOT EXISTS economy (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
''')

# Creating the shop table in rat_collection.db
db_cursor.execute('''
CREATE TABLE IF NOT EXISTS shop (
    item_name TEXT PRIMARY KEY,
    price INTEGER,
    description TEXT,
    item_type TEXT,
    effect_value INTEGER
)
''')

# Adding the last_claim_time column to the economy table
try:
    db_cursor.execute("ALTER TABLE economy ADD COLUMN last_claim_time TEXT DEFAULT '2000-01-01 00:00:00'")
    db_connection.commit()
    print("Added 'last_claim_time' column to user_economy.")
except _sqlite3.OperationalError as e:
    # This error occurs if the column already exists
    if "duplicate column name" not in str(e):
        raise

# Commit the changes to the database              
db_connection.commit()

# ------------------------------------- BOT SETUP ------------------------------------- #

# Defining intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix='sc~', intents=intents)

bot.db_connection = db_connection
bot.db_cursor = db_cursor

@bot.event
async def on_ready():
    """Confirms the bot is logged in and ready."""
    print(f'{bot.user.name} has connected to Discord!')
    
    try:
        # Load the spawning Cog
        await bot.load_extension('cogs.spawning')
        # Load the economy Cog
        await bot.load_extension('cogs.economy')
        # Load the info Cog
        await bot.load_extension('cogs.info')
        # Load the utility Cog
        await bot.load_extension('cogs.utility')
        print("All Cogs loaded successfully!")
    except Exception as e:
        print(f"Failed to load a Cog: {e}")

bot.run(TOKEN)
