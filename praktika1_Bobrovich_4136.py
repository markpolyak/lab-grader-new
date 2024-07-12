from fastapi import FastAPI, HTTPException, Path, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
import yaml
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from starlette.responses import FileResponse
from datetime import datetime
from odf.opendocument import OpenDocumentText
from odf.text import P, Span
from odf.style import Style, TextProperties, ParagraphProperties

def format_name(name_parts):
    if len(name_parts) == 3:
        return f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."
    return " ".join(name_parts)

app = FastAPI()

# Загрузка конфигурационного файла
config_path = 'C:/Users/User/AppData/Local/Programs/Python/Python310/operating-systems-2024.yaml'

if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Проверка наличия ключа 'labs' внутри 'course'
if 'course' in config and 'labs' in config['course']:
    labs = config['course']['labs']
else:
    raise KeyError("Key 'labs' not found in configuration file")

# Авторизация в Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/User/AppData/Local/Programs/Python/Python310/credentials.json', scope)
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
        student_github = sheet.cell(student.row, 2).value
        student_name = sheet.cell(student.row, 3).value
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
    with open(file_name, 'wb') as f:
        f.write(template_content)

    return FileResponse(path=file_name, filename=file_name, media_type='application/vnd.oasis.opendocument.text')

def generate_lab_template(course_id: int, lab_id: int, group_number: int, full_name: List[str], reviewer_name: str, reviewer_title: str) -> bytes:
    document = OpenDocumentText()

    # Создание стилей
    title_style = Style(name="Title", family="paragraph")
    title_style.addElement(TextProperties(attributes={"fontsize": "12pt", "fontname": "Times New Roman"}))
    title_style.addElement(ParagraphProperties(attributes={"textalign": "center"}))
    document.styles.addElement(title_style)

    o_style = Style(name="O", family="paragraph")
    o_style.addElement(TextProperties(attributes={"fontsize": "14pt", "fontname": "Times New Roman"}))
    o_style.addElement(ParagraphProperties(attributes={"textalign": "center"}))
    document.styles.addElement(o_style)
    
    text_style = Style(name="Text", family="paragraph")
    text_style.addElement(TextProperties(attributes={"fontsize": "12pt", "fontname": "Times New Roman"}))
    text_style.addElement(ParagraphProperties(attributes={"textalign": "left"}))
    document.styles.addElement(text_style)

    u_style = Style(name="Text", family="paragraph")
    u_style.addElement(TextProperties(attributes={"fontsize": "14pt", "fontname": "Times New Roman"}))
    u_style.addElement(ParagraphProperties(attributes={"textalign": "left"}))
    document.styles.addElement(u_style)

    # Добавление текста с определенным шрифтом, размером и ориентацией
    title_paragraph1 = P(stylename=title_style, text="МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ федеральное государственное автономное образовательное учреждение высшего образования САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ")
    document.text.addElement(title_paragraph1)

    # Добавление пустого пространства
    empty_paragraph = P(stylename=title_style, text=" ")
    document.text.addElement(empty_paragraph)

    title_paragraph1_4 = P(stylename=title_style, text="КАФЕДРА №  43")
    document.text.addElement(title_paragraph1_4)

    title_paragraph2 = P(stylename=text_style, text="ОТЧЁТ")
    document.text.addElement(title_paragraph2)
    title_paragraph2_2 = P(stylename=text_style, text="ЗАЩИЩЁН С ОЦЕНКОЙ")
    document.text.addElement(title_paragraph2_2)
    title_paragraph2_3 = P(stylename=text_style, text=f"ПРЕПОДАВАТЕЛЬ\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0{reviewer_title}\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0{reviewer_name}")
    document.text.addElement(title_paragraph2_3)

    title_paragraph2_4 = P(stylename=title_style, text="должность, уч. Степень, звание\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0подпись, дата\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0инициалы, фамилия")
    document.text.addElement(title_paragraph2_4)
    
    title_paragraph3 = P(stylename=o_style, text=f"ОТЧЁТ О ЛАБОРАТОРНОЙ РАБОТЕ №{lab_id}")
    document.text.addElement(title_paragraph3)
    title_paragraph3_2 = P(stylename=o_style, text="по курсу: Операционные системы")
    document.text.addElement(title_paragraph3_2)

    title_paragraph4 = P(stylename=text_style, text=f"РАБОТУ ВЫПОЛНИЛ")
    document.text.addElement(title_paragraph4)
    title_paragraph4_2 = P(stylename=text_style, text=f"СТУДЕНТ ГР. \u00A0{group_number}\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0{datetime.now().strftime('%d.%m.%Y')}\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0{format_name(full_name)}")
    document.text.addElement(title_paragraph4_2)

    title_paragraph4_3 = P(stylename=title_style, text="\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0подпись, дата\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0инициалы, фамилия")
    document.text.addElement(title_paragraph4_3)

    title_paragraph5 = P(stylename=o_style, text=f"Санкт-Петербург {datetime.now().year}")
    document.text.addElement(title_paragraph5)

    lab_sections = get_lab_content(lab_id)
    if lab_sections:
        for section in lab_sections:
            section_paragraph = P(stylename=u_style, text=section)
            document.text.addElement(section_paragraph)

    file_name = f"{' '.join(full_name)}_{group_number}_{lab_id}.odt"
    document.save(file_name)
    return open(file_name, 'rb').read()

def get_lab_content(lab_id: int):
    if 'course' not in config or 'labs' not in config['course']:
        raise KeyError("Key 'labs' not found in configuration file")
    
    lab_sections = config['course']['labs'][str(lab_id)]['report']
    return lab_sections
