'''This cog provides detailed information about collectible rats in the game.'''


from discord.ext import commands
import discord
from data.rat_data import COLLECTIBLE_DATA, RARITY_COLORS

class RatInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = bot.db_cursor

    # ------------------------------------- RAT INFO COMMAND ------------------------------------- #
    @commands.command(name='info')
    async def rat_info(self, ctx):
        '''Display detailed information about the currently equipped rat.'''
        
        user_id = ctx.author.id

        self.cursor.execute("SELECT id, rat_name, level FROM rats WHERE user_id = ? AND equipped = 1", (user_id,))
        equipped_rat = self.cursor.fetchone()

        if equipped_rat is None:
            return await ctx.send(f"{ctx.author.mention} You don't have a photo equipped! Use `sc~equip <photo-number>` to bring one to life!")

        rat_id, rat_name, rat_level = equipped_rat

        # Find the rat's number in the user's collection
        self.cursor.execute("SELECT id FROM rats WHERE user_id = ? ORDER BY id", (user_id,))
        all_rat_ids = [row[0] for row in self.cursor.fetchall()]
        rat_number = all_rat_ids.index(rat_id) + 1

        # Find the rat data
        rat_data = None
        for rat in COLLECTIBLE_DATA:
            if rat['name'].lower() == rat_name.lower():
                rat_data = rat
                break

        if rat_data is None:
            return await ctx.send(f"{ctx.author.mention} Error: Rat data for **{rat_number}** not found!")
        
        # Get rarity color
        color = discord.Color(RARITY_COLORS.get(rat_data['rarity'], 0x0099ff))
        
        # Get spawn rate percentage
        spawn_rates = {
            "Common": "94.5%",
            "Elite": "5%",
            "Legendary": "0.5%"
        }
        spawn_rate = spawn_rates.get(rat_data['rarity'], "Unknown")
        
        # Create the info embed
        embed = discord.Embed(
            title=f"✨ Your Equipped Rat",
            description=f"**{rat_data['name']}** (Number: {rat_number})\n*{rat_data['description']}*",
            color=color
        )
        
        # Add rat image if available
        if rat_data['image_url']:
            embed.set_image(url=rat_data['image_url'])
        
        # Add information fields
        embed.add_field(name="📊 Rarity", value=rat_data['rarity'], inline=True)
        embed.add_field(name="📊 Level", value=f"{rat_level}", inline=True)
        embed.add_field(name="🎯 Spawn Rate", value=spawn_rate, inline=True)
        embed.add_field(name="💰 Token Drop", value=f"{rat_data['drop'][0]} - {rat_data['drop'][1]} tokens", inline=True)
        embed.add_field(name="📸 Photo Number", value=f"#{rat_number}", inline=True)
        embed.add_field(name="🗓️ Status", value="Currently Equipped", inline=True)
        
        # Check how many of this rat type the user has
        self.cursor.execute("SELECT COUNT(*) FROM rats WHERE user_id = ? AND rat_name = ?", 
                           (user_id, rat_data['name']))
        caught_count = self.cursor.fetchone()[0]
        
        embed.add_field(name="📸 Collection", value=f"You have {caught_count} photo{'s' if caught_count != 1 else ''} of this rat type!", inline=False)
        
        embed.set_footer(text=f"Use 'sc~unequip' to unequip this rat or 'sc~equip <number>' to switch to another!")
        await ctx.send(embed=embed)

# ------------------------------------- COG SETUP ------------------------------------- #
async def setup(bot):
    await bot.add_cog(RatInfo(bot))
