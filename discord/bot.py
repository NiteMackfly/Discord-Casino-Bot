import discord
from discord.ext import commands
import os
import asyncio
from modules.helpers import *

intents = discord.Intents.default()
intents.message_content = True  # Ensure to enable necessary intents

client = commands.Bot(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=intents)

client.remove_command("help")


async def load_cogs():
    for filename in os.listdir(COG_FOLDER):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await client.load_extension(cog_name)
            except Exception as e:
                print(f"Failed to load extension {cog_name}: {e}")


@client.event
async def on_ready():
    await load_cogs()
    print(f"Logged in as {client.user}")


client.run(TOKEN)
