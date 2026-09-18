import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("YapBot is online!")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm YapBot!")


if not TOKEN:
    raise ValueError("DISCORD_TOKEN is missing from .env")


bot.run(TOKEN)