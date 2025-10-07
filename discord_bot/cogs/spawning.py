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
        "spawn_rate": 0 #temp
    },
    {
        "name": "Quantum Rat",
        "rarity": "Legendary",
        "image_url": "", 
        "spawn_rate": 0 #temp
    },
    {
        "name": "Rat",
        "rarity": "Common",
        "image_url": "", 
        "spawn_rate": 0 #temp
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

    # ----------------- COLLECTIBLE SPAWNING -------------------
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

        # Handles adding the rat into the user's rat database
        sql = "INSERT INTO rats (user_id, rat_name, captured_at) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (user_id, item_name, caught_time))
        self.conn.commit()

        await ctx.send(f"🎉 {ctx.author.mention} took a photo of {caught_rat['name']}!")
        self.active_rat = None  # Reset the active rat since it has been attempted to be captured

    @commands.command(name='myrats', aliases=['rats'])
    async def view_rats(self, ctx):
        '''Command to display the user's captured rats.'''

        user_id = ctx.author.id

        # SQL Query: Selects item name and counts them, filtered by user ID
        # ORDER BY COUNT(*) DESC ensures the items with the most quantity are at the top
        sql = "SELECT rat_name, COUNT(*) FROM rats WHERE user_id = ? GROUP BY rat_name ORDER BY COUNT(*) DESC"

        # Execute the query, passing the user ID as a parameter
        self.cursor.execute(sql, (user_id,))

        # Fetch all results: Returns a list of tuples (('Item Name', count), ...)
        my_rats = self.cursor.fetchall()

        if not my_rats:
            return await ctx.send(f"{ctx.author.mention}, you have no photos!")
        
        # Format the rat inventory for the discord embed
        rat_list = []
        num_of_rats = 0;
        for (rat, count) in my_rats:
            rat_list.append(f"• **{rat}** x{count}")
            num_of_rats += count

        # Create the embed
        embed = discord.Embed(
            title=f"🎒 {ctx.author.name}'s Photo Board",
            description="\n".join(rat_list), # Joins the list items into a clean block of text
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Total Photos: {num_of_rats}")
        await ctx.send(embed=embed)

    def cog_unload(self):
        """Ensures the background task is stopped when the cog is removed."""
        self.spawn_collectible.cancel()

# Function to load the cog into the bot (discord automatically looks for this when load_extension is called)
async def setup(bot):
    await bot.add_cog(Spawning(bot))
