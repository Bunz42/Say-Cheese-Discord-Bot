'''Utility commands for the bot.'''
from discord.ext import commands
import discord

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------- COMMAND LIST ------------------------------------- #
@commands.command(name='commands', aliases=['cmd', 'help'])
async def show_commands(self, ctx):
    '''Function to display and describe all available bot commands.'''

    embed = discord.Embed(
        title = "📸 🤖 Say Cheese Bot Commands",
        description = "Here are all the available commands: ",
        color = discord.Color.blue()
    )

    # Rat Collection Commands
    embed.add_field(
        title = "📸 **Rat Collection**",
        value = "`sc~capture` - Capture a spawned rat\n"
                "`sc~myrats, sc~rats` - Capture a spawned rat\n"
                "`sc~capture` - Capture a spawned rat\n"
                "`sc~capture` - Capture a spawned rat\n"
                "`sc~capture` - Capture a spawned rat\n"
                "`sc~capture` - Capture a spawned rat\n"
    )