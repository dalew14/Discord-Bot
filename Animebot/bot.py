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

MOD_ROLE = "Moderator"

def is_mod(ctx):
    role = discord.utils.get(ctx.author.roles, name = MOD_ROLE)
    return role is not None

anime_roles = {
    "chainsawman": "ChainsawMan",
    "jjk": "JJK",
    "gachiakuta": "Gachiakuta",
    "naruto": "Naruto",
    "bleach": "Bleach"
}

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
async def assign(ctx, anime=None):

    if anime is None:
        await ctx.send(
            "Usage: `!assign <anime>`\n"
            "Available: chainsawman, jjk, onepiece, naruto, aot"
        )
        return

    anime = anime.lower()

    if anime not in anime_roles:
        await ctx.send("That anime role doesn't exist.")
        return

    role_name = anime_roles[anime]

    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role is None:
        await ctx.send(f"The role `{role_name}` doesn't exist.")
        return

    await ctx.author.add_roles(role)

    await ctx.send(
        f"{ctx.author.mention} has been given the `{role_name}` role!"
    )

@bot.command()
async def remove(ctx, anime=None):

    if anime is None:
        await ctx.send(
            "Usage: `!remove <anime>`\n"
            "Example: `!remove jjk`"
        )
        return

    anime = anime.lower()

    if anime not in anime_roles:
        await ctx.send("That anime role doesn't exist.")
        return

    role_name = anime_roles[anime]

    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role is None:
        await ctx.send(f"The role `{role_name}` doesn't exist.")
        return

    if role not in ctx.author.roles:
        await ctx.send(f"You don't have the `{role_name}` role.")
        return

    await ctx.author.remove_roles(role)

    await ctx.send(
        f"{ctx.author.mention} has had the `{role_name}` role removed."
    )

@bot.command()
async def roles(ctx):

    available_roles = "\n".join(
        f"`{key}` → {value}"
        for key, value in anime_roles.items()
    )

    await ctx.send(
        "**Anime Roles**\n\n"
        f"{available_roles}\n\n"
        "Use `!assign <anime>` to get a role."
    )

bot.run(DISCORD_TOKEN)