import discord
from discord.ext import commands
from modules.economy import Economy
from modules.helpers import *


class GamblingHelpers(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.economy = Economy()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def set(
        self,
        ctx: commands.Context,
        user_id: int = None,
        money: int = 0,
        credits: int = 0,
    ):
        if money:
            self.economy.set_money(user_id, money)
        if credits:
            self.economy.set_credits(user_id, credits)

    @commands.command(
        brief=f"Gives you ${DEFAULT_BET*B_MULT} once every {B_COOLDOWN}hrs",
        usage="work",
        aliases=["w"],
    )
    @commands.cooldown(1, B_COOLDOWN * 3600, type=commands.BucketType.user)
    async def work(self, ctx: commands.Context):
        amount = DEFAULT_BET * B_MULT
        self.economy.add_money(ctx.author.id, amount)
        await ctx.reply(f"Added ${amount} come back in {B_COOLDOWN}hrs")

    @commands.command(
        brief="How much money you or someone else has",
        usage="money *[@member]",
        aliases=["credits", "m"],
    )
    async def money(self, ctx: commands.Context, user: discord.Member = None):
        user_id = user.id if user else ctx.author.id
        user = self.client.get_user(user_id) or await self.client.fetch_user(user_id)

        profile = self.economy.get_entry(user.id)
        embed = make_embed(
            title=user.name,
            description=(
                "**${:,}**".format(profile[1]) + "\n**{:,}** credits".format(profile[2])
            ),
            footer=None,
        )
        embed.set_thumbnail(url=user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.command(
        brief="Shows the user with the most money",
        usage="leaderboard",
        aliases=["top", "lb"],
    )
    async def leaderboard(self, ctx: commands.Context):
        entries = self.economy.top_entries(5)
        embed = make_embed(title="Leaderboard:", color=discord.Color.gold())
        for i, entry in enumerate(entries):
            user = self.client.get_user(entry[0]) or await self.client.fetch_user(
                entry[0]
            )
            embed.add_field(
                name=f"{i+1}. {user.name}",
                value="${:,}".format(entry[1]),
                inline=False,
            )
        await ctx.reply(embed=embed)

    @commands.command(
        brief="Give money to another user", usage="give @user amount", aliases=["g"]
    )
    async def give(self, ctx: commands.Context, user: discord.Member, amount: int):
        if amount <= 0:
            embed = make_embed(
                title="Error",
                description="Amount must be a positive number.",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            return

        giver_id = ctx.author.id
        receiver_id = user.id

        if giver_id == receiver_id:
            embed = make_embed(
                title="Error",
                description="You cannot give money to yourself.",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            return

        giver_profile = self.economy.get_entry(giver_id)
        if giver_profile[1] < amount:
            embed = make_embed(
                title="Error",
                description="You do not have enough money to give.",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            return

        self.economy.add_money(giver_id, -amount)
        self.economy.add_money(receiver_id, amount)

        embed = make_embed(
            title="Success",
            description=f"Gave ${amount:,} to {user.mention}.",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)

    @commands.command(brief="Sell a kidney for $10,000", usage="sellk", aliases=["sk"])
    async def sellk(self, ctx: commands.Context):
        user_id = ctx.author.id
        entry = self.economy.get_entry(user_id)

        if entry[3] > 0:
            new_entry = self.economy.remove_kidney(user_id)
            kidneys_left = new_entry[3]
            money = new_entry[1]

            if kidneys_left == 1:
                title = "Kidney Sold"
                description = f"You sold a kidney for $10,000. You now have ${money:,} and 1 kidney left. Be careful!"
                color = discord.Color.orange()
            else:
                title = "Last Kidney Sold"
                description = f"You sold your last kidney for $10,000. You now have ${money:,}. I hope it was worth it!"
                color = discord.Color.red()

            embed = make_embed(title=title, description=description, color=color)
            await ctx.reply(embed=embed)
        else:
            embed = make_embed(
                title="No Kidneys Left",
                description="You don't have any kidneys left to sell!",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)

    @commands.command(
        brief="Check how many kidneys you have left", usage="kidneys", aliases=["k"]
    )
    async def kidneys(self, ctx: commands.Context):
        user_id = ctx.author.id
        entry = self.economy.get_entry(user_id)
        kidneys_left = entry[3]

        if kidneys_left == 2:
            title = "Healthy Kidneys"
            description = "You have both of your kidneys."
            color = discord.Color.green()
        elif kidneys_left == 1:
            title = "One Kidney Left"
            description = "You have one kidney left. Think carefully before selling it!"
            color = discord.Color.orange()
        else:
            title = "No Kidneys"
            description = "You have no kidneys left. How are you still alive?"
            color = discord.Color.red()

        embed = make_embed(title=title, description=description, color=color)
        await ctx.reply(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(GamblingHelpers(client))
