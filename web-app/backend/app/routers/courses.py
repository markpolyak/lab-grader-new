from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
import os
import yaml
import gspread
from google.oauth2.credentials import Credentials
import httpx
from datetime import datetime, timedelta
import pytz
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import logging
from google.auth.transport.requests import Request
from urllib.parse import unquote
from backend.settings import GITHUB_TOKEN


router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)
# Области доступа для работы с Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# Директория с файлами курсов
COURSES_DIR = os.path.join(os.path.dirname(__file__), '..', 'courses')

# Класс для работы с Google Sheets API
class GoogleSheetsService:
    def __init__(self, credentials_file=None):
        self.credentials_file = credentials_file

    def get_spreadsheet_instance(self):
         # Инициализация переменной для учетных данных
        creds = None
        logging.getLogger(__name__).debug("Using a personal google user account to authenticate")
        
        # Проверка наличия файла с токенами доступа
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # Если учетные данные отсутствуют или недействительны, выполнить повторную авторизацию
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                request = Request()
                creds.refresh(request)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Сохранение учетных данных для последующего использования
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
         # Создание экземпляра службы Google Sheets
        service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
        spreadsheet = service.spreadsheets()
        return spreadsheet


google_sheets_service = GoogleSheetsService(credentials_file="E:/web-app/backend/credentials.json")

# Функция для получения списка файлов курсов
def get_course_files():
    """Returns a list of course filenames in the courses directory."""
    return [f for f in os.listdir(COURSES_DIR) if f.endswith(".yaml")]

# Функция для загрузки конфигурации курса по его ID
def load_course_config(course_id: str):
    course_files = get_course_files()
    try:
        course_idx = int(course_id) - 1
        if course_idx < 0 or course_idx >= len(course_files):
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=404, detail="Course not found")

    filename = course_files[course_idx]
    with open(os.path.join(COURSES_DIR, filename), encoding='utf-8') as file:
        return yaml.safe_load(file), filename

# Эндпоинт для получения списка всех курсов
@router.get("/", response_model=list)
async def get_courses():
    courses = []
    for idx, filename in enumerate(get_course_files()):
        with open(os.path.join(COURSES_DIR, filename),encoding='utf-8') as file:
            config = yaml.safe_load(file)
            courses.append({
                "id": str(idx + 1),
                "name": config["course"]["name"],
                "semester": config["course"]["semester"]
            })
    
    return courses

# Эндпоинт для получения информации о конкретном курсе
@router.get("/{course_id}", response_model=dict)
async def get_course(course_id: str):
    config, filename = load_course_config(course_id)
    
    return {
        "id": course_id,
        "config": filename,
        "name": config["course"]["name"],
        "semester": config["course"]["semester"],
        "email": config["course"]["email"],
        "github-organization": config["course"]["github"]["organization"],
        "google-spreadsheet": config["course"]["google"]["spreadsheet"]
    }

# Эндпоинт для получения списка групп курса
@router.get("/{course_id}/groups", response_model=list[str])
async def get_course_groups(course_id: str):
    config, _ = load_course_config(course_id)
    
    spreadsheet_id = config["course"]["google"]["spreadsheet"]
    info_sheet_name = config["course"]["google"]["info-sheet"]
    
    sheet = google_sheets_service.get_spreadsheet_instance()
    result = sheet.get(spreadsheetId=spreadsheet_id).execute()

    sheets = result.get('sheets', [])
    sheet_names = [s['properties']['title'] for s in sheets]
    # Возвращение списка групп, исключая лист с общей информацией
    groups = [name for name in sheet_names if name != info_sheet_name]

    return groups

from googleapiclient.errors import HttpError

