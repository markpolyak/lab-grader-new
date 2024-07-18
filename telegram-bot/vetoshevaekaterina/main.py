import asyncio
import time
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
from telebot.asyncio_handler_backends import State, StatesGroup

import filters
import reqs

from config import bot_token
TOKEN = bot_token
bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage())

bot.add_custom_filter(filters.CoursesCallbackFilter())
bot.add_custom_filter(filters.GroupsCallbackFilter())
bot.add_custom_filter(filters.LabsCallbackFilter())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.TextMatchFilter())


@bot.message_handler(commands=['start'])
async def start_command(message) :
    await bot.send_message(message.chat.id, "Старт бота проверки лаб", reply_markup=types.ReplyKeyboardRemove())
    await select_course(message)

@bot.message_handler(commands=['register'])
async def reg_command(message):
    user_id = message.from_user.id
    await provide_register(user_id, message)

@bot.message_handler(commands=['selectcourse'])
async def course_cmd(message):
    await select_course(message)

class stud:
    github = None
    surname = None
    name = None
    patronymic = None
    def __init__(self, surname, name, patronymic, github):
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.github = github

student_dict = {}

class chat_states(StatesGroup):
    course_state = State()
    group_state = State()
    lab_state = State()
    reg_name_state = State()
    reg_surname_state = State()
    reg_patronymic_state = State()
    reg_github_state = State()

def course_keyboard(courses):
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=course['name'] + " " + course['semester'],
                    callback_data=filters.course_factory.new(course_id=course['id'])
                )
            ] 
            for course in courses
        ]
    )

def group_keyboard(course, groups): 
    markup=types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=group,
                    callback_data=filters.groups_factory.new(course_id=course, group_id=group)
                )
            ] 
            for group in groups
        ]
    )
    markup.add(types.InlineKeyboardButton(text="Back", callback_data=filters.groups_factory.new(course_id=course, group_id="Back")))
    return markup

def lab_keyboard(course, group, labs):
    markup=types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=lab,
                    callback_data=filters.labs_factory.new(course_id=course, group_id=group, lab_id=lab)
                )
                for lab in labs
            ]
        ]
    )
    return markup

async def select_course(message):
    try:
        response = reqs.get_courses()
        if (response.status_code == 200) :
            await bot.set_state(message.chat.id, chat_states.course_state, message.chat.id)
            courses = response.json()
            markup=course_keyboard(courses)
            await bot.send_message(message.chat.id, "Предмет", reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, "Ошибка")
    except Exception as error:
        await bot.send_message(message.chat.id, "Ошибка")
        print(error)


@bot.message_handler(func=lambda call: False, state=chat_states.course_state)
async def input_course_itself(message):
    bot.send_message(message.chat.id, "Нажми кнопку")

@bot.callback_query_handler(func=None, course=filters.course_factory.filter())
async def on_course_callback(call):
    try:
        callback_data = filters.course_factory.parse(callback_data=call.data)
        course_id = callback_data['course_id']

        message = call.message
        await bot.set_state(call.from_user.id, chat_states.group_state, message.chat.id)
        response = reqs.get_groups_by_course_id(course_id)
        if (response.status_code == 200):
            groups = response.json()
            markup = group_keyboard(course_id, groups)
            await bot.send_message(message.chat.id, "Группа", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Ошибка")
            select_course(message)
                
    except Exception as error:
        print(error)
        await bot.send_message(message.chat.id, "Ошибка")
        await select_course(message)
    
@bot.message_handler(func=lambda call: False, state=chat_states.group_state)
async def input_course_itself(message):
    await bot.send_message(message.chat.id, "Нажми кнопку")

@bot.callback_query_handler(func=None, group=filters.groups_factory.filter())
async def select_group(call):
    try:
        callback_data = filters.groups_factory.parse(callback_data=call.data)
        course_id = callback_data['course_id']
        group_id = callback_data['group_id']
        await bot.set_state(call.from_user.id, chat_states.reg_name_state, call.message.chat.id)
        async with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
            if (group_id == "Back"):
                await select_course(call.message)
            elif (course_id is None):
                await bot.send_message(call.message.chat.id, "Ошибка")
                await select_course(call.message)
            else:
                data['course_id'] = course_id
                data['group_id'] = group_id
                await provide_register(call.from_user.id, call.message)
    except Exception as error:
        print(error)
        await bot.send_message(call.message.chat.id, "Ошибка")
        await select_course(call.message)

async def provide_register(user_id, message):
    try:
        await bot.send_message(message.chat.id, "Напиши фамилию", reply_markup=types.ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True
            ).add(types.KeyboardButton("Back")))
        await bot.set_state(user_id, chat_states.reg_surname_state, message.chat.id)
    except Exception as error:
        print(error)
        await bot.send_message(message.chat.id, "Ошибка")
        await select_course(message)
    

