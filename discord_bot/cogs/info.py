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
    async def rat_info(self, ctx, *, rat_name=None):
        '''Display detailed information about a specific rat.'''
        
        if rat_name is None:
            # Show available rats if no name is provided
            available_rats = [rat['name'] for rat in COLLECTIBLE_DATA]
            embed = discord.Embed(
                title="🐭 Available Rats",
                description="Use `sc~info <rat name>` to get detailed information about a rat.\n\n**Available rats:**\n" + 
                           "\n".join([f"• {rat}" for rat in available_rats]),
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)
        
        # Find the rat by name (case-insensitive)
        rat_data = None
        for rat in COLLECTIBLE_DATA:
            if rat['name'].lower() == rat_name.lower():
                rat_data = rat
                break
        
        if rat_data is None:
            available_rats = [rat['name'] for rat in COLLECTIBLE_DATA]
            embed = discord.Embed(
                title="❌ Rat Not Found",
                description=f"Could not find a rat named '{rat_name}'.\n\n**Available rats:**\n" + 
                           "\n".join([f"• {rat}" for rat in available_rats]),
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
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
            title=f"🐭 {rat_data['name']}",
            description=f"*{rat_data['description']}*",
            color=color
        )
        
        # Add rat image if available
        if rat_data['image_url']:
            embed.set_image(url=rat_data['image_url'])
        
        # Add information fields
        embed.add_field(name="📊 Rarity", value=rat_data['rarity'], inline=True)
        embed.add_field(name="🎯 Spawn Rate", value=spawn_rate, inline=True)
        embed.add_field(name="💰 Token Drop", value=f"{rat_data['drop'][0]} - {rat_data['drop'][1]} tokens", inline=True)
        
        # Check if user has caught this rat
        user_id = ctx.author.id
        self.cursor.execute("SELECT COUNT(*) FROM rats WHERE user_id = ? AND rat_name = ?", 
                           (user_id, rat_data['name']))
        caught_count = self.cursor.fetchone()[0]
        
        if caught_count > 0:
            embed.add_field(name="📸 Your Photos", value=f"You have {caught_count} photo{'s' if caught_count != 1 else ''} of this rat!", inline=False)
        else:
            embed.add_field(name="📸 Your Photos", value="You haven't captured this rat yet!", inline=False)
        
        embed.set_footer(text=f"Use 'sc~capture' when this rat spawns to add it to your collection!")
        await ctx.send(embed=embed)

# ------------------------------------- COG SETUP ------------------------------------- #
async def setup(bot):
    await bot.add_cog(RatInfo(bot))