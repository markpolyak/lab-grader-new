#!/usr/bin/env python3
import gspread

from oauth2client.service_account import ServiceAccountCredentials
import telebot
import requests
import json
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import token, adviser

cred_file = adviser

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)

client = gspread.authorize(creds)

bot = telebot.TeleBot(token)

user = {}
group = {}
group_id = {}
fio = {}
git = {}
domain = {}
last_response = {}
table = {}
lab = {}


def calculate_weeks_between_dates(start_date, end_date):
    delta = (end_date - start_date).days
    if delta > 70:
        return 10
    elif delta > 63:
        return 9
    elif delta > 56:
        return 8
    elif delta > 49:
        return 7
    elif delta > 42:
        return 6
    elif delta > 35:
        return 5
    elif delta > 28:
        return 4
    elif delta > 21:
        return 3
    elif delta > 14:
        return 2
    elif delta > 7:
        return 1
    else:
        return 0


def find_value_in_column(sheet, col, value):
    cell = sheet.find(value, in_column=col)
    if cell:
        return cell.row
    else:
        return 0


def check_lab(lab, github, chat_id):
    # response = requests.post(
    #     f'{http_start}/courses/{domain[chat_id]}/groups/{group[chat_id]}/labs/{lab}/grade',
    #     json={'github': f'{github}'})
    # data = response.json()
    # answer = json.loads(data)
    # if response.status_code == 200:
    sheets = client.open(table[chat_id])
    page = sheets.get_worksheet(group_id[chat_id])
    row = find_row_in_google_sheets(table[chat_id], github, 3, chat_id)
    date_str = page.cell(1, lab + 4).value
    start_date = datetime.strptime(date_str, "%d.%m.%Y")
    current_date = datetime.now()
    xdd = calculate_weeks_between_dates(start_date, current_date)
    save_res_into_table(table[chat_id], lab, row, xdd, chat_id)
    return f"Успешно. Ваша просрочка за лабораторную {xdd}" #message
    # else:
    #     return f"Лабораторная выполнена неправильно. Сообщение об ошибке {answer}"


def find_first_free_row(sheet, col):
    col_values = sheet.col_values(col)
    return len(col_values) + 1


def find_row_in_google_sheets(tablename, val, col, chat_id):
    sheets = client.open(tablename)
    page = sheets.get_worksheet(group_id[chat_id])
    res = find_value_in_column(page, col, val)
    if res:
        return page.cell(res, 3).row
    else:
        return 0


def check_in_google_sheets_name(tablename, val, col, user_id):
    sheets = client.open(tablename)
    page = sheets.get_worksheet(group_id[user_id])
    res = find_value_in_column(page, col, val)
    if res:
        return 1
    else:
        return 0


def check_in_google_sheets(tablename, val, col, user_id):
    sheets = client.open(tablename)
    page = sheets.get_worksheet(group_id[user_id])
    res = find_value_in_column(page, col, val)
    if res:
        return page.cell(res, 3).value
    else:
        return 0


def save_res_into_table(tablename, lab, row, min, chat_id):
    sheets = client.open(tablename)
    page = sheets.get_worksheet(group_id[chat_id])
    if min == 0:
        page.update_cell(row, lab + 4, 'v')
    else:
        page.update_cell(row, lab + 4, f'v-{min}')
    return 0


def save_user_into_table(tablename, git, fio, chat_id):
    sheets = client.open(tablename)
    page = sheets.get_worksheet(group_id[chat_id])
    row = find_row_in_google_sheets(tablename, fio, 2, chat_id)
    page.update_acell(f'C{row}', git)
    return 0


