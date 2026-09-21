import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from openai import AsyncOpenAI


# Load variables from the .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")


# Create the OpenAI client
ai_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY
)


# Discord intents
intents = discord.Intents.default()
intents.message_content = True


# Create the Discord bot
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# This runs when the bot successfully connects to Discord
@bot.event
async def on_ready():

    print(f"Logged in as {bot.user}")
    print("YapBot is online!")


# Simple test command
@bot.command()
async def hello(ctx):

    await ctx.send(
        "Hello! I'm YapBot!"
    )


# AI anime command
@bot.command()
async def anime(ctx, *, question):

    system_prompt = """
You are AnimeOracle, an AI anime expert inside a Discord server.

Your personality:
- Friendly
- Enthusiastic about anime
- Helpful
- Slightly mysterious
- Conversational

You know about:
- Anime
- Manga
- Characters
- Studios
- Genres
- Japanese terminology
- Anime storylines
- Powers and abilities

Rules:
- Answer the user's question clearly.
- Keep normal responses under 150 words.
- If the question involves a major plot spoiler, warn the user.
- Do not pretend to be a human.
"""

    try:

        # Tell Discord that the bot is working
        async with ctx.channel.typing():

            response = await ai_client.responses.create(
                model=OPENAI_MODEL,
                input=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

        # Get the AI's response
        answer = response.output_text.strip()

        # Make sure the response isn't empty
        if not answer:

            answer = "I couldn't come up with a response."

        # Discord messages cannot exceed 2,000 characters
        if len(answer) > 2000:

            answer = answer[:1997] + "..."

        # Send the AI response to Discord
        await ctx.send(answer)

    except Exception as error:

        print(f"AI error: {error}")

        await ctx.send(
            "I ran into an error while trying to think. "
            "Please try again later."
        )


# Check that the Discord token exists
if not DISCORD_TOKEN:

    raise ValueError(
        "DISCORD_TOKEN is missing from the .env file."
    )


# Check that the OpenAI key exists
if not OPENAI_API_KEY:

    raise ValueError(
        "OPENAI_API_KEY is missing from the .env file."
    )


# Start the bot
bot.run(DISCORD_TOKEN)