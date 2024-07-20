import random
import os

import discord
from discord.ext import commands
from discord.ext.commands.errors import BadArgument
from modules.economy import Economy
from modules.helpers import (
    DEFAULT_BET,
    InsufficientFundsException,
    make_embed,
    ABS_PATH,
)


class Gambling(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.economy = Economy()

    def check_bet(
        self,
        ctx: commands.Context,
        bet: int = DEFAULT_BET,
    ):
        bet = int(bet)
        if bet <= 0:
            raise commands.errors.BadArgument()
        current = self.economy.get_entry(ctx.author.id)[1]
        if bet > current:
            raise InsufficientFundsException(current, bet)

    @commands.command(
        brief="Flip a coin\nBet must be greater than $0",
        usage=f"flip [heads|tails] *[bet- default=${DEFAULT_BET}]",
    )
    async def flip(self, ctx: commands.Context, choice: str, bet: int = DEFAULT_BET):
        self.check_bet(ctx, bet)
        choices = {"h": "Heads", "t": "Tails"}
        choice = choice.lower()[0]
        if choice in choices.keys():
            result = random.choice(list(choices.keys()))
            won = result == choice

            if won:
                self.economy.add_money(ctx.author.id, bet)
                color = discord.Color.green()
                title = "You Won!"
                description = (
                    f"The coin landed on **{choices[result]}**!\nYou won ${bet}."
                )
            else:
                self.economy.add_money(ctx.author.id, bet * -1)
                color = discord.Color.red()
                title = "You Lost..."
                description = (
                    f"The coin landed on **{choices[result]}**.\nYou lost ${bet}."
                )

            embed = make_embed(title=title, description=description, color=color)
            embed.add_field(name="Your Choice", value=choices[choice], inline=True)
            embed.add_field(name="Result", value=choices[result], inline=True)
            embed.add_field(
                name="New Balance",
                value=f"${self.economy.get_entry(ctx.author.id)[1]}",
                inline=False,
            )

            # Add the coin image to the embed
            image_path = os.path.join(
                ABS_PATH, "modules", "ht", f"{choices[result].lower()}.png"
            )
            file = discord.File(image_path, filename=f"{choices[result].lower()}.png")
            embed.set_image(url=f"attachment://{choices[result].lower()}.png")

            await ctx.reply(embed=embed, file=file)
        else:
            raise BadArgument()

    @commands.command(
        brief="Roll 1 die\nBet must be greater than $0",
        usage=f"roll [guess:1-6] [bet- default=${DEFAULT_BET}]",
    )
    async def roll(self, ctx: commands.Context, choice: int, bet: int = DEFAULT_BET):
        self.check_bet(ctx, bet)
        choices = range(1, 7)
        if choice in choices:
            result = random.choice(choices)
            won = result == choice

            if won:
                self.economy.add_money(ctx.author.id, bet * 6)
                color = discord.Color.green()
                title = "You Won!"
                description = f"The die landed on **{result}**!\nYou won ${bet * 6}."
            else:
                self.economy.add_money(ctx.author.id, bet * -1)
                color = discord.Color.red()
                title = "You Lost..."
                description = f"The die landed on **{result}**.\nYou lost ${bet}."

            embed = make_embed(title=title, description=description, color=color)
            embed.add_field(name="Your Choice", value=choice, inline=True)
            embed.add_field(name="Result", value=result, inline=True)
            embed.add_field(
                name="New Balance",
                value=f"${self.economy.get_entry(ctx.author.id)[1]}",
                inline=False,
            )

            await ctx.reply(embed=embed)
        else:
            raise BadArgument()


async def setup(client: commands.Bot):
    await client.add_cog(Gambling(client))
