
import reqs
import time
import telebot
from config import token
import filters
import keyboard
TOKEN = token

bot = telebot.TeleBot(TOKEN)

users_dict = {}

def error(message):
    bot.send_message(message.chat.id, "Произошла внутренняя ошибка")
    instantiate_dialog(message)


@bot.message_handler(commands=['change_userdata'])
def instantiate_dialog(message):
    info = lambda: None
    invite_for_surname(message, info)

@bot.message_handler(commands=['start'])
def start_command(message) :
    bot.send_message(message.chat.id, "Старт бота проверки лаб")
    instantiate_dialog(message)



def invite_for_surname(message, info):
    msg = bot.send_message(message.chat.id, "Введи свою фамилию")
    bot.register_next_step_handler(msg, accept_surname, info)

def invite_for_name(message, info):
    msg = bot.send_message(message.chat.id, "Введи свое имя")
    bot.register_next_step_handler(msg, accept_name, info)

def invite_for_patronym(message, info):
    msg = bot.send_message(message.chat.id, "Введи свое отчество. Если нет отчества, напиши Нет")
    bot.register_next_step_handler(msg, accept_patronym, info)

def invite_for_github(message, info):
    msg = bot.send_message(message.chat.id, "Введи свой ник на GitHub")
    bot.register_next_step_handler(msg, accept_github, info)

def accept_surname(message, info):
    surname = message.text
    info.surname = surname
    invite_for_name(message, info)

def accept_name(message, info):
    name = message.text
    info.name = name
    invite_for_patronym(message, info)

def accept_patronym(message, info):
    if (message.text.lower() != "нет"):
        info.patronym = message.text
    invite_for_github(message, info)

def accept_github(message, info):
    github = message.text
    info.github = github
    print_userdata(message, info)
    users_dict[message.chat.id] = info
    select_subject(message)

def print_userdata(message, info):
    msg_text = "Фамилия: " + info.surname + "\nИмя: " + info.name + "\nОтчество: " + info.patronym + "\nGithub: " + info.github
    bot.send_message(message.chat.id, msg_text)

def register_user(message, subject_id, group, user_info):
    try:
        register_response = reqs.register_student(subject_id, group, user_info)
        status = register_response.status_code
        if (status == 200 or status == 202):
            resp_message = register_response.json()['message']
            bot.send_message(message.chat.id, resp_message)
            return True
        elif (status == 422 or status == 404):
            resp_message = register_response.json()['message']
            bot.send_message(message.chat.id, resp_message)
            return False
        else:
            resp_message = "Произошла ошибка регистрации. Проверь корректность введенных данных."
            bot.send_message(message.chat.id, resp_message)
            return False
    except:
        return False

@bot.message_handler(commands=['subject'])
def select_subject(message):
    try:
        subjects_response = reqs.get_subjects()
        if (subjects_response.status_code == 200):
            subjects = subjects_response.json()
            markup = keyboard.generate_subject_keyboard(subjects)
            bot.send_message(message.chat.id, "Выбери предмет", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Ошибка сервера " + subjects_response.status_code)
    except:
        error(message)
        

@bot.callback_query_handler(func=None, subject_config=filters.subject_factory.filter())
def on_selected_course(call):
    try:
        callback_data = filters.subject_factory.parse(callback_data=call.data)
        message = call.message
        user_info = users_dict[message.chat.id]
        subject_id = callback_data['subject']

        group_response = reqs.get_groups(subject_id)
        if (group_response.status_code == 200):
            groups = group_response.json()
            markup = keyboard.generate_group_keyboard(subject_id, groups)
            bot.send_message(message.chat.id, "Выбери свою группу", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Ошибка сервера " + group_response.status_code)
            select_subject(message)
    except:
        error(call.message)

@bot.callback_query_handler(func=None, group_config=filters.group_factory.filter())
def on_selected_group(call):
    try:
        callback_data = filters.group_factory.parse(callback_data=call.data)
        message = call.message
        user_info = users_dict[message.chat.id]
        subject_id = callback_data['subject']
        group_id = callback_data['group']
        if (register_user(message, subject_id, group_id, user_info)):
            labs_response = reqs.get_labs(subject_id, group_id)
            if (labs_response.status_code == 200):
                labs = labs_response.json()
                markup=keyboard.generate_labs_keyboard(subject_id, group_id, labs)
                bot.send_message(message.chat.id, "Выбери лабораторную работу", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Ошибка сервера " + labs_response.status_code)
                select_subject(message)
        else:
            select_subject(message)
    except:
        error(call.message)

@bot.callback_query_handler(func=None, lab_config=filters.lab_factory.filter())
def on_selected_lab(call):
    try:
        callback_data = filters.lab_factory.parse(callback_data=call.data)
        message = call.message
        user_info = users_dict[message.chat.id]
        subject_id = callback_data['subject']
        group_id = callback_data['group']
        lab_id = callback_data['lab']
        grade_response = reqs.grade_lab(subject_id, group_id, lab_id, user_info.github)
        body = grade_response.json()
        if (body is None):
            bot.send_message(message.chat.id, "Ошибка сервера " + grade_response.status_code + ". Повтори проверку позже")

        else:
            grade_message = body['message']
            if (grade_response.status_code != 200):
                grade_message = grade_message + "\nКод Ошибки: " + grade_response.status_code

            bot.send_message(message.chat.id, grade_message)
    except:
        error(call.message)

@bot.message_handler()
def unknown_message(message):
    bot.send_message(message.chat.id, "Я не понимаю")

filters.add_filters(bot)
while True:
    try:
        bot.infinity_polling()
    except:
        time.sleep(5)