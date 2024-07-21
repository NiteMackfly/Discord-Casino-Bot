import asyncio
import io
import os
import random
from typing import List, Tuple
import math

import discord
from discord.ext import commands
from discord.ui import View, Button
from modules.economy import Economy
from modules.helpers import *
from PIL import Image, ImageDraw, ImageFont


class RouletteView(View):
    def __init__(self, game, bet, ctx):
        super().__init__()
        self.game = game
        self.bet = bet
        self.ctx = ctx
        self.value = None
        self.user_id = ctx.author.id  # Store the user ID

    @discord.ui.button(label="Spin Again", style=discord.ButtonStyle.primary)
    async def spin_again(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You are not authorized to use this button.", ephemeral=True
            )
            return
        await interaction.response.defer()
        self.value = "spin_again"
        self.stop()


class Roulette(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.economy = Economy()
        self.wheel_numbers = [
            0,
            32,
            15,
            19,
            4,
            21,
            2,
            25,
            17,
            34,
            6,
            27,
            13,
            36,
            11,
            30,
            8,
            23,
            10,
            5,
            24,
            16,
            33,
            1,
            20,
            14,
            31,
            9,
            22,
            18,
            29,
            7,
            28,
            12,
            35,
            3,
            26,
        ]

    def check_bet(self, ctx: commands.Context, bet: int = DEFAULT_BET):
        bet = int(bet)
        if bet <= 0:
            raise commands.errors.BadArgument()
        current = self.economy.get_entry(ctx.author.id)[1]
        if bet > current:
            raise InsufficientFundsException(current, bet)

    def create_roulette_image(self, result: int) -> io.BytesIO:
        # Load images
        table = Image.open(
            os.path.join(ABS_PATH, "modules/roulette/roulette_table.png")
        ).convert("RGBA")

        # Create a new image with table as background
        base_image = Image.new("RGBA", table.size, (0, 0, 0, 0))
        base_image.paste(table, (0, 0))

        # Draw the result number on the image
        draw = ImageDraw.Draw(base_image)
        font = ImageFont.load_default()
        text = str(result)

        # Change: Use textbbox instead of textsize
        bbox = draw.textbbox((0, 0), text, font=font)  # Get bounding box of the text
        text_width = bbox[2] - bbox[0]  # Calculate width from bbox
        text_height = bbox[3] - bbox[1]  # Calculate height from bbox

        # Draw the text on the image
        draw.text(
            (
                (base_image.width - text_width) / 2,
                (base_image.height - text_height) / 2,
            ),
            text,
            font=font,
            fill=(255, 0, 0),
        )
        # Save image to BytesIO object
        img_byte_arr = io.BytesIO()
        base_image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return img_byte_arr

    @commands.command(
        brief="Play roulette\nBet must be greater than $0",
        usage="roulette [bet] [choice]",
        aliases=["rl", "r"],
    )
    async def roulette(self, ctx: commands.Context, bet: int, choice: str):
        self.check_bet(ctx, bet)

        choices = {
            "red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
            "r": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
            "black": [
                2,
                4,
                6,
                8,
                10,
                11,
                13,
                15,
                17,
                20,
                22,
                24,
                26,
                28,
                29,
                31,
                33,
                35,
            ],
            "b": [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
            "even": list(range(2, 37, 2)),
            "e": list(range(2, 37, 2)),
            "odd": list(range(1, 37, 2)),
            "o": list(range(1, 37, 2)),
            "low": list(range(1, 19)),
            "high": list(range(19, 37)),
            "l": list(range(1, 19)),
            "h": list(range(19, 37)),
        }

        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice <= 36:
                choices[str(choice)] = [choice]
            else:
                raise commands.errors.BadArgument()
        elif choice.lower() not in choices:
            raise commands.errors.BadArgument()

        result = random.choice(self.wheel_numbers)

        won = (isinstance(choice, str) and result in choices[choice.lower()]) or (
            isinstance(choice, int) and result == choice
        )

        multiplier = 35 if isinstance(choice, int) else 1

        if won:
            self.economy.add_money(ctx.author.id, bet * multiplier)
            color = discord.Color.green()
            title = "You Won!"
            description = (
                f"The ball landed on **{result}**!\nYou won ${bet * multiplier}."
            )
        else:
            self.economy.add_money(ctx.author.id, bet * -1)
            color = discord.Color.red()
            title = "You Lost..."
            description = f"The ball landed on **{result}**.\nYou lost ${bet}."

        # Create the roulette image in memory
        img_byte_arr = self.create_roulette_image(result)

        embed = make_embed(title=title, description=description, color=color)
        embed.add_field(
            name="New Balance",
            value=f"${self.economy.get_entry(ctx.author.id)[1]}",
            inline=False,
        )

        file = discord.File(fp=img_byte_arr, filename="roulette_result.png")
        embed.set_image(url="attachment://roulette_result.png")

        view = RouletteView(self, bet, ctx)
        msg = await ctx.reply(file=file, embed=embed, view=view)
        del img_byte_arr, file

        await view.wait()

        if view.value == "spin_again":
            await msg.delete()
            await ctx.invoke(self.roulette, bet=bet, choice=choice)


async def setup(client: commands.Bot):
    await client.add_cog(Roulette(client))
