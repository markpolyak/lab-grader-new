from fastapi import FastAPI, HTTPException, UploadFile, File  # модули FastAPI
import uvicorn
import os 
import tempfile  
import requests  
import gspread  
from oauth2client.service_account import ServiceAccountCredentials  
from PyPDF2 import PdfReader  
from config_parser import load_course_config, get_lab_config  
from functions import *  
from GIt_token import GITHUB_TOKEN  
from requests.auth import HTTPBasicAuth  
from errors import list_of_title_errors  

app = FastAPI()  


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'g-sheets/practice-432718-3f4f2a0086ea.json', scope
)
gc = gspread.authorize(credentials)  


# для проверки регистрации студента в Google Sheets
@app.post("/courses/{course_id}/check-registration")
async def check_registration(course_id: str, student_name: str, group_number: str):
    course_file = f'courses/{course_id}.yaml' 
    course_config = load_course_config(course_file)  
    spreadsheet_id = course_config['course']['google']['spreadsheet']  
    check_student = verify_student_registration(spreadsheet_id, student_name, group_number) 
    
    if check_student:
        return {"message": "Студент зарегистрирован в Google таблице"}
    else:
        raise HTTPException(
            status_code=400,
            detail={"Ошибка": "Студент не зарегистрирован в Google таблице"}
        )


#  для проверки наличия репозитория на GitHub
@app.post("/github/{org}/repos/{repo}/check-repo")
async def check_github_repo(course_id: str, lab_id: str, student_name: str, group_number: str):
    course_file = f'courses/{course_id}.yaml'  
    course_config = load_course_config(course_file)  
    spreadsheet_id = course_config['course']['google']['spreadsheet']  
    org = course_config['course']['github']['organization']  
    repo_prefix = course_config['course']['labs'][lab_id]['github-prefix']  
    
    github_username = get_GitHub_username(spreadsheet_id, student_name, group_number)  
    
    if github_username is None:
        return {f"Студент с именем '{student_name}' не найден."}
    
    
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
    

# для скачивания PDF-файла из репозитория на GitHub
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

        
        pdf_response = requests.get(pdf_file, auth=HTTPBasicAuth(github_username, GITHUB_TOKEN))

        if pdf_response.status_code == 200:
            save_path = f"tmp/{repo}.pdf"  
            with open(save_path, 'wb') as file:
                file.write(pdf_response.content)  # сохраняем файл на диск
            return {"message": "Файл успешно загружен", "save_path": save_path}
        else:
            raise HTTPException(
                status_code=pdf_response.status_code,
                detail=f"Ошибка при загрузке PDF: {pdf_response.text}"
            )
    
    raise HTTPException(status_code=404, detail="Ошибка при подключении к репозиторию")

        
# для проверки ПДФника
@app.post("/courses/{course_id}/labs/{lab_id}/verify-report")
async def verify_report(course_id: str, lab_id: str, student_name: str, group_number: str, file: UploadFile = File(...)):
    # сохраняем во временном хранилище,   Опять ):  
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        
        course_file = f'courses/{course_id}.yaml'
        course_config = load_course_config(course_file)
        lab_config = get_lab_config(course_config, lab_id)

        # Чтение PDF-файла
        reader = PdfReader(tmp_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()  # Извлекаем текст из всех страниц PDF

       
        title_errors = check_title_page(
            text, course_config, lab_id
        )

        
        normalize_student_name = normalize_full_name(student_name)
        normalize_student_name_format_1, normalize_student_name_format_2 = transform_name_format(normalize_student_name)
        split_student_normal_name = normalize_student_name_format_2.split()[1]

      
        if normalize_student_name not in text and normalize_student_name_format_2 not in text and split_student_normal_name not in text:
            title_errors.append({"Ошибка": list_of_title_errors[0]})
        
        if group_number not in text:
            title_errors.append({"Ошибка": list_of_title_errors[1]})


        missing_sections = check_report_sections(text, lab_config['report'])
        if missing_sections:
            raise HTTPException(
                status_code=400,
                detail={"Ошибки на титульной странице": title_errors, "Отсутствующие секции в отчете": missing_sections}
            )
        
        
        return {"Отчет корректен"}
    finally:
        os.remove(tmp_path)  # делитаем файл