# Эндпоинт для получения списка лабораторных работ группы курса
@router.get("/{course_id}/groups/{group_id}/labs", response_model=list[str])
async def get_course_group_labs(course_id: str, group_id: str):
    config, _ = load_course_config(course_id)
    
    spreadsheet_id = config["course"]["google"]["spreadsheet"]
    info_sheet_name = config["course"]["google"]["info-sheet"]
    group_sheet_name = group_id

    # Получение списка кратких названий лабораторных работ из конфигурации курса
    lab_keys = [lab["short-name"] for lab in config["course"]["labs"].values()]
    
    sheet = google_sheets_service.get_spreadsheet_instance()
    try:
        result = sheet.get(spreadsheetId=spreadsheet_id).execute()
    except HttpError as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving spreadsheet: {e}")

    sheets = result.get('sheets', [])
    sheet_names = [s['properties']['title'] for s in sheets]
    groups = [name for name in sheet_names if name != info_sheet_name]
    
    if group_sheet_name not in groups:
        raise HTTPException(status_code=404, detail="Group sheet not found")

    try:
        range_to_query = f"{group_sheet_name}!A1:AZ100"
        group_sheet_data = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_to_query).execute()
    except HttpError as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving sheet data: {e}")

    headers = group_sheet_data.get('values', [])[1] if len(group_sheet_data.get('values', [])) > 1 else []
    
    found_labs = [lab_key for lab_key in lab_keys if lab_key in headers]
    if not found_labs:
        raise HTTPException(status_code=404, detail="No lab columns found")
    
    return found_labs

# Модель для регистрации студента
class StudentRegistration(BaseModel):
    name: str = Field(..., min_length=1)
    surname: str = Field(..., min_length=1)
    patronymic: str = Field(default="")
    github: str = Field(..., min_length=1)
    
    @validator("patronymic")
    def validate_patronymic(cls, v):
        if v is None:
            return ""
        return v

# Эндпоинт для регистрации студента в группе курса
@router.post("/{course_id}/groups/{group_id}/register", response_model=dict)
async def register_student(course_id: str, group_id: str, registration: StudentRegistration):
    config, _ = load_course_config(course_id)
    
    spreadsheet_id = config["course"]["google"]["spreadsheet"]
    student_name_column_index = int(config["course"]["google"]["student-name-column"])
    info_sheet_name = config["course"]["google"]["info-sheet"]
    group_sheet_name = group_id
    
    sheet = google_sheets_service.get_spreadsheet_instance()
    range_to_query = f"{group_sheet_name}!A1:AZ100"
    try:
        worksheet_data = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_to_query).execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Group sheet not found: {str(e)}")
    
    values = worksheet_data.get('values', [])
    if not values:
        raise HTTPException(status_code=404, detail="Group sheet is empty")
    
    headers = values[0]

    if student_name_column_index >= len(headers):
        raise HTTPException(status_code=500, detail=f"Student name column index '{student_name_column_index + 1}' is out of range for sheet headers: {headers}")
    
    # Проверка существования студента
    full_name = f"{registration.surname} {registration.name} {registration.patronymic}".strip()
    
    # Поиск строки с именем студента
    student_row = None
    for idx, row in enumerate(values, start=1):
        if len(row) > student_name_column_index and row[student_name_column_index] == full_name:
            student_row = idx
            break
    
    if student_row is None:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    # Проверка существования пользователя GitHub
    github_api_url = f"https://api.github.com/users/{registration.github}"
    async with httpx.AsyncClient() as client:
        github_response = await client.get(github_api_url)
        if (github_response.status_code != 200):
            raise HTTPException(status_code=404, detail="Пользователь GitHub не найден")
    
    # Check and update GitHub username in the Google Sheet
    try:
        github_column_index = headers.index("GitHub")
    except ValueError:
        raise HTTPException(status_code=500, detail="GitHub столбец не найден")
    
    
    # Check if the student row has enough columns, and extend if necessary
    while len(values[student_row - 1]) <= github_column_index:
        values[student_row - 1].append('')
    
    current_github_username = values[student_row - 1][github_column_index]
    
    if current_github_username:
        if current_github_username == registration.github:
            return {"message": "Этот аккаунт GitHub уже был указан ранее для этого же студента. Для изменения аккаунта обратитесь к преподавателю"} 
        else:
            raise HTTPException(status_code=500, detail="Для студента был указан другой аккаунт GitHub. Для изменения аккаунта обратитесь к преподавателю")
    
    values[student_row - 1][github_column_index] = registration.github
    body = {
        'values': values
    }
    
    sheet.values().update(
        spreadsheetId=spreadsheet_id,
        range=range_to_query,
        valueInputOption='RAW',
        body=body
    ).execute()
    
    return {"message": "Аккаунт GitHub успешно задан"}



