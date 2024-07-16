from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
from telebot import types

from filters.course_filter import CoursesCallbackFilter
from filters.groups_filter import GroupsCallbackFilter
from filters.lab_filter import LabsCallbackFilter

from config import bot_token
TOKEN = bot_token
bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage())

commands=[
    types.BotCommand("start", "Начни работу с ботом"),
    types.BotCommand("selectcourse", "Выбрать курс и группу"),
    types.BotCommand("register", "Зарегистрироваться или сменить данные пользователя")
]

bot.set_my_commands(commands=commands)
bot.add_custom_filter(CoursesCallbackFilter())
bot.add_custom_filter(GroupsCallbackFilter())
bot.add_custom_filter(LabsCallbackFilter())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.TextMatchFilter())
