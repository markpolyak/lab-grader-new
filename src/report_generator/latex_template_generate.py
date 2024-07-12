import yaml
import os
import gspread
from google.oauth2.service_account import Credentials
from fastapi import HTTPException, Enum
from pydantic import BaseModel, Field
from typing import Optional
from fastapi.responses import PlainTextResponse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
credentials_path = os.path.join(BASE_DIR, 'src', 'urazalin-rustam-20eab27112e8.json')

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)

client = gspread.authorize(credentials)

class FormatType(str, Enum):
    docx = "docx"
    odf = "odf"
    latex = "latex"

class Reviewer(BaseModel):
    name: str = Field(default="")
    title: str = Field(default="")

class LabRequest(BaseModel):
    github: Optional[str] = None
    name: Optional[str] = None
    reviewer: Optional[Reviewer] = None

def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def load_all_configs(folder_path):
    configs = []
    for index, file_name in enumerate(os.listdir(folder_path), start=1):
        if file_name.endswith('.yaml'):
            file_path = os.path.join(folder_path, file_name)
            config = load_config(file_path)
            config["id"] = str(index)
            configs.append(config)
    return configs

config_folder_path = os.path.join(BASE_DIR, 'courses')
configs = load_all_configs(config_folder_path)

def get_courses_course_id(course_id: str):
    staff_list = []
    for config in configs:
        if course_id == config.get("id"):
            staff_list = config.get('course', {}).get('staff', [])
            break
    return staff_list

def get_template(
        course_id: str,
        group_id: str,
        lab_id: str,
        format: str,
        request_data: LabRequest
):
    for config in configs:
        if course_id == config.get("id"):
            spreadsheet_id = config.get('course', {}).get('google', {}).get('spreadsheet')
            if not spreadsheet_id:
                raise HTTPException(status_code=404, detail="Spreadsheet не найден")

            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheets = spreadsheet.worksheets()

            worksheet = next((ws for ws in worksheets if ws.title == group_id), None)
            if not worksheet:
                raise HTTPException(status_code=404, detail="Группа не найдена")

            github_column = 34
            name_column = 2

            github_row = None
            name_row = None
            if request_data.github:
                github_cell = worksheet.find(request_data.github, in_column=github_column)
                if github_cell:
                    github_row = github_cell.row
                else:
                    raise HTTPException(status_code=400, detail={"message": "Студента с таким именем GitHub нет в таблице"})

            if request_data.name:
                name_cell = worksheet.find(request_data.name, in_column=name_column)
                if name_cell:
                    name_row = name_cell.row
                else:
                    raise HTTPException(status_code=400, detail={"message": "Студента с таким ФИО нет в таблице"})

            if github_row and name_row and github_row != name_row:
                raise HTTPException(status_code=400, detail={"message": "Несоответствие ФИО и имени пользователя на GitHub"})

            student_row = github_row or name_row
            if not student_row:
                raise HTTPException(status_code=404, detail="Студент не найден")

            alt_names = config.get('course', {}).get('alt-names', {})
            course_name = alt_names[1] if len(alt_names) > 1 else None
            second_row = worksheet.row_values(2)
            labs = config.get('course', {}).get('labs', {})

            for lab_number, lab_info in labs.items():
                if lab_id == lab_info.get('short-name') and lab_info.get('short-name') in second_row:
                    worksheet_lab_names = next((ws for ws in worksheets if ws.title == "График"), None)
                    if not worksheet_lab_names:
                        raise HTTPException(status_code=404, detail="Лист График отсутствует в гугл таблице")
                    lab_name = next((row[1].replace(lab_info.get('short-name'), '').replace('*', '').replace('.', '') for row in worksheet_lab_names.get_all_values() if row[1].startswith(lab_info.get('short-name'))), None)
                    lab_number_ = lab_number
                    report_headers = lab_info.get('report')
                    student_name = request_data.name if request_data.name else ""
                    name_parts = student_name.split()
                    if len(name_parts) == 2:
                        student_name = f"{name_parts[1][0]}. {name_parts[0]}"
                    elif len(name_parts) == 3:
                        student_name = f"{name_parts[1][0]}.{name_parts[2][0]}. {name_parts[0]}"
                    if request_data.reviewer.name:
                        name_reviewer_parts = request_data.reviewer.name.split()
                        reviewer_name = f"{name_reviewer_parts[1][0]}.{name_reviewer_parts[2][0]}. {name_reviewer_parts[0]}"
                    else:
                        reviewer_name = ""
                    reviewer_title = request_data.reviewer.title if request_data.reviewer else ""
                    if format == FormatType.latex:
                        latex_template = generate_latex_template(
                            reviewer_title=reviewer_title,
                            reviewer_name=reviewer_name,
                            lab_number_=lab_number_,
                            lab_name=lab_name,
                            course_name=course_name,
                            group_id=group_id,
                            student_name=student_name,
                            report_headers=report_headers
                        )
                        return PlainTextResponse(content=latex_template, media_type="application/x-latex")
                    elif format == FormatType.docx:
                        return {"message": f"Template for {lab_id} in DOCX format"}

                    elif format == FormatType.odf:
                        return {"message": f"Template for {lab_id} in ODF format"}
            raise HTTPException(status_code=404, detail="Лабораторная работа не найдена")
    raise HTTPException(status_code=404, detail="Неправильный id курса")

def generate_latex_template(reviewer_title, reviewer_name, lab_number_, lab_name, course_name, group_id, student_name, report_headers):
    with open(os.path.join(BASE_DIR, 'src', 'report_generator', 'template.tex'), 'r', encoding='utf-8') as file:
        latex_template = file.read()

    latex_template = latex_template.replace('%%REVIEWER_TITLE%%', reviewer_title)
    latex_template = latex_template.replace('%%REVIEWER_NAME%%', reviewer_name)
    latex_template = latex_template.replace('%%LAB_NUMBER%%', lab_number_)
    latex_template = latex_template.replace('%%LAB_NAME%%', lab_name)
    latex_template = latex_template.replace('%%COURSE_NAME%%', course_name)
    latex_template = latex_template.replace('%%GROUP_ID%%', group_id)
    latex_template = latex_template.replace('%%STUDENT_NAME%%', student_name)

    report_headers_text = '\n'.join(f'\\subsection*{{{header}}}' for header in report_headers)
    latex_template = latex_template.replace('%%REPORT_HEADERS%%', report_headers_text)

    return latex_template
