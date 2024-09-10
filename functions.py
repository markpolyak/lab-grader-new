import re  # для регулярок
import gspread  # для работы с Google Sheets
from oauth2client.service_account import ServiceAccountCredentials  # Для авторизации с помощью Google API
from errors import list_of_title_errors

# Подключаемся к Google Sheets 
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"] 
credentials = ServiceAccountCredentials.from_json_keyfile_name('g-sheets/practice-432718-3f4f2a0086ea.json', scope)  # читаем файл с ключами
gc = gspread.authorize(credentials)  # авторизуемся с этими ключами


def check_report_sections(text, required_sections):
    found_sections = [section for section in required_sections if section in text]  # ищем в тексте секции, которые нашли
    missing_sections = [section for section in required_sections if section not in found_sections]  # смотрим, чего не хватает
    return missing_sections  


def transform_name_format(name):
    name_parts = name.split()  
    
    
    if len(name_parts) == 3:
        surname = name_parts[0]  # Фамилия
        initials = ' '.join(name_parts[1:])  # Имя и Отчество как инициалы
        format1 = f"{surname} {initials}"  
        format2 = f"{initials} {surname}"  
    
   
    elif len(name_parts) == 2:
        surname = name_parts[0]  # Фамилия
        initials = name_parts[1]  # Имя
        format1 = f"{surname} {initials}"  
        format2 = f"{initials} {surname}"  
    
   
    else:
        format1 = name
        format2 = name
    
    return format1, format2  # Возвращаем оба варианта


def check_title_page(text, course_config, lab_id):
    title_text = text 
    errors = [] 

    course = course_config['course']  
    course_name = course['name']  
    alt_names = course['alt-names']  
    course_name_upper = course_name.upper()  
    alt_names_upper = [name.upper() for name in alt_names] 

    semester = str(course['semester'].split()[-1])  # Номер семестра (последний элемент строки)

    teacher_name = course_config['course']['staff'][1]['name']  # Имя преподавателя
    teacher_name = normalize_full_name(teacher_name)  # Прихорашиваем имя преподавателя в нормальный вид
    teacher_name_format_1, teacher_name_format_2 = transform_name_format(teacher_name)  
    teacher_title = course_config['course']['staff'][0]['title']  
    teacher_title_no_spaces = teacher_title.replace(" ", "")  # Должность без пробелов (на всякий случай)

    # Проверка на наличие имени курса в титульной странице
    if course_name not in title_text and not any(alt_name in title_text for alt_name in alt_names) \
            and course_name_upper not in title_text and not any(alt_name_upper in title_text for alt_name_upper in alt_names_upper):
        errors.append(list_of_title_errors[2])  

    # Проверка на наличие имени преподавателя в титульной странице
    if (teacher_name not in title_text and 
        teacher_name_format_1 not in title_text and 
        teacher_name_format_2 not in title_text):
        errors.append(list_of_title_errors[3]) 

    # Проверка на наличие должности преподавателя в титульной странице
    if teacher_title not in title_text and teacher_title_no_spaces not in title_text:
        errors.append(list_of_title_errors[4]) 

    # Формируем строку с названием лабораторной работы
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

    return errors  # Возвращаем все найденные ошибки


def verify_student_registration(spreadsheet_id, student_name, group_name):
    try:
        sheet = gc.open_by_key(spreadsheet_id).worksheet(group_name)  # Открываем лист с нужной группой
        students = sheet.col_values(2)  
        if student_name not in students:
            return False  # Если имени нет в списке, студент не зарегистрирован
    except gspread.exceptions.WorksheetNotFound:
        return False  # Если лист не найден, тоже возвращаем False

    return True  # Если всё ок, студент зарегистрирован


def get_GitHub_username(spreadsheet_id, student_name, group_name):
    sheet = gc.open_by_key(spreadsheet_id).worksheet(group_name)  
    headers = sheet.row_values(1)

    github_col_index = headers.index("GitHub") + 1  # Находим индекс колонки с GitHub

    student_row_index = None  
    for row in sheet.col_values(2): 
        if row and row[1] == student_name: 
            student_row_index = sheet.find(student_name).row  # Получаем номер строки
            break

    if student_row_index is None:
        return None  

    cell_value = sheet.cell(student_row_index, github_col_index).value  # Получаем значение ячейки с GitHub-логином

    return cell_value  


def normalize_full_name(full_name):
    if full_name is None:
        return 'О О.О'  # Если имя пустое, возвращаем дефолтное значение

    # Удаляем лишние пробелы, разбиваем имя на части
    name_parts = re.sub(r'\s+', ' ', full_name).strip().split()
    if len(name_parts) == 3:  
        surname = name_parts[0].capitalize()  # Приводим фамилию с заглавной буквы
        first_initial = name_parts[1][0].upper()  
        middle_initial = name_parts[2][0].upper() 
        return f"{surname} {first_initial}.{middle_initial}."
    
    elif len(name_parts) == 2:  # Если только фамилия и имя
        surname = name_parts[0].capitalize()
        first_initial = name_parts[1][0].upper()
        return f"{surname} {first_initial}."
    
    # Если имя дано в виде инициалы.Фамилия
    match = re.match(r'([А-ЯЁA-Z])\.([А-ЯЁA-Z])\.(.+)', full_name)
    if match:
        first_initial = match.group(1).upper()
        middle_initial = match.group(2).upper()
        surname = match.group(3).capitalize().strip()
        return f"{surname} {first_initial}.{middle_initial}."
    
    # Если ничего не подошло, возвращаем как есть
    return full_name