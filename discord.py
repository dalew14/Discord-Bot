#Get an openAI api key, Ik where to get it
#Then pip install open ai in the terminal
#then code the ai in here to be called on by keyword
#then make a discord bot on this discord dev page
#success!
#any questions?

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
    print("AnimeOracle is online!")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm YapBot!")


if not TOKEN:
    raise ValueError("DISCORD_TOKEN is missing from .env")


bot.run(TOKEN)