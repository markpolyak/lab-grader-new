#!/usr/bin/env python3
import time

import telebot
import requests
import re
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import token, http_st


bot = telebot.TeleBot(token)


class Resp:
    def __init__(self, status_code, json):
        self.status_code = status_code
        self.json = json

    def json(self):
        return self.json


user = {}
group = {}
group_id = {}
fio = {}
git = {}
domain = {}
last_response = {}
lab = {}
http_start = http_st


def check_lab(lab_no, github, chat_id, param):
    # response = requests.post(
    #     f'{http_start}/courses/{domain[chat_id]}/groups/{group[chat_id]}/labs/{lab_no}/grade',
    #     json={'github': f'{github}'})
    response = Resp(200, param)
    data = response.json #()
    answer = json.loads(data)
    if response.status_code == 200:
        return f"Успешно: {answer['message']}"
    else:
        return f"Лабораторная выполнена неправильно. Сообщение об ошибке: {answer['message']}"


def create_butt_from_url(url, id_chat, name_btn, param):
    global last_response

    # response = requests.get(url)
    response = Resp(200, param)

    if response.status_code == 200:
        data = response.json #()
        last_response[id_chat] = json.loads(data)
        markup = create_keyboard_from_json(data, name_btn)
        return markup
    else:
        mess = f'Ошибка: {response.status_code}'
        return mess


def create_keyboard_from_json(json_string, name_json):
    data = json.loads(json_string)
    keyboard = InlineKeyboardMarkup()
    if name_json == 'domain':
        for item in data:
            button = InlineKeyboardButton(text=f'{item["name"]} {item["semester"]}', callback_data=item["id"])
            keyboard.add(button)
        return keyboard
    elif name_json == 'group':
        for item in data:
            button = InlineKeyboardButton(text=f'{item}', callback_data=item)
            keyboard.add(button)
        return keyboard
    elif name_json == 'labs':
        for item in data:
            button = InlineKeyboardButton(text=f'{item}', callback_data=item)
            keyboard.add(button)
        return keyboard
    # else:
    #     for id, nm in data.items():
    #         button = InlineKeyboardButton(text=nm, callback_data=id)
    #         keyboard.add(button)
    #     return keyboard


@bot.message_handler(commands=['Отмена', 'отмена', 'cancel'])
def deny(message):
    global domain
    global fio
    global group
    global group_id
    global git
    global lab
    if group.get(message.from_user.id) is None:
        del group[message.from_user.id]
    if group_id.get(message.from_user.id) is None:
        del group_id[message.from_user.id]
    if fio.get(message.from_user.id) is None:
        del fio[message.from_user.id]
    if git.get(message.from_user.id) is None:
        del git[message.from_user.id]
    if domain.get(message.from_user.id) is None:
        del domain[message.from_user.id]
    if lab.get(message.from_user.id) is None:
        del lab[message.from_user.id]
    mess = f'Я всё забыл, повтори ка!'
    bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler(commands=['Авторизация', 'авторизация', 'auth', 'Auth', 'start', 'Start'])
