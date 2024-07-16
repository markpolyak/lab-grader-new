import asyncio
import time
from telebot import types
from telebot.async_telebot import AsyncTeleBot


from bot_init import bot

@bot.message_handler(commands=['start'])
async def start_command(message) :
    await bot.send_message(message.chat.id, "Привет, я - бот для проверки лабораторных работ.", reply_markup=types.ReplyKeyboardRemove())
    await selection.select_course(message)

@bot.message_handler(commands=['register'])
async def reg_command(message):
    user_id = message.from_user.id
    await selection.provide_register(user_id, message)

@bot.message_handler(commands=['selectcourse'])
async def course_cmd(message):
    await selection.select_course(message)

import selection

while True:
    try:
        asyncio.run(bot.polling(none_stop=True))
    except:
        time.sleep(5)