async def invite_for_name(message):
    await bot.send_message(message.chat.id, "Напиши имя")
    await bot.set_state(message.from_user.id, chat_states.reg_name_state, message.chat.id)

async def invite_for_patronymic(message):
    await bot.set_state(message.from_user.id, chat_states.reg_patronymic_state, message.chat.id)
    return await bot.send_message(message.chat.id, "Напиши отчетсво. Если нет отчества, напиши Нет")

async def invite_for_git(message):
    await bot.set_state(message.from_user.id, chat_states.reg_github_state, message.chat.id)
    return await bot.send_message(message.chat.id, "Напиши свой github")

@bot.message_handler(state=chat_states.reg_surname_state)
async def get_surname(message):
    try:
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if (message.text == 'Back'):
                if (message.chat.id in student_dict):
                    await invite_for_lab(data['course_id'], data['group_id'], message)
                else:
                    await select_course(message)
            else:
                surname = message.text
                await invite_for_name(message)
                data['surname'] = surname
    except Exception as error:
        print(error)
        await bot.send_message(message.chat.id, "Ошибка")
        await select_course(message)

@bot.message_handler(state=chat_states.reg_name_state)
async def get_name(message):
    try:
        if (message.text == 'Back'):
            await provide_register(message.from_user.id, message)
        else:
            surname = message.text
            msg = await invite_for_patronymic(message)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['name'] = surname
    except Exception as error:
        print(error)
        await bot.send_message(message.chat.id, "Ошибка")
        await select_course(message)

@bot.message_handler(state=chat_states.reg_patronymic_state)
async def get_patronymic(message):
    try:
        if (message.text == 'Back'):
            await invite_for_name(message)
        else:
            surname = message.text
            if (surname.lower() == "нет"):
                surname = ""
            msg = await invite_for_git(message)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['patronymic'] = surname
    except Exception as error:
        print(error)
        await bot.send_message(message.chat.id, "Ошибка")
        await select_course(message)

@bot.message_handler(state=chat_states.reg_github_state)
async def get_github(message):
    try:
        if (message.text == 'Back'):
            await invite_for_patronymic(message)
        else:
            git = message.text
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                surname = data['surname']
                name = data['name']
                patronymic = data['patronymic']

                course_id = data['course_id']
                group_id = data['group_id']

                new_student = stud(surname, name, patronymic, git)
                response = reqs.register_student(course_id, group_id, new_student)
                if (response.status_code == 200 or response.status_code == 202):
                    body = response.json()
                    await bot.send_message(message.chat.id, body['message'])
                    await bot.set_state(message.from_user.id, chat_states.lab_state, message.chat.id)
                    student_dict[message.chat.id] = new_student
                    await invite_for_lab(course_id, group_id, message)

                elif (response.status_code == 422 or response.status_code == 404):
                    body = response.json()
                    await bot.send_message(message.chat.id, body['message'])
                    await select_course(message)
                else:
                    await bot.send_message(message.chat.id, "Ошибка")
                    await select_course(message)

    except Exception as error:
        print(error)
        await bot.send_message(message.chat.id, "Ошибка")
        await select_course(message)

async def invite_for_lab(course_id, group_id, message):
    try:
        response = reqs.get_labs_by_course_and_group(course_id, group_id)
        if (response.status_code == 200):
            body = response.json()
            markup=lab_keyboard(course_id, group_id, body)
            await bot.send_message(message.chat.id, "Доступные лабораторные работыи", reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, "Ошибка")
    except Exception as error:
        print(error)
        await bot.send_message(message.chat.id, "Ошибка")
        await select_course(message)

@bot.callback_query_handler(func=None, lab=filters.labs_factory.filter())
async def on_select_lab(call):
    try:
        if (call.from_user.id not in student_dict):
            await provide_register(call.from_user.id, call.message)
            return
        
        callback_data = filters.labs_factory.parse(callback_data=call.data)
        await bot.set_state(call.from_user.id, chat_states.lab_state, call.message.chat.id)
        
        async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['course_id'] = callback_data['course_id']
            data['group_id'] = callback_data['group_id']
            course_id = callback_data['course_id']
            group_id = callback_data['group_id']
            lab_id = callback_data['lab_id']
            github = student_dict[call.from_user.id].github

            response = reqs.grade_lab(course_id, group_id, lab_id, github)
            body = response.json()
            if (body is None):
                await bot.send_message(call.message.chat.id, "Ошибка. Проверь позже")
            else:
                text = body['message']

                await bot.send_message(call.message.chat.id, text)
    except Exception as error:
        print(error)
        await bot.send_message(call.message.chat.id, "Ошибка")
        await select_course(call.message)

@bot.message_handler(state=chat_states.lab_state)
async def on_lab_printed(message):
    await bot.send_message(message.chat.id, "Нажми кнопку")


while True:
    try:
        asyncio.run(bot.polling(none_stop=True))
    except:
        time.sleep(5)