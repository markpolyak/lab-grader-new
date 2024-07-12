from docx import Document
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import logging

from app.config_loader import load_all_configs, load_config
from app.google_sheets import find_student

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

courses = load_all_configs("courses")
creds_file = "credentials.json"  # Путь к файлу с учетными данными Service Account


@app.get("/courses/{course_id}/staff")
def get_course_staff(course_id: str):
    try:
        course = next((course for course in courses if course["id"] == course_id), None)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        config = load_config(os.path.join("courses", course["config"]))
        return config.course.staff
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching course staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class Reviewer(BaseModel):
    name: str = ""
    title: str = ""


class ReportRequest(BaseModel):
    github: Optional[str] = None
    name: Optional[str] = None
    reviewer: Optional[Reviewer] = Reviewer()


@app.post("/courses/{course_id}/groups/{group_id}/labs/{lab_id}/template")
async def get_lab_template(course_id: str, group_id: str, lab_id: str, format: str, report_request: ReportRequest):
    logger.info(f"Received request: {report_request}")
    if format not in ["docx", "odf", "latex"]:
        raise HTTPException(status_code=400, detail="Invalid format")

    course = next((course for course in courses if course["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    config = load_config(os.path.join("courses", course["config"]))

    student = None
    if report_request:
        student = find_student(config.course.google['spreadsheet'], group_id, creds_file, github=report_request.github, name=report_request.name)
        if isinstance(student, dict) and "error" in student:
            return JSONResponse(status_code=400, content={"message": student["error"]})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    template_path = generate_template(config, lab_id, format, student, report_request.reviewer, group_id)
    return FileResponse(template_path, media_type='application/octet-stream', filename=os.path.basename(template_path))


def generate_template(config, lab_id, format, student, reviewer, group_id):
    if format == 'docx':
        # Загрузка шаблона документа
        template_path = "templates/title_page.docx"
        document = Document(template_path)

        # Функция для преобразования полного имени в инициалы
        def get_initials(full_name):
            parts = full_name.split()
            initials = ' '.join([p[0] + '.' for p in parts[1:]])
            return f"{initials} {parts[0]}"

        # Определение замены меток
        replacements = {
            '*academic_position*': reviewer.title,
            '*teacher_name*': get_initials(reviewer.name),
            '*lab_number*': "№" + lab_id,
            '*course name*': config.course.alt_names[1],
            '*student group number*': group_id,
            '*initials*': get_initials(student.get('Ф.И.О.', '')),
            '*year*': config.course.semester.split()[1]
        }

        # Функция для замены текста в параграфах
        def replace_text_in_paragraph(paragraph, replacements):
            for key, value in replacements.items():
                if key in paragraph.text:
                    print(f"Found {key} in paragraph: {paragraph.text}")
                    paragraph.text = paragraph.text.replace(key, value)
                    print(f"Replaced {key} with {value} in paragraph")

        # Функция для замены текста в таблицах
        def replace_text_in_table(table, replacements):
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_text_in_paragraph(paragraph, replacements)

        # Обход всех параграфов в документе
        for paragraph in document.paragraphs:
            replace_text_in_paragraph(paragraph, replacements)

        # Обход всех таблиц в документе
        for table in document.tables:
            replace_text_in_table(table, replacements)

        # Добавление заголовков для лабораторной работы
        document.add_page_break()
        for heading in config.course.labs[lab_id].report:
            document.add_heading(heading + ":" + "\n", level=1)

        # Сохранение нового документа
        file_extension = 'docx'
        filename = f"lab_report_{student['GitHub']}_{lab_id}.{file_extension}"
        filepath = os.path.join("templates", filename)
        document.save(filepath)
    else:
        # Обработка форматов odf и latex если это необходимо
        raise HTTPException(status_code=400, detail="Unsupported format")

    return filepath


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
