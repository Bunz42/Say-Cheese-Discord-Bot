# cogs/spawning.py
from discord.ext import commands, tasks
import discord 
import random

SPAWN_CHANNEL_ID = 1423174402673086467  # <<< You MUST replace this number!

COLLECTIBLE_DATA = [
    {
        "name": "Disco Rat",
        "rarity": "Rare",
        "image_url": "", # Placeholder URL
        "catch_rate": 45
    },
    {
        "name": "Quantum Rat",
        "rarity": "Legendary",
        "image_url": "", # Placeholder URL
        "catch_rate": 5
    },
    {
        "name": "Rat",
        "rarity": "Common",
        "image_url": "", # Placeholder URL
        "catch_rate": 90
    }
]

class Spawning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_rat = None # This variable can track the rat that's currently spawned in the chat

        # Starts the loop as soon as the bot connects
        self.spawn_collectible.start() 

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
            embed.set_footer(text=f"Rarity: {collectible['rarity']} | Capture Rate: {collectible['catch_rate']}%")

            # Send a test message asynchronously
            await channel.send(embed=embed)

    @commands.command(name='spawninfo')
    async def spawn_info(self, ctx):
        """A simple test command for the cog."""
        await ctx.send("Spawning Cog is active and running!")

    # Define a command to capture the rat and add it to the user's collection
    @commands.command(name='capture')
    async def capture(self, ctx):
        # Perform a check to see if there's an active rat to capture
        if self.active_rat is None:
            await ctx.send("There is no rat to capture right now!")
            return

        # TODO: Perform a check to see if the user is in the correct channel (omit for now)

        caught_rat = self.active_rat  # The rat the user is trying to catch

        '''Capture Logic: Chance-based capture based on the rat's catch rate'''
        rate = self.active_rat['catch_rate']
        roll = random.randint(1, 100)

        if roll <= rate:
            # Capture successful
            await ctx.send(f"🎉 {ctx.author.mention} has successfully snapped a photo of {caught_rat['name']}!")
        else:
            # Capture failed
            await ctx.send(f"😢 {ctx.author.mention} failed to snap a photo of {caught_rat['name']}. The rat ran away!")

        self.active_rat = None  # Reset the active rat since it has been attempted to be captured

    def cog_unload(self):
        """Ensures the background task is stopped when the cog is removed."""
        self.spawn_collectible.cancel()

# Function to load the cog into the bot (discord automatically looks for this when load_extension is called)
async def setup(bot):
    """The required function to load the cog into the bot."""
    await bot.add_cog(Spawning(bot))