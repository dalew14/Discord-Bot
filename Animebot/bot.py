import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI client
ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

crole = "ChainsawMan"

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
    await ctx.send("Hello, I'm YapBot!")

@bot.command()
async def paynis(ctx):
    await ctx.send("paynis")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=crole)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} has been assigned the role '{crole}'!")
    else:
        await ctx.send(f"Role Doesn't Exist")
    
bot.run(DISCORD_TOKEN)