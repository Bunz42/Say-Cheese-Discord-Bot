'''This cog handles the spawning of collectible rats in a designated Discord channel.
It includes logic for random spawning based on rarity, user interaction to capture
the rats, and viewing the user's collection.'''

# cogs/spawning.py
from discord.ext import commands
import discord 
import random
import datetime
from data.rat_data import COLLECTIBLE_DATA

SPAWN_CHANNEL_ID = 1423174402673086467  # <<< You MUST replace this number!

class Spawning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Access the database connection and cursor from the bot instance
        self.conn = bot.db_connection
        self.cursor = bot.db_cursor

        self.active_rat = None # This variable can track the rat that's currently spawned in the chat
        self.rat_spawner_id = None # Variable to track who spawned the rat

        self.message_count = 0 # Tracks the number of messages sent in the channel
        self.spawn_threshold = 1 # Number of messages before a rat spawns


    # Define a function that listens to messages in the specified channel
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages and messages outside the spawn channel
        if message.author.bot or message.channel.id != SPAWN_CHANNEL_ID:
            return
        
        # Ignore command messages (messages that start with the bot's prefix)
        if message.content.startswith(self.bot.command_prefix):
            return
        
        # Don't count messages when there's already an active rat
        if self.active_rat is not None:
            return
        
        # Increment message count
        self.message_count += 1
        
        # Check if we've reached the spawn threshold
        if self.message_count >= self.spawn_threshold:
            await self.spawn_collectible()
            # Reset counter and set new threshold
            self.message_count = 0
            # self.spawn_threshold = random.randint(20, 50)

    # ------------------------------------- COLLECTIBLE SPAWNING ------------------------------------- #
    async def spawn_collectible(self):
        """The main loop that handles collectible spawning."""
        
        # Get the channel object using its ID
        channel = self.bot.get_channel(SPAWN_CHANNEL_ID)
        
        # Check if the channel exists before trying to send a message
        if channel:
            # Weighted random selection of a rat to spawn based on its rarity (0.5% Legendary, 5% Elite, 94.5% Common)
            collectible = self.select_rat_by_rarity()

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
    
    def select_rat_by_rarity(self):
        '''Selects a random rat from the COLLECTIBLE_DATA based on the specified rarity.'''
        # Generate a random real number between 0 and 100
        roll = random.random() * 100

        # 0.5% chance for Legendary
        if roll <= 0.5:
            legendary_rats = [rat for rat in COLLECTIBLE_DATA if rat['rarity'] == 'Legendary']
            return random.choice(legendary_rats) if legendary_rats else None
        
        # 5% chance for Elite (0.5% - 5.5% range to exclude overlap with Legendary)
        elif roll <= 5.5:
            elite_rats = [rat for rat in COLLECTIBLE_DATA if rat['rarity'] == 'Elite']
            return random.choice(elite_rats) if elite_rats else None
        
        # 94.5% chance for Common
        else:
            common_rats = [rat for rat in COLLECTIBLE_DATA if rat['rarity'] == 'Common']
            return random.choice(common_rats) if common_rats else None

    # ------------------------------------- COLLECTIBLE CAPTURE LOGIC ------------------------------------- #

    # Define a command to capture the rat and add it to the user's collection
    @commands.command(name='capture')
    async def capture(self, ctx):
        # Perform a check to see if there's an active rat to capture
        if self.active_rat is None:
            await ctx.send("There is no rat to capture right now!")
            return

        # TODO: Perform a check to see if the user is in the correct channel (omit for now)
        if ctx.channel.id != SPAWN_CHANNEL_ID:
            await ctx.send(f"{ctx.author.mention} You can only capture rats in the designated channel!")
            return
        
        # If the rat was spawned by a user, only that user can capture it
        if self.rat_spawner_id is not None and ctx.author.id != self.rat_spawner_id:
            spawner = await self.bot.fetch_user(self.rat_spawner_id)
            spawner_name = spawner.display_name if spawner else "someone else"
            await ctx.send(f"{ctx.author.mention} You can't capture this rat! It was spawned by {spawner_name}.")
            return

        caught_rat = self.active_rat  # The rat the user is trying to catch

        '''Capture Logic'''
        caught_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id = ctx.author.id
        item_name = caught_rat['name']

        # Handles adding the rat into the user's rat database
        sql = "INSERT INTO rats (user_id, rat_name, level, captured_at) VALUES (?, ?, ?, ?)"
        self.cursor.execute(sql, (user_id, item_name, 1, caught_time))

        # When user captures a rat, they also get a small random amount of currency (a "drop")
        reward = random.randint(*caught_rat['drop'])  # Random reward in a range defined by the rat's drop range
        self.cursor.execute("UPDATE economy SET balance = balance + ? WHERE user_id = ?", (reward, user_id))

        self.conn.commit()

        await ctx.send(f"🎉 {ctx.author.mention} took a photo of {caught_rat['name']}! It dropped **{reward} tokens**.")
        self.active_rat = None  # Reset the active rat since it has been attempted to be captured

    # ------------------------------------- COLLECTIBLE INVENTORY ------------------------------------- #
    
    # Command to view the user's captured rats
    @commands.command(name='myrats', aliases=['rats'])
    async def view_rats(self, ctx):
        '''Command to display the user's captured rats.'''

        user_id = ctx.author.id

        # SQL Query: Selects all rats for the user, ordered by capture date (ID represents capture order)
        sql = "SELECT id, rat_name, level FROM rats WHERE user_id = ? ORDER BY id"

        # Execute the query, passing the user ID as a parameter
        self.cursor.execute(sql, (user_id,))

        # Fetch all results: Returns a list of tuples ((id, 'Rat Name', level), ...)
        my_rats = self.cursor.fetchall()

        if not my_rats:
            return await ctx.send(f"{ctx.author.mention}, you have no photos!")
        
        total_rats = len(my_rats)
        
        # Format the rat inventory for the discord embed
        rat_list = []
        for i, (rat_id, rat_name, level) in enumerate(my_rats, 1):
            rat_list.append(f"{rat_name} | Level: {level} | Number: {i}")

        # Create the embed
        embed = discord.Embed(
            title=f"🎒 {ctx.author.display_name}'s Photo Board",
            description="\n".join(rat_list), # Joins the list items into a clean block of text
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Total Photos: {total_rats}")
        await ctx.send(embed=embed)

    # ------------------------------------- RAT EQUIPMENT SYSTEM ------------------------------------- #

    @commands.command(name='equip')
    async def equip_rat(self, ctx, rat_number: int = None):
        '''Equips a captured rat by its number in the rat inventory.'''

        if rat_number is None:
            return await ctx.send(f"{ctx.author.mention} Please specify which photo to equip! Use `sc~myrats` to see your photos and their numbers! Example: `sc~equip 5`")
        
        user_id = ctx.author.id
        
        # Check if user has this rat in their collection
        self.cursor.execute("SELECT id, rat_name, level FROM rats WHERE user_id = ? ORDER BY id", (user_id,))
        my_rats = self.cursor.fetchall()

        if not my_rats:
            return await ctx.send(f"{ctx.author.mention} You don't have any photos! Catch some first using `sc~capture`!")
        
        if rat_number < 1 or rat_number > len(my_rats):
            return await ctx.send(f"{ctx.author.mention} Invalid photo number! You have {len(my_rats)} rats. Use `sc~myrats` to see your photos.")

        # Get the rat at the specified number
        rat_id, rat_name, level = my_rats[rat_number - 1]

        # Check if user already has this rat equipped
        self.cursor.execute("SELECT equipped FROM rats WHERE user_id = ?", (user_id,))
        is_equipped = self.cursor.fetchone()[0]
        
        if is_equipped:
            return await ctx.send(f"{ctx.author.mention} **{rat_name}** (Number: {rat_number}) is already equipped!")
        
        rat_data = None
        for rat in COLLECTIBLE_DATA:
            if rat['name'].lower() == rat_name.lower():
                rat_data = rat
                break
        
        if rat_data is None:
            return await ctx.send(f"{ctx.author.mention} Error: Rat data for **{rat_name}** not found!")

        # Unequip any currently equipped rat
        self.cursor.execute("UPDATE rats SET equipped = 0 WHERE user_id = ?", (user_id,))
        self.cursor.execute("UPDATE rats SET equipped = 1 WHERE id = ?", (rat_id,))
        self.conn.commit()

        # Create success embed
        from data.rat_data import RARITY_COLORS
        color = discord.Color(RARITY_COLORS.get(rat_data['rarity'], 0x0099ff))
        
        embed = discord.Embed(
            title="📸 Photo Equipped!",
            description=f"You have equipped **{rat_name}**!\n*The rat in this photo has been brought to life!*",
            color=color
        )
        
        if rat_data['image_url']:
            embed.set_thumbnail(url=rat_data['image_url'])
        
        embed.add_field(name="✨ Rarity", value=rat_data['rarity'], inline=True)
        embed.add_field(name="Level", value=f"{level}", inline=True)
        embed.set_footer(text="Use 'sc~info' to see your currently equipped rat!")
        
        await ctx.send(embed=embed)

# ------------------------------------- COG SETUP ------------------------------------- #
# Function to load the cog into the bot (discord automatically looks for this when load_extension is called)
async def setup(bot):
    await bot.add_cog(Spawning(bot))
