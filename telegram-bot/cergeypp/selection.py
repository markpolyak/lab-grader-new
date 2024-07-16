from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import types
from telebot import asyncio_filters

from bot_init import bot
import backend_requests
from filters.course_filter import course_factory
from filters.groups_filter import groups_factory
from filters.lab_filter import labs_factory

import json

class Student:
    github = None
    surname = None
    name = None
    patronymic = None
    def __init__(self, surname, name, patronymic, github):
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.github = github

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

student_dict = {}

class SelectionStates(StatesGroup):
    courseState = State()
    courseAcceptState = State()
    groupState = State()
    labState = State()
    nameState = State()
    surnameState = State()
    patronymicState = State()
    githubState = State()
    registerAcceptState = State()

def course_keyboard(courses):
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=course['name'] + " " + course['semester'],
                    callback_data=course_factory.new(course_id=course['id'])
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
                    callback_data=groups_factory.new(course_id=course, group_id=group)
                )
            ] 
            for group in groups
        ]
    )
    markup.add(types.InlineKeyboardButton(text="Назад", callback_data=groups_factory.new(course_id=course, group_id="Назад")))
    return markup

def lab_keyboard(course, group, labs):
    markup=types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=lab,
                    callback_data=labs_factory.new(course_id=course, group_id=group, lab_id=lab)
                )
                for lab in labs
            ]
        ]
    )
    return markup

def course_accept_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton(text='Да'))
    markup.add(types.KeyboardButton(text='Назад'))
    return markup

async def select_course(message):
    try:
        response = backend_requests.get_courses()
        if (response.status_code == 200) :
            await bot.set_state(message.chat.id, SelectionStates.courseState, message.chat.id)
            courses = response.json()
            markup=course_keyboard(courses)
            await bot.send_message(message.chat.id, "Выбери курс:", reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, "Что-то пошло не так. Обратитесь к преподавателю")
    except Exception as error:
        await bot.send_message(message.chat.id, "Бот сломался :). Обратись к преподавателю.")
        print(error)


@bot.message_handler(func=lambda call: False, state=SelectionStates.courseState)
async def input_course_itself(message):
    bot.send_message(message.chat.id, "Выберите курс с помощью клавиатуры")

@bot.callback_query_handler(func=None, course=course_factory.filter())
async def view_course_info(call):
    try:
        callback_data = course_factory.parse(callback_data=call.data)
        course_id = callback_data['course_id']

        message = call.message
        response = backend_requests.get_course_by_id(course_id)
        if (response.status_code == 200):
            body = response.json()

            course_name = body['name']
            semestr = body['semester']
            email = body['email']
            spreadsheet = body['google-spreadsheet']

            messageTemplate = "Название: {}\nСеместр: {}\nE-mail: {}\nГугл-таблица: {}\n\nЭто Ваш курс?"
            messageTemplate = messageTemplate.format(course_name, semestr, email, spreadsheet)
            await bot.set_state(call.from_user.id, SelectionStates.courseAcceptState, message.chat.id)
            await bot.send_message(message.chat.id, text=messageTemplate, reply_markup=course_accept_keyboard())
            async with bot.retrieve_data(message.chat.id) as data:
                data['course_id'] = course_id

        else:
            bot.send_message(message.chat.id, "Что-то пошло не так. Обратитесь к преподавателю")
            select_course(message)
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)
    
@bot.message_handler(state=SelectionStates.courseAcceptState)
async def accept_course(message):
    try:
        if (message.text == 'Да'):
            await bot.set_state(message.from_user.id, SelectionStates.groupState, message.chat.id)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                course_id = data['course_id']
                response = backend_requests.get_groups_by_course_id(course_id)
                if (response.status_code == 200):
                    groups = response.json()
                    markup = group_keyboard(course_id, groups)
                    await bot.send_message(message.chat.id, "Выберите группу", reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, "Что-то пошло не так. Обратитесь к преподавателю")
                    select_course(message)
                    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                        data['course_id'] = None

        elif message.text == 'Назад':
            await select_course(message)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['course_id'] = None
        else:
            await bot.send_message(message.chat.id, "Я не понимаю твою команду. Воспользуйся клавиатурой")
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)

@bot.message_handler(func=lambda call: False, state=SelectionStates.groupState)
async def input_course_itself(message):
    await bot.send_message(message.chat.id, "Выберите группу с помощью клавиатуры")

@bot.callback_query_handler(func=None, group=groups_factory.filter())
async def select_group(call):
    try:
        callback_data = groups_factory.parse(callback_data=call.data)
        course_id = callback_data['course_id']
        group_id = callback_data['group_id']
        await bot.set_state(call.from_user.id, SelectionStates.nameState, call.message.chat.id)
        async with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
            if (group_id == "Назад"):
                await select_course(call.message)
            elif (course_id is None):
                await bot.send_message(call.message.chat.id, "Что-то пошло не так.")
                await select_course(call.message)
            else:
                data['group_id'] = group_id
                await bot.send_message(call.message.chat.id, 'Для смены курса и группы напишите команду /selectcourse')
                await provide_register(call.from_user.id, call.message)
    except:
        await bot.send_message(call.message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(call.message)

async def provide_register(user_id, message):
    try:
        await bot.send_message(message.chat.id, "Введи свою фамилию", reply_markup=types.ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True
            ).add(types.KeyboardButton("Назад")))
        await bot.set_state(user_id, SelectionStates.surnameState, message.chat.id)
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)
    

async def invite_for_name(message):
    await bot.send_message(message.chat.id, "Введите имя")
    await bot.set_state(message.from_user.id, SelectionStates.nameState, message.chat.id)

