import os
import requests
import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None  # Disable default so we can make our own
)


anime_roles = {
    "chainsawman": "ChainsawMan",
    "jjk": "JJK",
    "gachiakuta": "Gachiakuta",
    "naruto": "Naruto",
    "bleach": "Bleach",
    "dragon ball": "Dragon Ball",
    "one piece": "One Piece",
    "jjba": "JJBA"
}


def is_mod(): #mod checker... checks if person has mod
    async def predicate(ctx):
        mod_role = discord.utils.get(ctx.guild.roles, name="Moderator")
        if ctx.author.guild_permissions.administrator:
            return True
        if mod_role and mod_role in ctx.author.roles:
            return True
        await ctx.send("You need the `Moderator` role to use this command.")
        return False
    return commands.check(predicate)


@bot.event #this is the bot start up, essentially we press play and this plays in terminal
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("YapBot is online!")


@bot.command() #literally the first command
async def hello(ctx):
    await ctx.send("Hello, I'm YapBot!")


@bot.command() #command I added for fun
async def paynis(ctx):
    await ctx.send("paynis")


@bot.command(name="help") #help command - sends bot commands
async def help_command(ctx):
    await ctx.send(
        "** YapBot Commands**\n\n"
        "** Anime Roles**\n"
        "`!assign <anime>` — Get an anime role\n"
        "`!remove <anime>` — Remove an anime role\n"
        "`!roles` — List available anime roles\n\n"
        "** Anime Info**\n"
        "`!anime <name>` — Look up an anime\n\n"
        "** Mod Commands** *(Moderator role required)*\n"
        "`!kick @user [reason]` — Kick a user\n"
        "`!mute @user [minutes] [reason]` — Timeout a user\n"
        "`!ban @user [reason]` — Ban a user\n\n"
        "** Admin Commands**\n"
        "`!givemod @user` — Give someone the Moderator role\n"
        "`!removemod @user` — Remove someone's Moderator role"
    )


@bot.command() #assign roles command
async def assign(ctx, anime=None):

    if anime is None:
        await ctx.send(
            "Usage: `!assign <anime>`\n"
            "Available: chainsawman, jjk, gachiakuta, naruto, bleach"
        )
        return

    anime = anime.lower()

    if anime not in anime_roles:
        await ctx.send("That anime role doesn't exist.")
        return

    role_name = anime_roles[anime]
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role is None:
        await ctx.send(f"The role `{role_name}` doesn't exist in this server.")
        return

    await ctx.author.add_roles(role)
    await ctx.send(f"{ctx.author.mention} has been given the `{role_name}` role!")


@bot.command() #remove roles
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
        await ctx.send(f"The role `{role_name}` doesn't exist in this server.")
        return

    if role not in ctx.author.roles:
        await ctx.send(f"You don't have the `{role_name}` role.")
        return

    await ctx.author.remove_roles(role)
    await ctx.send(f"{ctx.author.mention} has had the `{role_name}` role removed.")



@bot.command() #shows roles you can give yourself
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


