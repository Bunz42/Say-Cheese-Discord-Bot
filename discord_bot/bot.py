import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import _sqlite3

# Load the environment variables from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# -----------------DATABASE SETUP-----------------
# Establish a connection to the SQLite database
db_connection = _sqlite3.connect('rat_collection.db')
db_cursor = db_connection.cursor()

# Create a table to store captured rats if it doesn't already exist
db_cursor.execute('''
CREATE TABLE IF NOT EXISTS rats (
    user_id INTEGER,
    rat_name TEXT,
    captured_at TEXT
)
''')
db_connection.commit()

# print("\n--- INVENTORY CONTENTS CHECK ---")
# # Execute the select statement
# db_cursor.execute("SELECT * FROM rats")

# # Loop through all the rows returned and print them
# for row in db_cursor.fetchall():
#     print(row)
# print("--------------------------------\n")

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
    
    # NEW: Load our cog right after the bot connects!
    try:
        await bot.load_extension('cogs.spawning')
        print("Spawning Cog loaded successfully and DB objects passed!")
    except Exception as e:
        print(f"Failed to load Spawning Cog: {e}")

bot.run(TOKEN)
