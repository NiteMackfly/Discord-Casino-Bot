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
        usage="add",
        aliases=["w", "work"],
    )
    @commands.cooldown(1, B_COOLDOWN * 3600, type=commands.BucketType.user)
    async def add(self, ctx: commands.Context):
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


async def setup(client: commands.Bot):
    await client.add_cog(GamblingHelpers(client))
