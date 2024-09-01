import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PyPDF2 import PdfReader
from errors import list_of_title_errors

# Загрузка учетных данных Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('g-sheets/practice-432718-3f4f2a0086ea.json', scope)
gc = gspread.authorize(credentials)

# Функция для извлечения информации о студенте из текста PDF файла
def extract_student_info(title_text):
    group_pattern = r'((?:\d{4}К)|(?:М\d{3})|(?:\d{4}K)|(?:M\d{3})|(?:\d+))'
    name_pattern = r'([А-ЯЁA-Z]\.[А-ЯЁA-Z]\.\s*[А-ЯЁA-Z][а-яёa-z]*|[А-ЯЁA-Z][а-яёa-z]+ [А-ЯЁA-Z]\.[А-ЯЁA-Z]\.|[А-ЯЁA-Z]\.[А-ЯЁA-Z]\.[А-ЯЁA-Z][а-яёa-z]+)'
    full_pattern = rf'{group_pattern}\s*(?:\S*\s*)?{name_pattern}'

    match = re.search(full_pattern, title_text, re.UNICODE)

    if match:
        group_number = match.group(1)
        student_name = match.group(2)
        return student_name, group_number
    return None, None

# Функция для проверки наличия необходимых секций в PDF файле
def check_report_sections(text, required_sections):
    found_sections = [section for section in required_sections if section in text]
    missing_sections = [section for section in required_sections if section not in found_sections]
    return missing_sections

# Функция для трансформации формата имени
def transform_name_format(name):
    parts = name.split()
    if len(parts) == 2:
        last_name = parts[0]
        initials = parts[1]
        initials_with_space = f"{initials} {last_name}"
        initials_without_space = f"{initials}{last_name}"
        return initials_with_space, initials_without_space
    return name, name

# Функция для проверки титульной страницы
def check_title_page(text, course_config, lab_id):
    title_text = text
    student_name, group_number = extract_student_info(title_text)
    errors = []

    course = course_config['course']
    course_name = course['name']
    alt_names = course['alt-names']
    course_name_upper = course_name.upper()
    alt_names_upper = [name.upper() for name in alt_names]

    semester = str(course['semester'].split()[-1])

    teacher_name = course_config['course']['staff'][1]['name']
    teacher_name = normalize_full_name(teacher_name)
    teacher_name_with_space, teacher_name_without_space = transform_name_format(teacher_name)
    print(teacher_name)
    teacher_title = course_config['course']['staff'][0]['title']
    teacher_title_no_spaces = teacher_title.replace(" ", "")

    if student_name is None:
        errors.append(list_of_title_errors[0])

    if group_number is None:
        errors.append(list_of_title_errors[1])

    if course_name not in title_text and not any(alt_name in title_text for alt_name in alt_names)\
            and course_name_upper not in title_text and not any(alt_names_upper in title_text for alt_names_upper in alt_names_upper):
        errors.append(list_of_title_errors[2])

    if teacher_name not in title_text and teacher_name_with_space not in title_text and teacher_name_without_space not in title_text:
        errors.append(list_of_title_errors[3])

    if teacher_title not in title_text and teacher_title_no_spaces not in title_text:
        errors.append(list_of_title_errors[4])

    named_rep = "отчет о лабораторной работе "
    named_lab = named_rep + "№" + str(lab_id)
    named_lab_no_spaces = named_lab.replace(" ", "")
    named_lab_caps = named_rep.upper() + "№" + str(lab_id)
    named_lab_caps_no_spaces = named_lab_caps.replace(" ", "")

    # Проверяем наличие строки без учета пробелов
    title_text_no_spaces = title_text.replace(" ", "")
    if named_lab_no_spaces not in title_text_no_spaces and named_lab_caps_no_spaces not in title_text_no_spaces:
        errors.append(list_of_title_errors[5])
    if semester not in title_text:
        errors.append(list_of_title_errors[6])

    return errors, student_name, group_number

# Функция для проверки регистрации студента в Google Sheets
def verify_student_registration(spreadsheet_id, student_name, group_name):
    try:
        sheet = gc.open_by_key(spreadsheet_id).worksheet(group_name)
        students = sheet.col_values(2)
        if student_name not in students:
            return False
    except gspread.exceptions.WorksheetNotFound:
        return False

    return True

def verify_student_registration_on_GitHub(spreadsheet_id, student_name, group_name):
    try:
        sheet = gc.open_by_key(spreadsheet_id).worksheet(group_name)
        headers = sheet.row_values(1)
        try:
            github_col_index = headers.index("GitHub") + 1  
        except ValueError:
            print("Столбец с названием 'GitHub' не найден.")
            return

        student_row_index = None
        for row in sheet.get_all_values():
            if row and row[1] == student_name:  
                student_row_index = sheet.find(student_name).row
                break

        if student_row_index is None:
            print(f"Студент с именем '{student_name}' не найден.")
            return

        cell_value = sheet.cell(student_row_index, github_col_index).value

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return cell_value

# Функция для нормализации имени студента
def normalize_name(name):
    # Удаление всех пробелов для упрощения обработки
    name = re.sub(r'\s+', '', name)

    #Шаблоны для разных случаев записи имени
    patterns = [
        r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.([А-ЯЁA-Z][а-яёa-z]+)',  # И.О.Фамилия
        r'([А-ЯЁA-Z][а-яёa-z]+)([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.',  # ФамилияИ.О.
        r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.([А-ЯЁA-Z][а-яёa-z]+)',  # И.О. Фамилия (с пробелом)
        r'([А-ЯЁA-Z][а-яёa-z]+) ([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.',  # Фамилия И.О. (с пробелом)
    ]

    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            if len(match.groups()) == 3:
                surname = match.group(3) if pattern.startswith('([А-ЯЁA-Z])') else match.group(1)
                initials = f"{match.group(1)}.{match.group(2)}."
                return f"{surname} {initials}"

    return name  # Если ни один шаблон не подошел, возвращаем оригинальное имя

def normalize_full_name(full_name):
    # Удаление лишних пробелов и разбиение на части
    name_parts = re.sub(r'\s+', ' ', full_name).strip().split()

    if len(name_parts) == 3:
        surname = name_parts[0].capitalize()
        first_initial = name_parts[1][0].upper()
        middle_initial = name_parts[2][0].upper()
        return f"{surname} {first_initial}.{middle_initial}."
    
    elif len(name_parts) == 2:  # Обработка случая, когда есть только фамилия и имя
        surname = name_parts[0].capitalize()
        first_initial = name_parts[1][0].upper()
        return f"{surname} {first_initial}."
    
    # Обработка случая, когда имя дано в виде инициалы.Фамилия
    match = re.match(r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.(.+)', full_name)
    if match:
        first_initial = match.group(1).upper()
        middle_initial = match.group(2).upper()
        surname = match.group(3).capitalize().strip()
        return f"{surname} {first_initial}.{middle_initial}."
    
    # Если не подходит под шаблоны, возвращаем как есть
    return full_name

# Основная функция для обработки PDF файла
def process_pdf(pdf_path, course_config, lab_id):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        title_errors, student_name, group_number = check_title_page(text, course_config, lab_id)
        missing_sections = check_report_sections(text, course_config['course']['labs'][lab_id]['report'])

        if title_errors:
            return {"errors": title_errors}
        if missing_sections:
            return {"missing_sections": missing_sections}

        return {"student_name": student_name, "group_number": group_number, "status": "Valid"}
