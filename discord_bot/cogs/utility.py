'''Utility commands for the bot.'''
from discord.ext import commands
import discord

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------- COMMAND LIST ------------------------------------- #
    @commands.command(name='commands', aliases=['cmd'])
    async def show_commands(self, ctx):
        '''Function to display and describe all available bot commands.'''

        embed = discord.Embed(
            title = "📸 🤖 Say Cheese Bot Commands",
            description = "Here are all the available commands: ",
            color = discord.Color.blue()
        )

        # Rat Collection Commands
        embed.add_field(
            name="📸 **Rat Collection**",
            value="`sc~capture` - Capture a spawned rat\n"
                    "`sc~myrats` - View your photo collection\n"
                    "`sc~equip <photo number>` - Bring a photo to life\n"
                    "`sc~equipped` - View equipped rat\n"
                    "`sc~unequip` - Unequip current rat\n"
                    "`sc~info` - See information about your equipped rat\n",
            inline=False
        )

        # Economy Commands
        embed.add_field(
            name="💰 **Economy**",
            value="`sc~daily` - Claim daily tokens\n"
                    "`sc~balance` - Check your token balance\n"
                    "`sc~market-list <rat name>` - Lists your rat on the market\n"
                    "`sc~market` - View the rat market",
            inline=False
        )

        # Utility Commands
        embed.add_field(
            name="🔧 **Utility**",
            value="`sc~commands` - Show this command list",
            inline=False
        )

        embed.set_footer(text="💡 Tip: Rats spawn when users chat in the designated channel!")
        await ctx.send(embed=embed)

# ------------------------------------- COG SETUP ------------------------------------- #
# Function to load the cog into the bot (discord automatically looks for this when load_extension is called)
async def setup(bot):
    await bot.add_cog(Utility(bot))