def create_butt_from_url(url, id_chat, name_btn):
    global last_response

    # response = requests.get(url)
    # if response.status_code == 200:
    #     data = response.json()
    #     last_response[id_chat] = json.loads(data)
    #     markup = create_keyboard_from_json(last_response[id_chat], name_btn)
    #     return markup
    #
    # else:
    #     mess = f'Ошибка: {response.status_code}'
    #     return mess

    if url == "Основы машинного обучения 2024 осеньgroups":
        last_response[id_chat] = '''{
               "0": "4131",
               "1": "4132",
               "2": "4133К",
               "3": "4134К",
               "4": "4136",
               "5": "М111",
               "6": "М112",
               "7": "Z1431",
               "8": "Z1432К"
           }'''
        return create_keyboard_from_json(last_response[id_chat], name_btn)
    elif url == "Операционные системы 2024 веснаgroups":
        last_response[id_chat] = '''{
               "0": "4131",
               "1": "4132",
               "2": "4133К",
               "3": "4134К",
               "4": "4136",
               "5": "М111",
               "6": "М112",
               "7": "Z1431",
               "8": "Z1432К"
           }'''
        return create_keyboard_from_json(last_response[id_chat], name_btn)
    elif url == "Операционные системы 2024 осеньgroups":
        last_response[id_chat] = '''{
               "0": "4131",
               "1": "4132",
               "2": "4133К",
               "3": "4134К",
               "4": "4136",
               "5": "М111",
               "6": "М112",
               "7": "Z1431",
               "8": "Z1432К"
           }'''
        return create_keyboard_from_json(last_response[id_chat], name_btn)
    elif url == "domains":
        last_response[id_chat] = '''{
               "1": "Операционные системы 2024 весна",
               "2": "Операционные системы 2024 осень",
               "3": "Основы машинного обучения 2024 осень"
           }'''
        return create_keyboard_from_json(last_response[id_chat], name_btn)
    elif url == "Операционные системы 2024 весна":
        last_response[id_chat] = '''{
               "Lab0": 0,
               "Lab1": 1,
               "Lab2": 2,
               "Lab3": 3,
               "Lab4": 4,
               "Lab5": 5,
               "Lab6": 6,
               "Lab7": 7
           }'''
        return create_keyboard_from_json(last_response[id_chat], name_btn)
    elif url == "Основы машинного обучения 2024 осень":
        last_response[id_chat] = '''{
               "Lab1": 1,
               "Lab2": 2,
               "Lab3": 3,
               "Lab4": 4,
               "Lab5": 5
           }'''
        return create_keyboard_from_json(last_response[id_chat], name_btn)
    elif url == "Операционные системы 2024 осень":
        last_response[id_chat] = '''{
               "Lab0": 0,
               "Lab1": 1,
               "Lab2": 2,
               "Lab3": 3,
               "Lab4": 4,
               "Lab5": 5,
               "Lab6": 6,
               "Lab7": 7
           }'''
        return create_keyboard_from_json(last_response[id_chat], name_btn)




def create_keyboard_from_json(json_string, name):
    data = json.loads(json_string)
    keyboard = InlineKeyboardMarkup()
    if name == 'domain':
        for id, nm, sem in data.items():
            button = InlineKeyboardButton(text=f'{nm} {sem}', callback_data=id)
            keyboard.add(button)
        return keyboard
    elif name == 'group':
        for nm in data.items():
            button = InlineKeyboardButton(text=f'{nm}', callback_data=nm)
            keyboard.add(button)
        return keyboard
    elif name == 'labs':
        for nm in data.items():
            button = InlineKeyboardButton(text=f'{nm}', callback_data=nm)
            keyboard.add(button)
        return keyboard
    else:
        for id, nm in data.items():
            button = InlineKeyboardButton(text=nm, callback_data=id)
            keyboard.add(button)
        return keyboard


@bot.message_handler(commands=['Отмена', 'отмена', 'deny'])
def deny(message):
    global domain
    global fio
    global group
    global group_id
    global git
    global table
    global lab
    del group[message.from_user.id]
    del group_id[message.from_user.id]
    del fio[message.from_user.id]
    del git[message.from_user.id]
    del domain[message.from_user.id]
    del table[message.from_user.id]
    del lab[message.from_user.id]
    mess = f'Я всё забыл, повтори ка!'
    bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler(commands=['Авторизация', 'авторизация', 'auth'])
