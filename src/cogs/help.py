from asyncio.tasks import current_task
import discord
from discord.ext import commands
from discord.ext.commands import bot
from discord_components import *
from discord_components.dpy_overrides import send_files
from src.cogs.utilities import setup
from src.constants.help_embeds import embeds, get_cmd_embed
from src.constants.urls import *
import asyncio
from src.constants.vars import MONGO_URL, INSTANCE, MONGO_CLIENT
from src.constants.ids import SUPPORT_SERVER_ID

from src.utils.fetchEmojis import fetchEmojis

def get_prefix(message):
    if INSTANCE == 'beta':
        return "t!"

    try:
        db = MONGO_CLIENT["discord_bot"]
        collection = db["prefixes"]
        prefixes = collection.find_one({"_id": 0})
        if str(message.guild.id) not in prefixes:
            return "s!"
        else:
            return prefixes[str(message.guild.id)]
    except Exception as e:
        print(e)
        return "s!"


class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="help", aliases=["h", "halp", "commands", "cmds"])
    async def help(self, ctx):  # New Help command.
        supportServer = self.client.get_guild(SUPPORT_SERVER_ID)
        EMOJIS = await fetchEmojis(supportServer)

        menu_embed = discord.Embed(
            title="Help Menu",
            description=f"Click a button below to get more info on games.\n"
                        f"{EMOJIS['RLGL']} **➜** Rules of Red Light Green Light\n"
                        f"{EMOJIS['HONEYCOMB']} **➜** Rules of Honeycomb\n"
                        f"{EMOJIS['TEAM']} **➜** Rules of Tug Of War\n"
                        f"{EMOJIS['MARBLES']} **➜** Rules of Marbles\n"
                        f"{EMOJIS['GLASS']} **➜** Rules of Glass Walk\n"
                        f"{EMOJIS['CMDS']} **➜** Bot Commands\n"
                        f"{EMOJIS['MENU']} **➜** Shows this Menu\n",
            color=discord.Color.purple()
        )
        embeds["menu"] = {
            "embed": menu_embed,
            "name": "menu"
        }
        embeds["cmds"] = {
            "embed": get_cmd_embed(get_prefix(ctx.message)),
            "name": "Bot Commands"
        }

        button_list_1 = [
            Button(emoji=EMOJIS["RLGL"], custom_id="rlgl", style=ButtonStyle.blue),
            Button(emoji=EMOJIS["HONEYCOMB"], custom_id="honeycomb", style=ButtonStyle.blue),
            Button(emoji=EMOJIS["TEAM"], custom_id="tug", style=ButtonStyle.blue),
            Button(emoji=EMOJIS["MARBLES"], custom_id="marbles", style=ButtonStyle.blue),
            Button(emoji=EMOJIS["GLASS"], custom_id="glass", style=ButtonStyle.blue),
        ]

        button_list_2 = [
            Button(emoji=EMOJIS["MENU"], custom_id="menu", style=ButtonStyle.green),
            Button(emoji=EMOJIS["CMDS"], style=ButtonStyle.green, custom_id="cmds"),

            Button(label="Vote", style=ButtonStyle.URL, url=bot_vote_url, custom_id="vote"),
            Button(label="Join the support server", style=ButtonStyle.URL, custom_id="invite", url=support_server_invite)
        ]

        button_list_3 = [
            Button(label="Support Us!", style=ButtonStyle.URL, url=donate_url, custom_id="donate"),
        ]

        current_embed = menu_embed

        menu_embed.set_thumbnail(url=bot_icon)
        menu_embed.set_footer(text="Click a button to get more info on games.")

        msg = await ctx.send(
            embed=current_embed,
            components=[
                ActionRow(*button_list_1),
                ActionRow(*button_list_2),
                ActionRow(*button_list_3)
            ]
        )

        while True:
            try:
                i = await self.client.wait_for("button_click", timeout=60, check=lambda x: x.message.id == msg.id)
            except asyncio.TimeoutError:
                for i in range(len(button_list_1)):
                    button_list_1[i].disabled = True
                for i in range(len(button_list_2)):
                    button_list_2[i].disabled = True
                await msg.edit(
                    embed=current_embed,
                    components=[
                        ActionRow(*button_list_1),
                        ActionRow(*button_list_2),
                        ActionRow(*button_list_3)
                    ])
                return
            except Exception as e:
                print(e)
            else:
                if i.custom_id != "vote" and i.custom_id != "invite":
                    current_embed = embeds[i.component.custom_id]["embed"]

                await i.respond(
                    type=7,
                    ephemeral=False,
                    embed=current_embed,
                    components=[
                        ActionRow(*button_list_1),
                        ActionRow(*button_list_2),
                        ActionRow(*button_list_3)
                    ]
                )


def setup(client):
    client.add_cog(Help(client))
