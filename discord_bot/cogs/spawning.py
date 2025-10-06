# cogs/spawning.py
from discord.ext import commands, tasks
import discord 
import random
import datetime

SPAWN_CHANNEL_ID = 1423174402673086467  # <<< You MUST replace this number!

COLLECTIBLE_DATA = [
    {
        "name": "Disco Rat",
        "rarity": "Rare",
        "image_url": "", 
        "catch_rate": 45
    },
    {
        "name": "Quantum Rat",
        "rarity": "Legendary",
        "image_url": "", 
        "catch_rate": 5
    },
    {
        "name": "Rat",
        "rarity": "Common",
        "image_url": "", 
        "catch_rate": 90
    }
]

class Spawning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Access the database connection and cursor from the bot instance
        self.conn = bot.db_connection
        self.cursor = bot.db_cursor

        self.active_rat = None # This variable can track the rat that's currently spawned in the chat

        # Starts the loop as soon as the bot connects
        self.spawn_collectible.start() 

    # ----------------- COLLECTIBLE SPAWNING -----------------
    @tasks.loop(seconds=20) # Adjust the interval as needed
    async def spawn_collectible(self):
        """The main loop that handles collectible spawning."""
        
        # Get the channel object using its ID
        channel = self.bot.get_channel(SPAWN_CHANNEL_ID)
        
        # Check if the channel exists before trying to send a message
        if channel:
            collectible = random.choice(COLLECTIBLE_DATA)

            self.active_rat = collectible # Track the currently spawned rat

            # Make the discord embed
            embed = discord.Embed(
                title="A Rat Appeared!",
                description=f"It's a **{collectible['name']}**!",
                color=discord.Color.dark_teal()
            )

            embed.set_image(url=collectible['image_url'])
            embed.set_footer(text=f"Rarity: {collectible['rarity']} | Quick! Type sc~capture to take a photo!")

            # Send a test message asynchronously
            await channel.send(embed=embed)

    # Define a command to capture the rat and add it to the user's collection
    @commands.command(name='capture')
    async def capture(self, ctx):
        # Perform a check to see if there's an active rat to capture
        if self.active_rat is None:
            await ctx.send("There is no rat to capture right now!")
            return

        # TODO: Perform a check to see if the user is in the correct channel (omit for now)

        caught_rat = self.active_rat  # The rat the user is trying to catch

        '''Capture Logic'''
        caught_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id = ctx.author.id
        item_name = caught_rat['name']

        sql = "INSERT INTO rats (user_id, rat_name, captured_at) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (user_id, item_name, caught_time))
        self.conn.commit()

        await ctx.send(f"🎉 {ctx.author.mention} took a photo of {caught_rat['name']}!")
        self.active_rat = None  # Reset the active rat since it has been attempted to be captured

    @commands.command(name='myrats')
    async def myrats(self, ctx):
        '''Command to display the user's captured rats.'''
        await ctx.send(f"Inventory command received for {ctx.author.mention}! (Database lookup will go here)")

    def cog_unload(self):
        """Ensures the background task is stopped when the cog is removed."""
        self.spawn_collectible.cancel()

# Function to load the cog into the bot (discord automatically looks for this when load_extension is called)
async def setup(bot):
    await bot.add_cog(Spawning(bot))