class GradeRequest(BaseModel):
    github: str = Field(..., description="GitHub username of the student")

@router.post("/{course_id}/groups/{group_id}/labs/{lab_id}/grade")
async def grade_lab(course_id: str, group_id: str, lab_id: str, request: GradeRequest):
    # Декодирование URL-параметров
    course_id = unquote(course_id)
    group_id = unquote(group_id)
    lab_id = unquote(lab_id)
    config, _ = load_course_config(course_id)
    spreadsheet_id = config["course"]["google"]["spreadsheet"]
    student_name_column_index = int(config["course"]["google"]["student-name-column"])
    group_sheet_name = group_id
    
    sheet = google_sheets_service.get_spreadsheet_instance()
    range_to_query = f"{group_sheet_name}!A1:AZ100"
    try:
        worksheet_data = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_to_query).execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Группа не найдена: {str(e)}")
    
    values = worksheet_data.get('values', [])

    if not values or len(values) < 2:
        raise HTTPException(status_code=404, detail="В Google Sheet обнаружено недостаточно данных")

    # Поиск индекса колонки GitHub
    github_column_idx = -1
    header_row_github = values[0]
    for idx, cell in enumerate(header_row_github):
        if cell == 'GitHub':
            github_column_idx = idx
            break

    if github_column_idx == -1:
        raise HTTPException(status_code=500, detail="Столбец GitHub не найден")

    # Поиск индекса столбца лабораторной работы
    lab_column_idx = -1
    header_row_lab = values[1]
    for idx, cell in enumerate(header_row_lab):
        if lab_id in cell:
            lab_column_idx = idx
            break

    if lab_column_idx == -1:
        raise HTTPException(status_code=404, detail="Столбец Lab ID не найден")

    github_username = request.github
    student_row_idx = -1
    
    try:
        for idx, row in enumerate(values[2:], start=2):
            if row[github_column_idx] == github_username:
                student_row_idx = idx
                break
    except Exception as e:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")

    if student_row_idx == -1:
        raise HTTPException(status_code=404, detail="Имя пользователя GitHub не найдено")

    lab_grade_cell = values[student_row_idx][lab_column_idx]
    if lab_grade_cell and not lab_grade_cell.startswith('?'):
        return {"message": "Лабораторная работа уже оценена. Обратитесь к преподавателю для повторной оценки."}

    lab_config = None
    for lab_info in config["course"]['labs'].values():
        if lab_info['short-name'] == lab_id:
            lab_config = lab_info
            break

    if not lab_config:
        raise HTTPException(status_code=404, detail="Конфигурация Лабораторной работы не найдена")

    github_org = config['course']['github']['organization']
    repo_prefix = lab_config['github-prefix']
    repo_name = f"{github_org}/{repo_prefix}-{github_username}"

    async with httpx.AsyncClient() as client:
        headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        
        }
        # Get repository information
        repo_url = f"https://api.github.com/repos/{repo_name}"
        repo_response = await client.get(repo_url, headers=headers)

        if repo_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Репозиторий GitHub не найден")

        branch_url = f"https://api.github.com/repos/{repo_name}/branches"
        

        branches_response = await client.get(branch_url, headers=headers)
        branches = branches_response.json()
        
        default_branch = next(branch for branch in branches if branch['name'] == 'main' or branch['name'] == 'master')['name']
        
        checks_url = f"https://api.github.com/repos/{repo_name}/commits/{default_branch}/check-runs"
        checks_response = await client.get(checks_url, headers=headers)
        checks = checks_response.json()

        ci_value = lab_config.get('ci')

        # Проверяем тип значения 'ci' (должен быть словарем)
        if isinstance(ci_value, dict) and 'workflows' in ci_value:
            # Используем workflows из 'ci'
            required_jobs = ci_value['workflows']
        else:
            # Используем значение по умолчанию
            required_jobs = ['run-autograding-tests', 'test', 'build', 'Autograding']

        

        completed_jobs = [check for check in checks['check_runs'] if check['conclusion'] == 'success']
        
        
        if len(completed_jobs) < len(required_jobs):
            raise HTTPException(status_code=400, detail="Не все необходимые тесты пройдены")

        latest_job_time = max(datetime.strptime(job['completed_at'], "%Y-%m-%dT%H:%M:%SZ") for job in completed_jobs)
        timezone = pytz.timezone(config['course']['timezone'])
        latest_job_time = timezone.localize(latest_job_time)

        deadline_str = values[0][lab_column_idx]
        deadline = datetime.strptime(deadline_str, "%d.%m.%Y")
        timezone = pytz.timezone(config['course']['timezone'])
        deadline = timezone.localize(deadline + timedelta(hours=23, minutes=59, seconds=59))

        penalty_max = lab_config['penalty-max']
        overdue_days = (latest_job_time - deadline).days + 1
        penalty = max(0, (overdue_days // 7))
        penalty = min(penalty, penalty_max)
        final_grade = None
        if 'taskid-max' not in lab_config:
            penalty_str = f"-{penalty}" if penalty else ""
            final_grade = f"v{penalty_str}"
        else:
            task_id_column = config['course']['google']['task-id-column']
            task_id = values[student_row_idx][task_id_column]
        
            task_id_shift = lab_config.get('taskid-shift', 0)
            task_id_max = lab_config['taskid-max']
            expected_task_id = (int(task_id) + task_id_shift) % task_id_max
        
            job_logs = []
            for job in completed_jobs:
                logs_url = job.get('output', {}).get('annotations_url')
                if logs_url:
                    logs_response = await client.get(logs_url, headers=headers)
                    job_logs.append(logs_response.text)
                else:
                    job_logs.append("Logs URL not available")


            found_task_ids = []

            for log in job_logs:
                task_id_match = re.findall(r"^TASKID is (\d+)$", log, re.MULTILINE)
                if task_id_match:
                    found_task_ids.extend([int(number) for number in task_id_match])

            # Проверка на наличие более одного найденного значения TASKID
            if len(found_task_ids) > 1:
                # Проверка, что все найденные значения равны между собой
                if not all(task_id == found_task_ids[0] for task_id in found_task_ids):
                    # Возвращаем ошибку HTTP 400
                    raise HTTPException(status_code=400, detail={
                    "message": "Подозрение на несанкционированное внесение изменений в тесты в связи с несоответствием варианта задания. Верните тесты в исходное состояние или обратитесь к преподавателю"
                    })

            if found_task_ids and any(task_id != expected_task_id for task_id in found_task_ids):
                sheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{group_id}!{chr(65 + lab_column_idx)}{student_row_idx + 1}",
                    body={"values": [["?! Wrong TASKID!"]]},
                    valueInputOption="RAW"
                ).execute()
                raise HTTPException(status_code=400, detail="Выполнен неверный task ID, лаборатория не принята")

            grade_reduction_match = re.findall(r"^Grading reduced by (\d+)%$", log, re.MULTILINE)
            grade_reduction = max(map(int, grade_reduction_match)) / 100 if grade_reduction_match else 0

            multiplier = f"*{grade_reduction}" if grade_reduction else ""
            penalty_str = f"-{penalty}" if penalty else ""
        
            final_grade = f"v{multiplier}{penalty_str}"

        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{group_id}!{chr(65 + lab_column_idx)}{student_row_idx + 1}",
            body={"values": [[final_grade]]},
            valueInputOption="RAW"
        ).execute()
        
        return {"message": "Лабораторная работа оценена успешно"}


