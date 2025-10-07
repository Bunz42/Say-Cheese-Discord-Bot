from discord.ext import commands
import discord
import datetime # Used to check 24-hour cooldown on the daily cmd.

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Storing db objects from bot.py.
        self.conn =bot.db_connection
        self.c = bot.db_cursor

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

    '''Command for the user to check their own balance'''
    # @commands.command(name='balance', aliases=['bal'])
    # async def check_balance(self, ctx):
    #     user_id = ctx.author.id
    #     self.c.execute("SELECT balance FROM economy WHERE user_id = ?", (user_id,))
    #     balance = self.c.fetchone()
    #     await ctx.send(f"💰 {ctx.author.mention} your balance is: {balance}")

async def setup(bot):
    await bot.add_cog(Economy(bot))