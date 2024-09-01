from fastapi import FastAPI, HTTPException, status
import os
import tempfile
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PyPDF2 import PdfReader
from config_parser import load_course_config, get_lab_config
from functions import (
    check_report_sections,
    check_title_page,
    normalize_full_name,
    verify_student_registration_on_GitHub
)
from GIt_token import GITHUB_TOKEN
from requests.auth import HTTPBasicAuth
from errors import list_of_title_errors

app = FastAPI()

# Загрузка учетных данных Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'g-sheets/practice-432718-3f4f2a0086ea.json', scope
)
gc = gspread.authorize(credentials)





@app.post("/courses/{course_id}/labs/{lab_id}/upload-report")
async def upload_report(course_id: str, lab_id: str, student_name: str, group_number: str):
    # Загрузка конфигурации курса и лабораторной работы
    try:
        course_file = f'courses/{course_id}.yaml'
        course_config = load_course_config(course_file)
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={"Ошибка": "Конфигурация лабораторной работы не найдена"}
        )

    # Проверка регистрации студента в Google Sheets
    spreadsheet_id = course_config['course']['google']['spreadsheet']
    github_username = verify_student_registration_on_GitHub(spreadsheet_id, student_name, group_number)
    if not github_username:
        raise HTTPException(
            status_code=404,
            detail={"Ошибка": "Студент не зарегистрирован или не имеет GitHub профиля"}
        )

    # Извлечение данных из конфигурационного файла
    org = course_config['course']['github']['organization']
    repo_prefix = course_config['course']['labs'][lab_id]['github-prefix']

    # Формирование имени репозитория
    repo_name = f"{repo_prefix}-{github_username}"
    repo_url = f"https://api.github.com/repos/{org}/{repo_name}/contents/"

    # Запрос к GitHub API для проверки и скачивания файла report.pdf
    save_path = "D:/sem 6/practice/src/tmp/upload_report.pdf"
    response = requests.get(repo_url, auth=HTTPBasicAuth(github_username, GITHUB_TOKEN))
    
    if response.status_code == 200:
        repo_contents = response.json()
        pdf_file = None

        # Поиск файла report.pdf в содержимом репозитория
        for item in repo_contents:
            if item['name'] == 'report.pdf' and item['type'] == 'file':
                pdf_file = item['download_url']
                break

        if not pdf_file:
            raise HTTPException(status_code=404, detail="Файл report.pdf не найден в репозитории")

        # Скачивание PDF-файла
        pdf_response = requests.get(pdf_file, auth=HTTPBasicAuth(github_username, GITHUB_TOKEN))

        if pdf_response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(pdf_response.content)
            return {"message": f"Файл успешно загружен."}
        else:
            raise HTTPException(
                status_code=pdf_response.status_code,
                detail=f"Ошибка при загрузке PDF: {pdf_response.text}"
            )

    # Сохранение PDF файла во временное хранилище
    pdf_content = response.content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_content)
        
@app.post("/courses/{course_id}/labs/{lab_id}/verify-report")
async def verify_report(course_id: str, lab_id: str, student_name: str, group_number: str):
    tmp_path = "tmp/upload_report.pdf"
    try:
        course_file = f'courses/{course_id}.yaml'
        course_config = load_course_config(course_file)
        lab_config = get_lab_config(course_config, lab_id)
        reader = PdfReader(tmp_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Проверка титульной страницы
        title_errors, extracted_student_name, extracted_group_number = check_title_page(
            text, course_config, lab_id
        )
        if title_errors:
            raise HTTPException(
                status_code=400,
                detail={"Ошибки на титульной странице": title_errors}
            )

        # Нормализация имен для сравнения
       
        
        print(f"Оригинальные имена:\nИзвлеченное: {extracted_student_name}\nОжидаемое: {student_name}")
        
        

    # Проверка совпадения переданного и извлеченного ФИО
         # Нормализация имен
        normalized_extracted_name = normalize_full_name(extracted_student_name)
        normalized_student_name = normalize_full_name(student_name)
        print(f"Сравнение имен:\nИзвлеченное: {normalized_extracted_name}\nОжидаемое: {normalized_student_name}")
        # Разделение на части для получения фамилии и инициалов
        extracted_parts = normalized_extracted_name.split()
        student_parts = normalized_student_name.split()
        
        extracted_surname = extracted_parts[0]
        student_surname = student_parts[0]

        # Сравнение фамилий (без учета регистра)
        if extracted_surname.lower() != student_surname.lower():
            raise HTTPException(
                status_code=400,
                detail={"Ошибка": "Несоответствие Фамилии"}
            )

        # Сравнение инициалов
        extracted_initials = extracted_parts[1] if len(extracted_parts) > 1 else ""
        student_initials = student_parts[1] if len(student_parts) > 1 else ""

        # Проверка первой буквы инициалов имени
        if extracted_initials[0] != student_initials[0]:
            raise HTTPException(
                status_code=400,
                detail={"Ошибка": "Несоответствие Инициалов"}
            )

        # Если у извлеченного имени есть отчество, проверяем его
        if len(extracted_initials) > 2:
            if len(student_initials) > 2:
                if extracted_initials[2] != student_initials[2]:
                    raise HTTPException(
                        status_code=400,
                        detail={"Ошибка": "Несоответствие Инициалов"}
                    )
            # Если в ожидаемом имени нет отчества, проверку пропускаем
            

        if extracted_group_number != group_number:
            raise HTTPException(
                status_code=400,
                detail={"Ошибка": "Несоответствие номера группы"}
            )

        # Проверка наличия необходимых секций в отчете
        missing_sections = check_report_sections(text, lab_config['report'])
        if missing_sections:
            raise HTTPException(
                status_code=400,
                detail={"Отсутствующие секции в отчете": missing_sections}
            )

        # Возвращение успешного результата, если все проверки пройдены
        return {"Результат": "Отчет корректен", "Отсутствующие секции": missing_sections}

    finally:
        # Удаление временного файла
       print("Hi")
       

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

