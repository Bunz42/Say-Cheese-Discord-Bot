'''This cog handles user economy features such as currency balance, daily rewards, and inventory management.'''

from discord.ext import commands
import discord
import datetime # Used to check 24-hour cooldown on the daily cmd.

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Storing db objects from bot.py.
        self.conn =bot.db_connection
        self.c = bot.db_cursor

    # ------------------------------------- DAILY TOKEN CLAIM COMMAND ------------------------------------- #
    @commands.command(name='daily')
    async def daily_claim(self, ctx):
        '''Allows users to claim their fair share of daily currency!'''
        user_id = ctx.author.id
        reward = 500

        # Look up user's balance and last claim time
        self.c.execute("SELECT balance, last_claim_time FROM economy WHERE user_id = ?", (user_id,))
        user_data = self.c.fetchone()

        # Handling a new user
        if user_data == None:
            # Inserting a new record for new users with a default balance of 0
            initial_claim_time = datetime.datetime.min.strftime("%Y-%m-%d %H:%M:%S")
            self.c.execute("INSERT INTO economy (user_id, balance, last_claim_time) VALUES (?, ?, ?)", 
                           (user_id, 0, initial_claim_time))
            self.conn.commit()

            # Re-fetch the data after adding the new user
            self.c.execute("SELECT balance, last_claim_time FROM economy WHERE user_id = ?", (user_id,))
            user_data = self.c.fetchone()

        balance, last_claim_str = user_data

        # Checking the 24hr cooldown of the daily command
        last_claim_time = datetime.datetime.strptime(last_claim_str, "%Y-%m-%d %H:%M:%S")
        cooldown_end = last_claim_time + datetime.timedelta(hours=24)
        time = datetime.datetime.now()

        if time < cooldown_end:
            time_remaning = cooldown_end - time
            # Calculating the remaning hours and minutes before the user can execut the command again
            hours, remainder = divmod(time_remaning.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)

            return await ctx.send(f"{ctx.author.mention} You've already claimed you're daily reward! Please wait **{int(hours)}hrs and {int(minutes)}min**"
                                  " before using this command again.")
        
        # If the cmd isn't on cooldown, then the user gets the reward
        new_balance = balance + reward
        new_claim_time = time.strftime("%Y-%m-%d %H:%M:%S")

        # SQL statement to update the user database
        self.c.execute("UPDATE economy SET balance = ?, last_claim_time = ? WHERE user_id = ?", 
                       (new_balance, new_claim_time, user_id))
        self.conn.commit()

        await ctx.send(f"💰 {ctx.author.mention} Daily Reward claimed! You earned **{reward} currency**. Your new balance is **{new_balance}**.")

    # ------------------------------------- CHECK BALANCE COMMAND ------------------------------------- #
    @commands.command(name='balance', aliases=['bal'])
    async def check_balance(self, ctx):
        user_id = ctx.author.id

        # Query the database for the user's balance
        self.c.execute("SELECT balance FROM economy WHERE user_id = ?", (user_id,))
        balance = self.c.fetchone()

        if balance is None:
            # User has no record in the economy table
            return await ctx.send(f"💰 {ctx.author.mention} you have no economy profile yet! Try running 'sc~daily' to create one!")

        balance = balance[0]  # Extract the balance from the tuple (the fetchone() method returns a tuple)

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Balance", 
            description=f"You have {balance} tokens.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.add_field(name="Token Balance", value=f"{balance}", inline=False)
        await ctx.send(embed=embed)

# ------------------------------------- COG SETUP ------------------------------------- #
async def setup(bot):
    await bot.add_cog(Economy(bot))
