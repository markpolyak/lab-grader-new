import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from errors import list_of_title_errors

# Загрузка учетных данных Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('src/g-sheets/parsing-428822-d0f161bcdd17.json', scope)
gc = gspread.authorize(credentials)


def extract_student_info(title_text):
    # Паттерн для поиска номера группы
    group_pattern = r'((?:\d{4}К)|(?:М\d{3})|(?:\d{4}K)|(?:M\d{3})|(?:\d+))'

    # Паттерн для поиска ФИО
    name_pattern = r'([А-ЯЁA-Z]\.[А-ЯЁA-Z]\.\s*[А-ЯЁA-Z][а-яёa-z]*|[А-ЯЁA-Z][а-яёa-z]+ [А-ЯЁA-Z]\.[А-ЯЁA-Z]\.|[А-ЯЁA-Z]\.[А-ЯЁA-Z]\.[А-ЯЁA-Z][а-яёa-z]+)'

    # Полный паттерн для поиска группы и ФИО с промежуточными данными
    full_pattern = rf'{group_pattern}\s*(?:\S*\s*)?{name_pattern}'

    match = re.search(full_pattern, title_text, re.UNICODE)

    if match:
        group_number = match.group(1)
        student_name = match.group(2)
        return student_name, group_number
    return None, None


# Функция для проверки наличия необходимых секций в документе
def check_report_sections(doc, required_sections):
    # Извлечение текста всех параграфов из документа
    found_sections = {p.text for p in doc.paragraphs}
    # Определение отсутствующих секций, которые должны быть в документе
    missing_sections = [section for section in required_sections if section not in found_sections]
    return missing_sections

# Функция для трансформации формата имени
def transform_name_format(name):
    # Разделение строки по пробелам
    parts = name.split()
    if len(parts) == 2:
        last_name = parts[0]
        initials = parts[1]
        initials_with_space = f"{initials} {last_name}"
        initials_without_space = f"{initials}{last_name}"
        return initials_with_space, initials_without_space
    return name, name  # Если строка не соответствует ожидаемому формату, возвращаем её без изменений

# Функция для проверки титульной страницы
def check_title_page(doc, course_config, lab_id):
    # Инициализация переменной для хранения текста титульной страницы
    title_text = ""

    # Извлечение текста всех абзацев и таблиц
    for para in doc.paragraphs:
        title_text += " " + para.text
        if re.search(r'Санкт-Петербург\s+\d{4}', para.text):
            break

    # Извлечение текста из всех таблиц
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    title_text += " " + paragraph.text

    # Извлечение имени студента и номера группы из текста на титульной странице
    student_name, group_number = extract_student_info(title_text)

    # Инициализация списка для хранения ошибок
    errors = []

    # Извлечение информации о курсе из конфигурационного файла
    course = course_config['course']
    course_name = course['name']
    alt_names = course['alt-names']
    course_name_upper = course_name.upper()
    alt_names_upper = [name.upper() for name in alt_names]

    # Извлечение года семестра
    semester = str(course['semester'].split()[-1])

    # Извлечение имени и должности преподавателя из конфигурационного файла
    teacher_name = course_config['course']['staff'][1]['name']
    teacher_name = normalize_full_name(teacher_name)
    teacher_name_with_space, teacher_name_without_space = transform_name_format(teacher_name)
    teacher_title = course_config['course']['staff'][0]['title']
    teacher_title_no_spaces = teacher_title.replace(" ", "")

    # Проверка наличия имени студента и номера группы на титульном листе
    if student_name is None:
        errors.append(list_of_title_errors[0])

    if group_number is None:
        errors.append(list_of_title_errors[1])

    # Проверка корректности названия курса (учитываются альтернативные названия)
    if course_name not in title_text and not any(alt_name in title_text for alt_name in alt_names)\
            and course_name_upper not in title_text and not any(alt_names_upper in title_text for alt_names_upper in alt_names_upper):
        errors.append(list_of_title_errors[2])

    # Проверка наличия имени преподавателя на титульном листе
    if teacher_name not in title_text and teacher_name_with_space not in title_text and teacher_name_without_space not in title_text:
        errors.append(list_of_title_errors[3])

    # Проверка наличия должности преподавателя на титульном листе
    if teacher_title not in title_text and teacher_title_no_spaces not in title_text:
        errors.append(list_of_title_errors[4])

    # Формирование ожидаемого названия лабораторной работы
    named_rep = "Отчет о лабораторной работе "
    named_lab = named_rep + "№" + str(lab_id)
    named_lab_caps = named_rep.upper() + "№" + str(lab_id)

    # Проверка наличия ID лабораторной работы на титульном листе
    if named_lab not in title_text and named_lab_caps not in title_text:
        errors.append(list_of_title_errors[5])

    # Проверка корректности года семестра
    if semester not in title_text:
        errors.append(list_of_title_errors[6])



    # Возвращение списка найденных ошибок
    return errors, student_name, group_number

# Функция для проверки регистрации студента в Google Sheets
def verify_student_registration(spreadsheet_id, student_name, group_name):
    try:
        # Открытие Google Sheets по идентификатору таблицы и названию листа (группы)
        sheet = gc.open_by_key(spreadsheet_id).worksheet(group_name)

        # Извлечение значений из второго столбца - имена студентов
        students = sheet.col_values(2)

        # Проверка наличия имени студента в списке имен
        if student_name not in students:
            return False
    except gspread.exceptions.WorksheetNotFound:
        # Обработка исключения, если лист с именем группы не найден
        return False

    # Возвращение True, если студент зарегистрирован
    return True

# Функция для нормализации имени студента
def normalize_name(name):
    # Удаляем все пробелы
    name = re.sub(r'\s+', '', name)

    # Проверка и обработка форматов имен
    match = re.match(r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.([А-ЯЁA-Z][а-яёa-z]+)', name)
    if match:
        # Формат "И.О.Фамилия"
        initials = f"{match.group(1)}.{match.group(2)}."
        surname = match.group(3)
        return f"{surname} {initials}"

    match = re.match(r'([А-ЯЁA-Z][а-яёa-z]+)([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.', name)
    if match:
        # Формат "ФамилияИ.О."
        surname = match.group(1)
        initials = f"{match.group(2)}.{match.group(3)}."
        return f"{surname} {initials}"

    match = re.match(r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\. ([А-ЯЁA-Z][а-яёa-z]+)', name)
    if match:
        # Формат "И.О. Фамилия"
        initials = f"{match.group(1)}.{match.group(2)}."
        surname = match.group(3)
        return f"{surname} {initials}"

    match = re.match(r'([А-ЯЁA-Z][а-яёa-z]+) ([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.', name)
    if match:
        # Формат "Фамилия И.О."
        surname = match.group(1)
        initials = f"{match.group(2)}.{match.group(3)}."
        return f"{surname} {initials}"

    # Если ни один формат не подошел, возвращаем исходное имя
    return name

# Функция для нормализации полного имени
def normalize_full_name(full_name):
    # Удаляем лишние пробелы и разбиваем строку на компоненты
    name_parts = re.sub(r'\s+', ' ', full_name).strip().split()

    # Проверка, что в имени есть фамилия, имя и отчество
    if len(name_parts) == 3:
        surname = name_parts[0]
        first_initial = name_parts[1][0]
        middle_initial = name_parts[2][0]
        return f"{surname} {first_initial}.{middle_initial}."

    # Если формат не соответствует "Фамилия Имя Отчество", возвращаем исходное имя
    return full_name