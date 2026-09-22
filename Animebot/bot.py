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

Crole = "ChainsawMan"

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
    await ctx.send("Hello! I'm AnimeOracle!")

@bot.command()
async def paynis(ctx):
    await ctx.send("paynis")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=Crole)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} has been assigned the role '{Crole}'!")
    else:
        await ctx.send(f"Role Doesn't Exist")
    

@bot.event
async def on_message(message):

    # Ignore messages from bots
    if message.author.bot:
        return

    # Check for our anime keyword
    if message.content.lower().startswith("anime"):

        # Remove "anime" from the beginning
        question = message.content[5:].strip()

        # Make sure they actually asked something
        if not question:
            await message.reply(
                "Ask me something! For example: `anime who is Gojo?`",
                mention_author=False
            )
            return

        try:
            # Show typing indicator
            async with message.channel.typing():

                response = await ai_client.responses.create(
                    model="gpt-5.6-luna",
                    instructions="""
You are AnimeOracle, an AI anime expert inside a Discord server.

You know about anime, manga, characters, studios, genres,
stories, powers, Japanese terminology, and anime culture.

Your personality is:
- Friendly
- Enthusiastic about anime
- Casual
- Helpful
- Occasionally funny

Keep responses relatively short unless the user asks for
a detailed explanation.

If discussing major plot points, warn the user about spoilers.
""",
                    input=question
                )

            answer = response.output_text

            # Discord messages cannot exceed 2000 characters
            if len(answer) > 2000:
                answer = answer[:1997] + "..."

            await message.reply(
                answer,
                mention_author=False
            )

        except Exception as error:
            print(f"OpenAI error: {error}")

            await message.reply(
                "Something went wrong while talking to the AI.",
                mention_author=False
            )

    # Allow normal Discord commands like !hello to continue working
    await bot.process_commands(message)


if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is missing from .env")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from .env")


bot.run(DISCORD_TOKEN)