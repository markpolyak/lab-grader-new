import os
import logging

import disnake
from disnake.ext import commands

from config import bot_config

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, test_guilds=[1274398953940455485])  # вставляем id-сервера


@bot.event
async def on_ready():
    logging.info("Bot has started")


logging.basicConfig(level=logging.INFO, filename="lab-handler-discord-bot.log", filemode="w")


def get_cogs():
    """
    Loading of cogs (aka bots extensions, bot modules) to bot
    :return:
    """
    for file in os.listdir(bot_config.COGS_DIR_PATH):
        if file.endswith(".py"):
            ext_name = f"{bot_config.COGS_DIR_NAME}.{file[:-3]}"
            bot.load_extension(ext_name)
            logging.info(f'added {ext_name} cog to bot')


get_cogs()

bot.run(YOUR_BOT_TOKEN)
