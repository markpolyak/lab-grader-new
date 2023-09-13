import os
import yaml
import json
from flask import Flask, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# todo в файлах старых курсов не указаны short_name и запрос на лабы не срабатывает
# todo  защита от доступа к листам не читаемых запросом GET /courses/{course_id}/groups
# todo вынести путь к файлам курсов например в переменную

app = Flask(__name__)

# Путь к файлу с ключом
keyfile_path = 'tmpkey.json'

# Используем ключ сервисного аккаунта для аутентификации
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('tmpkey.json', scope)
client = gspread.authorize(creds)


@app.route('/courses/', methods=['GET'])
def get_courses():
    courses_dir = 'courses'
    courses_info = []

    if not os.path.exists(courses_dir) or not os.path.isdir(courses_dir):
        return jsonify([])

    for filename in os.listdir(courses_dir):
        file_path = os.path.join(courses_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.yaml'):
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    course_config = yaml.safe_load(file)
                    course_info = {
                        'id': filename,
                        'name': course_config.get('course', {}).get('name', ''),
                        'semester': course_config.get('course', {}).get('semester', '')
                    }
                    courses_info.append(course_info)
                except Exception as e:
                    print(f"Error reading {filename}: {str(e)}")

    return jsonify(courses_info)


@app.route('/courses/<course_id>/', methods=['GET'])
def get_course(course_id):
    courses_dir = 'courses'
    course_file = os.path.join(courses_dir, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        return jsonify({}), 404

    with open(course_file, 'r', encoding='utf-8') as file:
        try:
            course_config = yaml.safe_load(file)
            course_info = {
                'id': course_id,
                'config': f'{course_id}.yaml',
                'name': course_config.get('course', {}).get('name', ''),
                'semester': course_config.get('course', {}).get('semester', ''),
                'email': course_config.get('course', {}).get('email', ''),
                'github-organization': course_config.get('course', {}).get('github', {}).get('organization', ''),
                'google-spreadsheet': course_config.get('course', {}).get('google', {}).get('spreadsheet', '')
            }
            return jsonify(course_info)
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/courses_name_only/', methods=['GET'])
def get_course_names():
    courses_dir = 'courses'
    course_names = []

    if not os.path.exists(courses_dir) or not os.path.isdir(courses_dir):
        return jsonify([])

    for filename in os.listdir(courses_dir):
        file_path = os.path.join(courses_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.yaml'):
            course_names.append(filename)

    return jsonify(course_names)


@app.route('/courses/<course_id>/groups', methods=['GET'])
def get_course_groups(course_id):
    courses_dir = 'courses'
    course_file = os.path.join(courses_dir, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        return jsonify({}), 404

    with open(course_file, 'r', encoding='utf-8') as file:
        try:
            course_config = yaml.safe_load(file)
            google_spreadsheet_field = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')

            if not google_spreadsheet_field:
                return jsonify([]), 200  # Если нет ссылки на Google Spreadsheet, возвращаем пустой список групп

            # Формируем URL для таблицы на основе значения из YAML-файла
            google_spreadsheet_url = f'https://docs.google.com/spreadsheets/d/{google_spreadsheet_field}/edit?pli=1#gid=0'

            # Открываем таблицу по сформированному URL
            spreadsheet = client.open_by_url(google_spreadsheet_url)

            # Получаем список имен листов
            all_sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]

            info_sheet_name = course_config.get('course', {}).get('google', {}).get('info-sheet', '')

            # Убираем информационный лист из списка
            if info_sheet_name in all_sheet_names:
                all_sheet_names.remove(info_sheet_name)

            return jsonify(all_sheet_names), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/courses/<course_id>/groups/<group_id>/labs', methods=['GET'])
def get_course_group_labs(course_id, group_id):
    courses_dir = 'courses'
    course_file = os.path.join(courses_dir, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        return jsonify({}), 404

    with open(course_file, 'r', encoding='utf-8') as file:
        try:
            course_config = yaml.safe_load(file)
            google_spreadsheet = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')

            if not google_spreadsheet:
                return jsonify([]), 200

            # Получаем ссылку на Google Spreadsheet из конфигурационного файла
            spreadsheet_url = f'https://docs.google.com/spreadsheets/d/{google_spreadsheet}/edit?pli=1#gid=0'

            # Открываем таблицу по URL
            try:
                gc = gspread.service_account(filename='tmpkey.json')
                worksheet = gc.open_by_url(spreadsheet_url).worksheet(group_id)
            except gspread.exceptions.SpreadsheetNotFound as e:
                return jsonify({}), 404  # В случае ошибки 404, если таблица не найдена

            # Инициализируем пустой список для хранения сокращенных названий лабораторных работ
            lab_short_names = []

            # Извлекаем сокращенные названия лабораторных работ из конфигурационного файла
            lab_config = course_config.get('course', {}).get('labs', {})
            for lab_key in lab_config:
                short_name = lab_config[lab_key].get('short-name', '')
                if short_name:
                    lab_short_names.append(short_name)

            # Инициализируем пустой список для хранения найденных лабораторных работ
            group_labs = []

            # Проверяем наличие каждой лабораторной работы в таблице и добавляем ее в список, если есть
            for short_name in lab_short_names:
                if worksheet.find(short_name):  # Используем функцию find для поиска столбца
                    group_labs.append(short_name)

            return jsonify(group_labs), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
