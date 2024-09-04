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
    verify_student_registration_on_GitHub,
    verify_student_registration
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




@app.post("/courses/{course_id}/check-registration")
async def check_registration(course_id: str, student_name: str, group_number: str):
    course_file = f'courses/{course_id}.yaml'
    course_config = load_course_config(course_file)
    spreadsheet_id = course_config['course']['google']['spreadsheet']
    check_student = verify_student_registration(spreadsheet_id, student_name, group_number)
    print(check_student)
    if check_student:
        raise HTTPException(
            status_code=200,
            detail={"OK": "Студент зарегистрирован в Google таблице"}
        )
    elif check_student != True :
         raise HTTPException(
            status_code=400,
            detail={"Ошибка": "Студент не зарегистрирован или не имеет GitHub профиля"}
        )

   


@app.post("/github/{org}/repos/{repo}/check-repo")
async def check_github_repo(course_id: str, lab_id: str,student_name: str, group_number: str):
    course_file = f'courses/{course_id}.yaml'
    course_config = load_course_config(course_file)
    spreadsheet_id = course_config['course']['google']['spreadsheet']
    github_username = verify_student_registration_on_GitHub(spreadsheet_id, student_name, group_number)
    org = course_config['course']['github']['organization']
    repo_prefix = course_config['course']['labs'][lab_id]['github-prefix']

    # Формирование имени репозитория
    repo_name = f"{repo_prefix}-{github_username}"
    repo_url = f"https://api.github.com/repos/{org}/{repo_name}/contents/"

    response = requests.get(repo_url, auth=HTTPBasicAuth(github_username, GITHUB_TOKEN))
    print(repo_url)
    if response.status_code == 200:
        return {"message": "Репозиторий доступен", "repo_contents": response.json()}
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Ошибка при подключении к репозиторию: {response.text}"
        )
    
@app.get("/github/{org}/repos/{repo}/download-pdf")
async def download_pdf(org: str, repo: str, github_username: str):
    repo_url = f"https://api.github.com/repos/{org}/{repo}/contents/"
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
            save_path = "tmp/upload_report.pdf"
            with open(save_path, 'wb') as file:
                file.write(pdf_response.content)
            return {"message": "Файл успешно загружен", "save_path": save_path}
        else:
            raise HTTPException(
                status_code=pdf_response.status_code,
                detail=f"Ошибка при загрузке PDF: {pdf_response.text}"
            )
    
    raise HTTPException(status_code=404, detail="Ошибка при подключении к репозиторию")
        
@app.post("/courses/{course_id}/labs/{lab_id}/verify-report")
async def verify_report(course_id: str, lab_id: str, student_name: str, group_number: str):
    tmp_path = "tmp/upload_report.pdf"
    errors = []  # Список для накопления ошибок
    
    try:
        # Загрузка конфигурации курса и лабораторной работы
        course_file = f'courses/{course_id}.yaml'
        course_config = load_course_config(course_file)
        lab_config = get_lab_config(course_config, lab_id)

        # Чтение PDF-файла
        reader = PdfReader(tmp_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
            

        # Проверка титульной страницы
        title_errors, extracted_student_name, extracted_group_number = check_title_page(
            text, course_config, lab_id
        )

        
        
        # Проверка наличия ошибок на титульной странице
        if title_errors:
            errors.append({"Ошибки на титульной странице": title_errors})

        # Нормализация имен для сравнения
        normalized_extracted_name = normalize_full_name(extracted_student_name)
        normalized_student_name = normalize_full_name(student_name)

        # Разделение на части для получения фамилии и инициалов
        extracted_parts = normalized_extracted_name.split()
        student_parts = normalized_student_name.split()

        # Сравнение фамилий (без учета регистра)
        extracted_surname = extracted_parts[0] if extracted_parts else ""
        student_surname = student_parts[0] if student_parts else ""

        if extracted_surname.lower() != student_surname.lower():
            errors.append({"Ошибка": "Несоответствие Фамилии студента"})

        # Сравнение инициалов
        extracted_initials = extracted_parts[1] if len(extracted_parts) > 1 else ""
        student_initials = student_parts[1] if len(student_parts) > 1 else ""
        print(extracted_initials,student_initials)
        # Проверка первой буквы инициалов имени
        if extracted_initials and student_initials and extracted_initials[0] != student_initials[0]:
            errors.append({"Ошибка": "Несоответствие Инициалов студента"})

        # Если у извлеченного имени есть отчество, проверяем его
        if len(extracted_initials) > 2 and len(student_initials) > 2:
            if extracted_initials[2] != student_initials[2]:
                errors.append({"Ошибка": "Несоответствие Инициалов студента"})

    

        # Проверка наличия необходимых секций в отчете
        missing_sections = check_report_sections(text, lab_config['report'])
        if missing_sections:
            raise HTTPException(
                status_code=400,
                detail={"Ошибки на титульной странице": errors, "Отсутствующие секции в отчете": missing_sections}
            )

        # Возвращение успешного результата, если все проверки пройдены
        return {"Результат": "Отчет корректен", "Отсутствующие секции": missing_sections}
    finally:
        # Удаление временного файла
       print("Hi")
       #os.remove(tmp_path)
       

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