async def invite_for_patronymic(message):
    await bot.set_state(message.from_user.id, SelectionStates.patronymicState, message.chat.id)
    return await bot.send_message(message.chat.id, "Введите отчество. Если нет отчества, напиши Нет")

async def invite_for_git(message):
    await bot.set_state(message.from_user.id, SelectionStates.githubState, message.chat.id)
    return await bot.send_message(message.chat.id, "Введите имя пользователя GitHub")

@bot.message_handler(state=SelectionStates.surnameState)
async def get_surname(message):
    try:
        if (message.text == 'Назад'):
            if (message.chat.id in student_dict):
                await invite_for_lab(message)
            else:
                await select_course(message)
        else:
            surname = message.text
            await invite_for_name(message)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['surname'] = surname
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)

@bot.message_handler(state=SelectionStates.nameState)
async def get_name(message):
    try:
        if (message.text == 'Назад'):
            await provide_register(message)
        else:
            surname = message.text
            msg = await invite_for_patronymic(message)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['name'] = surname
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)

@bot.message_handler(state=SelectionStates.patronymicState)
async def get_patronymic(message):
    try:
        if (message.text == 'Назад'):
            await invite_for_name(message)
        else:
            surname = message.text
            if (surname.lower() == "нет"):
                surname = ""
            msg = await invite_for_git(message)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['patronymic'] = surname
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)

@bot.message_handler(state=SelectionStates.githubState)
async def get_github(message):
    try:
        if (message.text == 'Назад'):
            await invite_for_patronymic(message)
        else:
            git = message.text
            await bot.set_state(message.from_user.id, SelectionStates.registerAcceptState, message.chat.id)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                surname = data['surname']
                name = data['name']
                patronymic = data['patronymic']
                data['git'] = git

                messageTemplate = "Все ли введено верно?\nФамилия: {}\nИмя: {}\nОтчество: {}\nИмя GitHub: {}"
                messageTemplate = messageTemplate.format(surname, name, patronymic, git)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add(types.KeyboardButton("Да"))
                markup.add(types.KeyboardButton("Назад"))
                await bot.send_message(message.chat.id, messageTemplate, reply_markup=markup)
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)

@bot.message_handler(state=SelectionStates.registerAcceptState)
async def accept_register(message):
    try:
        if (message.text == 'Да'):
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                surname = data['surname']
                name = data['name']
                patronymic = data['patronymic']
                git = data['git']

                course_id = data['course_id']
                group_id = data['group_id']

                new_student = Student(surname, name, patronymic, git)
                response = backend_requests.register_student(course_id, group_id, new_student)
                if (response.status_code == 200 or response.status_code == 202):
                    body = response.json()
                    await bot.send_message(message.chat.id, body['message'])
                    await bot.send_message(message.chat.id, "Для смены ФИО и имя Github введите команду /register")
                    await bot.set_state(message.from_user.id, SelectionStates.labState, message.chat.id)
                    student_dict[message.chat.id] = new_student
                    await invite_for_lab(course_id, group_id, message)

                elif (response.status_code == 422 or response.status_code == 404):
                    body = response.json()
                    await bot.send_message(message.chat.id, body['message'])
                    await select_course(message)
                else:
                    await bot.send_message(message.chat.id, "Что-то пошло не так. Обратитесь к преподавателю")
                    await select_course(message)
                
        elif (message.text == 'Назад'):
            await provide_register(message)
            async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['surname'] = None
                data['name'] = None
                data['patronymic'] = None
                data['git'] = None
        else:
            await bot.send_message(message.chat.id, "Я не понимаю твою команду. Воспользуйся клавиатурой")
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)


async def invite_for_lab(course_id, group_id, message):
    try:
        response = backend_requests.get_labs_by_course_and_group(course_id, group_id)
        if (response.status_code == 200):
            body = response.json()
            markup=lab_keyboard(course_id, group_id, body)
            await bot.send_message(message.chat.id, "Выберите лабораторную работу для проверки", reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, "Что-то пошло не так. Обратитесь к преподавателю")
    except:
        await bot.send_message(message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(message)

@bot.callback_query_handler(func=None, lab=labs_factory.filter())
async def on_select_lab(call):
    try:
        if (call.from_user.id not in student_dict):
            await provide_register(call.from_user.id, call.message)
            return
        
        callback_data = labs_factory.parse(callback_data=call.data)
        await bot.set_state(call.from_user.id, SelectionStates.labState, call.message.chat.id)
        async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['course_id'] = callback_data['course_id']
            data['group_id'] = callback_data['group_id']

        async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['course_id'] = callback_data['course_id']
            data['group_id'] = callback_data['group_id']
            course_id = callback_data['course_id']
            group_id = callback_data['group_id']
            lab_id = callback_data['lab_id']
            github = student_dict[call.from_user.id].github

            response = backend_requests.grade_lab(course_id, group_id, lab_id, github)
            body = response.json()
            if (body is None):
                await bot.send_message(call.message.chat.id, "Случилась непредвиденная ошибка на сервере. Попробуйте запустить проверку позже")
            else:
                text = body['message']
                if (response.status_code != 200):
                    text = text + "\nСтатус ошибки: " + response.status_code

                await bot.send_message(call.message.chat.id, text)
    except:
        await bot.send_message(call.message.chat.id, "Произошла ошибка. Введите данные заново.")
        await select_course(call.message)

@bot.message_handler(state=SelectionStates.labState)
async def on_lab_printed(message):
    await bot.send_message(message.chat.id, "Я не понимаю твою команду. Воспользуйся кнопками")
