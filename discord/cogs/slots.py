import asyncio
import bisect
import os
import random
import io

import discord
from discord.ext import commands
from discord.ui import View, Button
from modules.economy import Economy
from modules.helpers import *
from PIL import Image
from modules.exceptions import ActiveGameError


class SlotView(View):
    def __init__(self, game, bet, ctx):
        super().__init__(timeout=30)
        self.game = game
        self.bet = bet
        self.ctx = ctx
        self.value = None
        self.user_id = ctx.author.id
        self.message = None

    async def on_timeout(self) -> None:
        # Disable the button when the view times out
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You are not authorized to use this button.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="REROLL", style=discord.ButtonStyle.primary)
    async def reroll(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=None)
        self.value = "reroll"
        self.stop()

    async def start(self, message):
        self.message = message
        return self


class Slots(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.economy = Economy()
        self.active_players = set()

    def cog_check(self, ctx):
        if ctx.author.id in self.active_players:
            raise ActiveGameError("You have an ongoing game. Please finish it first.")
        return True

    def check_bet(self, ctx: commands.Context, bet: int = DEFAULT_BET):
        bet = int(bet)
        if bet <= 0 or bet > 3:
            raise commands.errors.BadArgument()
        current = self.economy.get_entry(ctx.author.id)[2]
        if bet > current:
            raise InsufficientFundsException(current, bet)

    @commands.command(
        brief="Slot machine\nbet must be 1-3",
        usage="slots *[bet]",
        aliases=["sl"],
    )
    async def slots(self, ctx: commands.Context, bet: int = 1):
        if ctx.author.id in self.active_players:
            await ctx.send(
                "You have an ongoing game. Please finish it first.", ephemeral=True
            )
            return

        self.active_players.add(ctx.author.id)

        async def play_slots(bet):
            self.check_bet(ctx, bet=bet)
            path = os.path.join(ABS_PATH, "modules/")
            facade = Image.open(f"{path}slot-face.png").convert("RGBA")
            reel = Image.open(f"{path}slot-reel.png").convert("RGBA")

            facade = facade.resize(
                (facade.width // 2, facade.height // 2), Image.LANCZOS
            )
            reel = reel.resize((reel.width // 2, reel.height // 2), Image.LANCZOS)

            rw, rh = reel.size
            item = 180
            items = rh // item

            s1 = random.randint(1, items - 1)
            s2 = random.randint(1, items - 1)
            s3 = random.randint(1, items - 1)

            win_rate = 12 / 100

            if random.random() < win_rate:
                symbols_weights = [3.5, 7, 15, 25, 55]
                x = round(random.random() * 100, 1)
                pos = bisect.bisect(symbols_weights, x)
                s1 = pos + (random.randint(1, (items / 6) - 1) * 6)
                s2 = pos + (random.randint(1, (items / 6) - 1) * 6)
                s3 = pos + (random.randint(1, (items / 6) - 1) * 6)
                s1 = s1 - 6 if s1 == items else s1
                s2 = s2 - 6 if s2 == items else s2
                s3 = s3 - 6 if s3 == items else s3

            images = []
            speed = 30
            for i in range(1, (item // speed) + 1):
                bg = Image.new("RGBA", facade.size, color=(255, 255, 255))
                bg.paste(reel, (25 + rw * 0, 100 - (speed * i * s1)))
                bg.paste(reel, (25 + rw * 1, 100 - (speed * i * s2)))
                bg.paste(reel, (25 + rw * 2, 100 - (speed * i * s3)))
                bg.alpha_composite(facade)
                images.append(bg)

            spinning_images = images[:-1]
            spinning_file = self.create_optimized_gif(
                spinning_images, duration=430, loop=True
            )

            result_image = images[-1]
            result_file = self.create_optimized_gif(
                [result_image], duration=1000, loop=False
            )

            result = ("lost", bet)
            self.economy.add_credits(ctx.author.id, bet * -1)
            if (1 + s1) % 6 == (1 + s2) % 6 == (1 + s3) % 6:
                symbol = (1 + s1) % 6
                reward = [4, 80, 40, 25, 10, 5][symbol] * bet
                result = ("won", reward)
                self.economy.add_credits(ctx.author.id, reward)

            result_embed = make_embed(
                title=(
                    f"You {result[0]} {result[1]} credits"
                    + ("." if result[0] == "lost" else "!")
                ),
                description=(
                    "You now have "
                    + f"**{self.economy.get_entry(ctx.author.id)[2]}** "
                    + "credits."
                ),
                color=(
                    discord.Color.red()
                    if result[0] == "lost"
                    else discord.Color.green()
                ),
            )

            result_embed.set_image(url="attachment://slot_result.gif")

            return result_embed, spinning_file, result_file

        async def send_slot_result(embed, file, view=None):
            return await ctx.reply(embed=embed, file=file, view=view)

        result_embed, spinning_file, result_file = await play_slots(bet)

        spinning_embed = make_embed(
            title="Spinning the slot machine...", color=discord.Color.blue()
        )

        spinning_embed.set_image(url="attachment://slot_result.gif")

        msg = await send_slot_result(spinning_embed, spinning_file)

        await asyncio.sleep(5)

        view = await SlotView(self, bet, ctx).start(msg)
        await msg.edit(embed=result_embed, attachments=[result_file], view=view)
        self.active_players.remove(ctx.author.id)

        while True:
            try:
                await view.wait()
                if view.value == "reroll":
                    if ctx.author.id in self.active_players:
                        return

                    self.active_players.add(ctx.author.id)
                    result_embed, spinning_file, result_file = await play_slots(bet)

                    spinning_embed.title = (
                        f"<@{ctx.author.id}> Rerolled! Spinning the slot machine..."
                    )
                    await msg.edit(embed=spinning_embed, attachments=[spinning_file])

                    await asyncio.sleep(5)

                    view = await SlotView(self, bet, ctx).start(msg)
                    await msg.edit(
                        embed=result_embed, attachments=[result_file], view=view
                    )
                    self.active_players.remove(ctx.author.id)
                else:
                    break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def create_optimized_gif(self, images, duration, loop):
        with io.BytesIO() as image_binary:
            images[0].save(
                image_binary,
                format="GIF",
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=loop,
                optimize=True,
                quality=10,
            )
            image_binary.seek(0)
            return discord.File(fp=image_binary, filename="slot_result.gif")

    @commands.command(
        brief=f"Purchase credits. Each credit is worth ${DEFAULT_BET}.",
        usage="buyc [credits]",
        aliases=["buy", "b"],
    )
    async def buyc(self, ctx: commands.Context, amount_to_buy: int):
        user_id = ctx.author.id
        profile = self.economy.get_entry(user_id)
        cost = amount_to_buy * DEFAULT_BET
        if profile[1] >= cost:
            self.economy.add_money(user_id, cost * -1)
            self.economy.add_credits(user_id, amount_to_buy)
        await ctx.invoke(self.client.get_command("money"))

    @commands.command(
        brief=f"Sell credits. Each credit is worth ${DEFAULT_BET}.",
        usage="sellc [credits]",
        aliases=["sell", "s"],
    )
    async def sellc(self, ctx: commands.Context, amount_to_sell: int):
        user_id = ctx.author.id
        profile = self.economy.get_entry(user_id)
        if profile[2] >= amount_to_sell:
            self.economy.add_credits(user_id, amount_to_sell * -1)
            self.economy.add_money(user_id, amount_to_sell * DEFAULT_BET)
        await ctx.invoke(self.client.get_command("money"))


async def setup(client: commands.Bot):
    await client.add_cog(Slots(client))