def start(message):
    global domain
    global fio
    global group
    global group_id
    global git
    global lab
    if group.get(message.from_user.id) is None:
        del group[message.from_user.id]
    if group_id.get(message.from_user.id) is None:
        del group_id[message.from_user.id]
    if fio.get(message.from_user.id) is None:
        del fio[message.from_user.id]
    if git.get(message.from_user.id) is None:
        del git[message.from_user.id]
    if domain.get(message.from_user.id) is None:
        del domain[message.from_user.id]
    if lab.get(message.from_user.id) is None:
        del lab[message.from_user.id]
    if message.from_user.last_name:
        mess = f'Привет, <b>{message.from_user.first_name} {message.from_user.last_name}</b>! Выбери свой предмет:'
    else:
        mess = f'Привет, <b>{message.from_user.first_name}</b>! Выбери свой предмет:'
    js = '''
    [{
      "id": "1",
      "name": "Машинное обучение",
      "semester": "весна 2024"
    },
    {
        "id": "2",
        "name": "Операционные системы",
        "semester": "осень 2024"
    }]
    '''
    key = create_butt_from_url(f"{http_start}/courses/", message.from_user.id, 'domain', js)
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
    if domain.get(call.from_user.id) is None:
        try:
            if int(call.data) < 100:
                domain[call.from_user.id] = call.data
                response_text = f"Вы выбрали предмет. Выберете вашу группу:"
                js = '''
                ["4031", "4032", "4036", "Z0431", "Z0432", "Z0436"]
                '''
                key = create_butt_from_url(f"{http_start}/courses/{domain[call.from_user.id]}/groups", call.from_user.id,
                                           'group', js)
                bot.send_message(call.message.chat.id, response_text, parse_mode='html', reply_markup=key)
            else:
                raise Exception
        except:
            response_text = f"Произошла ошибка при выборе предмета. Проверьте корректность ваших действий"
            bot.send_message(call.message.chat.id, response_text, parse_mode='html')

    elif group.get(call.from_user.id) is None:
        try:
            numbers = re.findall(r'\d+', call.data)
            if int(numbers[0]) > 101:
                group[call.from_user.id] = call.data
                response_text = f"Выбрана группа: {group[call.from_user.id]}. Выберите лабораторную работу:"
                js = '''
                    ["ЛР0", "ЛР1", "ЛР2", "ЛР3"]
                '''
                key = create_butt_from_url(f"{http_start}"
                                           f"/courses/domain[call.from_user.id]/groups/group[call.from_user.id]/labs",
                                           call.from_user.id, 'labs', js)
                bot.send_message(call.message.chat.id, response_text, parse_mode='html', reply_markup=key)
            else:
                raise Exception
        except:
            response_text = f"Произошла ошибка при выборе группы. Проверьте корректность ваших действий"
            bot.send_message(call.message.chat.id, response_text, parse_mode='html')
    elif fio.get(call.from_user.id) is None:
        try:
            if "ЛР" in call.data:
                lab[call.from_user.id] = call.data
                response_text = f"Выбрана лабораторная: {lab[call.from_user.id]}. Введите ваше ФИО:"
            else:
                raise Exception
            bot.send_message(call.message.chat.id, response_text, parse_mode='html')
        except:
            response_text = f"Произошла ошибка при выборе лабораторной. Проверьте корректность ваших действий"
            bot.send_message(call.message.chat.id, response_text, parse_mode='html')

    else:
        try:
            numbers = re.findall(r'\d+', call.data)
            if int(numbers[0]) > 101:
                lab[call.from_user.id] = call.data
                response_text = f"Выбрана лабораторная: {lab[call.from_user.id]}."
                bot.send_message(call.message.chat.id, response_text, parse_mode='html')
                js = '''
                    {"message": "Сообщение о проверке лр"}
                '''
                answer = check_lab(lab[call.from_user.id], git[call.from_user.id], call.from_user.id, js)
                response_text = f"Здравствуй, {fio[call.from_user.id]}. Лабораторная проверена. Результат: {answer}"
                bot.send_message(call.message.chat.id, response_text, parse_mode='html')
            else:
                raise Exception
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
        fio[message.from_user.id] = message.html_text
        response_text = f"Здравствуй, {fio[message.from_user.id]}. Введите ваш логин GitHub"
        bot.send_message(message.chat.id, response_text, parse_mode='html')
    elif git.get(message.from_user.id) is None:
        git[message.from_user.id] = message.html_text

        names = fio[message.from_user.id].split()
        if len(names) < 2:
            response_text = f"ФИО некоректно. Повторите ввода ФИО и GitHub заново"
            del fio[message.from_user.id]
            del git[message.from_user.id]
            bot.send_message(message.chat.id, response_text, parse_mode='html')
        firstname = names[1]
        surname = names[0]
        if len(names) == 3:
            patr = names[2]
        else:
            patr = ''
        # json_response = requests.post(f'{http_start}/courses/{domain[message.from_user.id]}/groups/'
        #                               f'{group[message.from_user.id]}/register',
        #                               json={'name': f'{firstname}', 'surname' : f'{surname}',
        #                                     'patronymic' : f'{patr}', 'github' : f'{git[message.from_user.id]}'})
        js = '''
        {
            "message": "сообщение об ошибке или успешном выполнении запроса"
        }
        '''
        json_response = response = Resp(200, js)
        data = json_response.json #()
        answ = json.loads(data)
        if json_response.status_code == 200 or json_response.status_code == 202:
            response_text = f"{answ['message']}"
            bot.send_message(message.chat.id, response_text, parse_mode='html')
            js = '''
                {"message": "Сообщение о проверке лр"}
            '''
            answer = check_lab(lab[message.from_user.id], git[message.from_user.id], message.from_user.id, js)
            response_text = f"{fio[message.from_user.id]}, лабораторная проверена. Результат: {answer}"
            bot.send_message(message.chat.id, response_text, parse_mode='html')

        else:
            response_text = f"Такого пользователя не существует. Повторите ввод ФИО и GitHub"
            del fio[message.from_user.id]
            del git[message.from_user.id]
            bot.send_message(message.chat.id, response_text, parse_mode='html')


while True:
    try:
        bot.polling(none_stop=True)
    except:
        time.sleep(10)
