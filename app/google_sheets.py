import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

logger = logging.getLogger(__name__)


def get_gspread_client(creds_file):
    # Используем учетные данные Service Account для доступа к Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    return gspread.authorize(creds)


def find_student(sheet_id: str, sheet_name: str, creds_file: str, github: str = None, name: str = None):
    try:
        # Проверка аргументов github и name на пустоту
        if name == '' and github == '':
            return {"error": "Empty arguments"}

        client = get_gspread_client(creds_file)
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

        # Получаем заголовки из первых двух строк
        headers_row_1 = sheet.row_values(1)
        headers_row_2 = sheet.row_values(2)

        # Ищем индексы столбцов "Ф.И.О." и "GitHub"
        if 'Ф.И.О.' in headers_row_1:
            fio_index = headers_row_1.index('Ф.И.О.')
        elif 'Ф.И.О.' in headers_row_2:
            fio_index = headers_row_2.index('Ф.И.О.')
        else:
            raise ValueError("Не удалось найти заголовок 'Ф.И.О.'")

        if 'GitHub' in headers_row_1:
            github_index = headers_row_1.index('GitHub')
        elif 'GitHub' in headers_row_2:
            github_index = headers_row_2.index('GitHub')
        else:
            raise ValueError("Не удалось найти заголовок 'GitHub'")

        logger.info(f"Ф.И.О. Index: {fio_index}, GitHub Index: {github_index}")

        # Получаем данные начиная с третьей строки
        data = sheet.get_all_values()[2:]

        students = []
        for row in data:
            if len(row) > max(fio_index, github_index):  # Проверяем, что индекс не выходит за пределы строки
                student = {
                    'Ф.И.О.': row[fio_index],
                    'GitHub': row[github_index]
                }
                students.append(student)

        # logger.info(f"Ф.И.О. {students}")

        matched_by_github = None
        matched_by_name = None

        if github:
            for student in students:
                if student.get('GitHub') == github:
                    matched_by_github = student
                    logger.info(f"Ф.И.О.name {student}")
                    break
        if name:
            for student in students:
                if student.get('Ф.И.О.') == name:
                    logger.info(f"Ф.И.О.git {student}")
                    matched_by_name = student
                    break

        if matched_by_github and name == '':
            return matched_by_github

        if matched_by_name and github == '':
            return matched_by_name

        if matched_by_github and matched_by_name:
            return matched_by_github

        if (matched_by_github and not matched_by_name) or (not matched_by_github and matched_by_name):
            return {"error": "Несоответствие ФИО и имени пользователя на GitHub"}

    except Exception as e:
        logger.error(f"Error finding student: {e}")
        raise e