def start(message):
    if message.from_user.last_name:
        mess = f'Привет, <b>{message.from_user.first_name} {message.from_user.last_name}</b>! Выбери свой предмет:'
    else:
        mess = f'Привет, <b>{message.from_user.first_name}</b>! Выбери свой предмет:'
    key = create_butt_from_url("domains", message.from_user.id, '')
    # key = create_butt_from_url(f"{http_start}/courses/", message.from_user.id, 'domain')
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=key)


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id)
    global domain
    global fio
    global group
    global group_id
    global git
    global table
    if domain.get(call.from_user.id) is None:
        try:
            assoc = json.loads(last_response[call.from_user.id])
            domain[call.from_user.id] = assoc.get(call.data)
            table[call.from_user.id] = domain[call.from_user.id]
            response_text = f"Выбран предмет: {domain[call.from_user.id]}. Выберете вашу группу:"
            key = create_butt_from_url(f"{domain[call.from_user.id]}groups", call.from_user.id, '')
            # key = create_butt_from_url(f"{http_start}/courses/domain[call.from_user.id]/groups", message.from_user.id, 'group')
            bot.send_message(call.message.chat.id, response_text, parse_mode='html', reply_markup=key)
        except:
            response_text = f"Произошла ошибка. Проверьте корректность ваших действий"
            bot.send_message(call.message.chat.id, response_text, parse_mode='html')

    elif group.get(call.from_user.id) is None:
        try:
            assoc = json.loads(last_response[call.from_user.id])
            group_id[call.from_user.id] = int(call.data)
            group[call.from_user.id] = assoc.get(call.data)
            response_text = f"Выбрана группа: {group[call.from_user.id]}. Выберите лабораторную работу:"
            key = create_butt_from_url(f"{domain[call.from_user.id]}", call.from_user.id, '')
            # key = create_butt_from_url(f"{http_start}/courses/domain[call.from_user.id]/groups/group[call.from_user.id]/labs", message.from_user.id, 'labs')
            bot.send_message(call.message.chat.id, response_text, parse_mode='html', reply_markup=key)
        except:
            response_text = f"Произошла ошибка. Проверьте корректность ваших действий"
            bot.send_message(call.message.chat.id, response_text, parse_mode='html')
    elif fio.get(call.from_user.id) is None:
        try:
            assoc = json.loads(last_response[call.from_user.id])
            lab[call.from_user.id] = assoc.get(call.data)
            if 0 < lab[call.from_user.id] <= 10:
                response_text = f"Выбрана лабораторная: {lab[call.from_user.id]}. Введите ваше ФИО:"
                bot.send_message(call.message.chat.id, response_text, parse_mode='html')
        except:
            response_text = f"Произошла ошибка. Проверьте корректность ваших действий"
            bot.send_message(call.message.chat.id, response_text, parse_mode='html')

    else:
        try:
            assoc = json.loads(last_response[call.from_user.id])
            lab[call.from_user.id] = assoc.get(call.data)
            if 0 < lab[call.from_user.id] <= 10:
                response_text = f"Выбрана лабораторная: {lab[call.from_user.id]}."
                bot.send_message(call.message.chat.id, response_text, parse_mode='html')
                answer = check_lab(lab[call.from_user.id], git[call.from_user.id], call.from_user.id)
                response_text = f"Здравствуй, {fio[call.from_user.id]}. Лабораторная проверена. Результат: {answer}"
                bot.send_message(call.message.chat.id, response_text, parse_mode='html')
        except:
            response_text = f"Произошла ошибка. Проверьте корректность ваших действий"
            bot.send_message(call.message.chat.id, response_text, parse_mode='html')


@bot.message_handler()
def name(message):
    global fio
    global git
    global lab
    global domain
    global group
    if domain.get(message.from_user.id) is None:
        response_text = f"Вы не выбрали предмет!"
        bot.send_message(message.chat.id, response_text, parse_mode='html')
    elif group.get(message.from_user.id) is None:
        response_text = f"Вы не выбрали группу!"
        bot.send_message(message.chat.id, response_text, parse_mode='html')
    elif lab.get(message.from_user.id) is None:
        response_text = f"Вы не выбрали лабораторную!"
        bot.send_message(message.chat.id, response_text, parse_mode='html')
    elif fio.get(message.from_user.id) is None:
        #Проверка на существование такого в файле и получения логина гита из гугл дока
        result_of_name_check = check_in_google_sheets_name(table[message.from_user.id], message.html_text, 2,
                                                           message.from_user.id)
        if result_of_name_check:
            fio[message.from_user.id] = message.html_text
            result_of_github_check = check_in_google_sheets(table[message.from_user.id], fio[message.from_user.id], 2,
                                                            message.from_user.id)
            if result_of_github_check:
                git[message.from_user.id] = result_of_github_check
                # Функция для проверки
                answer = check_lab(lab[message.from_user.id], git[message.from_user.id], message.from_user.id)
                response_text = f"Здравствуй, {fio[message.from_user.id]}. Лабораторная проверена. Результат: {answer}"
                bot.send_message(message.chat.id, response_text, parse_mode='html')

            else:
                response_text = f"Здравствуй, {fio[message.from_user.id]}.  Введи логин GitHub для сохранения в таблицу"
                bot.send_message(message.chat.id, response_text, parse_mode='html')
        else:
            response_text = f"Такого пользователя не существует."
            bot.send_message(message.chat.id, response_text, parse_mode='html')

    elif git.get(message.from_user.id) is None:
        #Функция для сохранения логина гита и фио в гугл док
        git[message.from_user.id] = message.html_text
        save_user_into_table(table[message.from_user.id], git[message.from_user.id], fio[message.from_user.id],
                             message.from_user.id)
        answer = check_lab(lab[message.from_user.id], git[message.from_user.id], message.from_user.id)
        names = fio[message.from_user.id].split()
        name = names[0]
        surname = names[1]
        if names.get(2) is not None:
            patr = names[2]
        else:
            patr = ''
        # json_response = requests.post(f'{http_start}/courses/{domain[message.from_user.id]}/groups/{group[message.from_user.id]}/register', json={'name': f'{name}', 'surname' : f'{surname}', 'patronymic' : f'{patr}', 'github' : f'{git[message.from_user.id]}'})
        response_text = f"Здравствуй, {fio[message.from_user.id]}. Лабораторная проверена. Результат: {answer}"
        bot.send_message(message.chat.id, response_text, parse_mode='html')


bot.polling(none_stop=True)