@bot.command() #Keon added this, it was orginally gonna be a different API, but he used anilist which actually works way better
async def anime(ctx, *, search):

    async with ctx.channel.typing():

        try:

            url = "https://graphql.anilist.co"

            
            anime_query = """
            query ($search: String) {
                Media(search: $search, type: ANIME) {
                    title { romaji english }
                    description(asHtml: false)
                    episodes
                    averageScore
                    siteUrl
                }
            }
            """

            response = requests.post(
                url,
                json={"query": anime_query, "variables": {"search": search}},
                timeout=15
            )

            data = response.json()
            media = data.get("data", {}).get("Media") if response.status_code == 200 else None

            
            if not media:

                char_query = """
                query ($search: String) {
                    Character(search: $search) {
                        name { full }
                        description(asHtml: false)
                        siteUrl
                        media(perPage: 1, type: ANIME) {
                            nodes {
                                title { romaji english }
                                siteUrl
                            }
                        }
                    }
                }
                """

                char_response = requests.post(
                    url,
                    json={"query": char_query, "variables": {"search": search}},
                    timeout=15
                )

                char_data = char_response.json()
                character = char_data.get("data", {}).get("Character") if char_response.status_code == 200 else None

                if not character:
                    await ctx.send(f"I couldn't find an anime or character named **{search}**.")
                    return

                name = character["name"].get("full", search)
                description = character.get("description") or "No description available."
                description = description.replace("\n", " ").replace("<br>", " ")
                if len(description) > 700:
                    description = description[:697] + "..."

                site_url = character.get("siteUrl", "")

                # Get the anime they appear in
                anime_nodes = character.get("media", {}).get("nodes", [])
                appears_in = ""
                if anime_nodes:
                    anime_title = (
                        anime_nodes[0]["title"].get("english")
                        or anime_nodes[0]["title"].get("romaji")
                    )
                    anime_url = anime_nodes[0].get("siteUrl", "")
                    appears_in = f"\n**Appears in:** [{anime_title}]({anime_url})"

                await ctx.send(
                    f"** {name}** *(character)*{appears_in}\n\n"
                    f"**About:**\n{description}\n\n"
                    f"**AniList:** {site_url}"
                )

                return

            # Anime found — send anime info
            title = (
                media["title"].get("english")
                or media["title"].get("romaji")
                or search
            )

            description = media.get("description") or "No description available."
            description = description.replace("\n", " ").replace("<br>", " ")
            if len(description) > 700:
                description = description[:697] + "..."

            episodes = media.get("episodes") or "Unknown"
            score = media.get("averageScore") or "Unknown"
            site_url = media.get("siteUrl") or ""

            await ctx.send(
                f"**🎬 {title}**\n\n"
                f"**Synopsis:**\n{description}\n\n"
                f"**Episodes:** {episodes}\n"
                f"**Score:** {score}/100\n"
                f"**AniList:** {site_url}"
            )

        except requests.exceptions.RequestException as error:

            print("================================")
            print("ANILIST API ERROR:")
            print(error)
            print("================================")

            await ctx.send(
                "The anime database is temporarily unavailable. "
                "Please try again later."
            )

        except Exception as error:

            print("================================")
            print("ANIME ERROR:")
            print(error)
            print("================================")

            await ctx.send(
                "Something went wrong while looking up that anime."
            )



@bot.command() #Give mod role, only admins can give mod... for security measure
@commands.has_permissions(administrator=True)
async def givemod(ctx, member: discord.Member = None):

    if member is None:
        await ctx.send("Usage: `!givemod @user`")
        return

    mod_role = discord.utils.get(ctx.guild.roles, name="Moderator")

    if mod_role is None:
        await ctx.send("The `Moderator` role doesn't exist. Create it in your server first.")
        return

    await member.add_roles(mod_role)
    await ctx.send(f"✅ {member.mention} has been given the `Moderator` role.")


@bot.command() #remove mod role
@commands.has_permissions(administrator=True)
async def removemod(ctx, member: discord.Member = None):

    if member is None:
        await ctx.send("Usage: `!removemod @user`")
        return

    mod_role = discord.utils.get(ctx.guild.roles, name="Moderator")

    if mod_role is None:
        await ctx.send("The `Moderator` role doesn't exist in this server.")
        return

    if mod_role not in member.roles:
        await ctx.send(f"{member.mention} doesn't have the `Moderator` role.")
        return

    await member.remove_roles(mod_role)
    await ctx.send(f"✅ {member.mention} has had the `Moderator` role removed.")


@bot.command() #kick
@is_mod() #CHECK FOR MOD
async def kick(ctx, member: discord.Member = None, *, reason="No reason provided"):

    if member is None:
        await ctx.send("Usage: `!kick @user [reason]`")
        return

    if member == ctx.author:
        await ctx.send("You can't kick yourself.")
        return

    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} has been kicked. Reason: {reason}")


@bot.command() #mute command
@is_mod()
async def mute(ctx, member: discord.Member = None, duration: int = 10, *, reason="No reason provided"):

    if member is None:
        await ctx.send("Usage: `!mute @user [minutes] [reason]`")
        return

    if member == ctx.author:
        await ctx.send("You can't mute yourself.")
        return

    until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
    await member.timeout(until, reason=reason)
    await ctx.send(f"🔇 {member.mention} has been muted for {duration} minute(s). Reason: {reason}")



@bot.command() #ban command
@is_mod()
async def ban(ctx, member: discord.Member = None, *, reason="No reason provided"):

    if member is None:
        await ctx.send("Usage: `!ban @user [reason]`")
        return

    if member == ctx.author:
        await ctx.send("You can't ban yourself.")
        return

    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} has been banned. Reason: {reason}")


if not DISCORD_TOKEN: #token check
    raise ValueError("DISCORD_TOKEN is missing from the .env file.")


bot.run(DISCORD_TOKEN)