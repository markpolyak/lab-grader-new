from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
from typing import List, Optional
import yaml
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from lab_template_generation import generate_lab_template

app = FastAPI()

# Загрузка конфигурационного файла и файла данных
config_path = 'operating-systems-2024.yaml'
credentials_path = 'credentials.json'

current_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(current_dir, config_path)
credentials_path = os.path.join(current_dir, credentials_path)

if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Проверка наличия ключа 'labs' внутри 'course'
if 'course' in config and 'labs' in config['course']:
    labs = config['course']['labs']
else:
    raise KeyError("Key 'labs' not found in configuration file")

config_last_modified = os.path.getmtime(config_path)

def reload_config():
    global config, config_last_modified
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    config_last_modified = os.path.getmtime(config_path)

@app.on_event("startup")
async def startup_event():
    reload_config()

@app.middleware("http")
async def check_config_update(request, call_next):
    global config, config_last_modified
    if os.path.getmtime(config_path) > config_last_modified:
        reload_config()
    response = await call_next(request)
    return response

# Авторизация в Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)
sheet = client.open("Student Information").sheet1

# Модель данных для преподавателя
class Teacher(BaseModel):
    name: str
    title: str

# Модель данных для запроса шаблона отчета
class LabTemplateRequest(BaseModel):
    github: Optional[str]
    name: Optional[str]
    reviewer: Optional[Teacher]

@app.get("/courses/{course_id}/staff", response_model=List[Teacher])
async def get_course_staff(course_id: int):
    try:
        staff = config['course']['staff']
        return staff
    except KeyError:
        raise HTTPException(status_code=404, detail="Course not found")

@app.post("/courses/{course_id}/groups/{group_id}/labs/{lab_id}/template")
async def get_lab_template(
    request: LabTemplateRequest,
    course_id: int = Path(..., description="ID курса"),
    group_id: int = Path(..., description="ID группы"),
    lab_id: int = Path(..., description="ID лабораторной работы"),
    format: str = Query(..., description="Формат шаблона отчета", choices=["odf"])
):
    if request.github:
        student = sheet.find(request.github)
    elif request.name:
        student = sheet.find(request.name)
    else:
        raise HTTPException(status_code=400, detail="Either GitHub username or name must be provided")

    if student and request.name and request.github:
        student_github = sheet.cell(student.row, 34).value
        student_name = sheet.cell(student.row, 2).value
        if student_github != request.github or student_name != request.name:
            raise HTTPException(status_code=400, detail="GitHub username and name do not match")

    file_name = f"{' '.join(request.name.split())}_{group_id}_{lab_id}.odt"
    template_content = generate_lab_template(
        course_id=course_id,
        lab_id=lab_id,
        group_number=group_id,
        full_name=request.name.split(),
        reviewer_name=request.reviewer.name if request.reviewer else "",
        reviewer_title=request.reviewer.title if request.reviewer else ""
    )

    # Сохранение файла и возврат файла в ответе
    #with open(file_name, 'wb') as f:
    #    f.write(template_content)
    return {"download_link": f"/download/{file_name}"}
    #return FileResponse(path=file_name, filename=file_name, media_type='application/vnd.oasis.opendocument.text')
