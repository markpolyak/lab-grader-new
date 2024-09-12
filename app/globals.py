import os

from config import Config

config = Config("config.ini")
config.print()

################################################################################



################################################################################

import re

#
def all_names_varians(name):
    # Удаляем все пробелы
    name = re.sub(r'\s+', '', name)

    # Проверка форматов имен
    patterns = [
        r'([А-ЯЁA-Z][а-яёa-z]+)([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.',  # "ФамилияИ.О."
        r'([А-ЯЁA-Z][а-яёa-z]+) ([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.',  # "Фамилия И.О."
        r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.([А-ЯЁA-Z][а-яёa-z]+)',  # "И.О.Фамилия"
        r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\. ([А-ЯЁA-Z][а-яёa-z]+)'   # "И.О. Фамилия"
    ]

    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            if len(match.groups()) == 3:
                surname = match.group(1)
                initial1 = match.group(2)
                initial2 = match.group(3)
                return f"{surname} {initial1}.{initial2}."

    # Если ни один формат не подошел, возвращаем исходное имя
    return name

def fix_full_name(full_name):
    name_parts = re.sub(r'\s+', ' ', full_name).strip().split()

    if len(name_parts) == 3:
        return f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."

    return full_name

def parse_student_info(title_text):
    # Паттерн для поиска номера группы
    group_pattern = r'((?:\d{4}К)|(?:М\d{3})|(?:\d{4}K)|(?:M\d{3})|(?:\d+))'

    # Паттерн для поиска ФИО
    name_pattern = r'([А-ЯЁA-Z]\.[А-ЯЁA-Z]\.\s*[А-ЯЁA-Z][а-яёa-z]*|[А-ЯЁA-Z][а-яёa-z]+ [А-ЯЁA-Z]\.[А-ЯЁA-Z]\.|[А-ЯЁA-Z]\.[А-ЯЁA-Z]\.[А-ЯЁA-Z][а-яёa-z]+)'

    # Полный паттерн для поиска группы и ФИО с промежуточными данными
    full_pattern = rf'{group_pattern}\s*(?:\S*\s*)?{name_pattern}'

    match = re.search(full_pattern, title_text, re.UNICODE)
    group_number, student_name = None, None
    if match:
        group_number = match.group(1)
        student_name = match.group(2)
    return {
        "group_number": group_number,
        "student_name": student_name
    }

def transform_name_format(name):
    parts = name.split()
    if len(parts) == 2:
        return f"{parts[1]} {parts[0]}", f"{parts[1]}{parts[0]}"
    return name, name

################################################################################

def extract_digits(input_string):
    return ''.join(filter(str.isdigit, input_string))

################################################################################



################################################################################

import yaml

def read_config(file, lab_id):
    lab_key = str(lab_id)
    with open(file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    course = config.get('course', None)
    return {
        "report": course.get('labs', None).get(lab_key, None)["report"],
        "staff": course.get('staff', None)
    }
