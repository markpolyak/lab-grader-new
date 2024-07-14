from fastapi import FastAPI, File, UploadFile, HTTPException, Form, status
from docx import Document
import os
import tempfile
from config_parser import load_course_config, get_lab_config
from functions import check_report_sections, check_title_page, verify_student_registration, normalize_name, normalize_full_name
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from errors import list_of_common_errors

# Инициализация приложения FastAPI
app = FastAPI()

# Загрузка учетных данных Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('src/g-sheets/parsing-428822-d0f161bcdd17.json', scope)
gc = gspread.authorize(credentials)


# Маршрут для загрузки отчета о лабораторной работе
@app.post("/courses/{course_id}/labs/{lab_id}/upload-report")
async def upload_report(course_id: str, lab_id: str, file: UploadFile = File(...), student_name: str = Form(...), group_number: str = Form(...)):

    try:
        # Загрузка конфигурации курса и лабораторной работы
        course_file = f'courses/{course_id}.yaml'
        course_config = load_course_config(course_file)
        lab_config = get_lab_config(course_config, lab_id)
    except FileNotFoundError:
            raise HTTPException(status_code=404, detail={"Ошибка": list_of_common_errors[0]})

    # Чтение содержимого загруженного файла
    contents = await file.read()

    # Временное сохранение файла на диск для обработки
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Открытие документа Word
        doc = Document(tmp_path)
        # Проверка титульной страницы
        title_errors, extracted_student_name, extracted_group_number = check_title_page(doc, course_config, lab_id)
        if title_errors:
            raise HTTPException(status_code=400, detail={"Ошибки на титульной странице": title_errors})

        # Нормализация имен для сравнения
        normalized_extracted_name = normalize_name(extracted_student_name)
        normalized_student_name = normalize_full_name(student_name)

        print(normalized_extracted_name, normalized_student_name)
        print(extracted_group_number, group_number)

        # Проверка совпадения переданного и извлеченного ФИО и номера группы
        if normalized_extracted_name != normalized_student_name:
            raise HTTPException(status_code=400, detail={"Ошибка": list_of_common_errors[1]})

        if extracted_group_number != group_number:
            raise HTTPException(status_code=400, detail={"Ошибка": list_of_common_errors[2]})

        # Проверка студента в Google Sheets
        spreadsheet_id = course_config['course']['google']['spreadsheet']
        if not verify_student_registration(spreadsheet_id, student_name, group_number):
            raise HTTPException(status_code=400, detail={"Ошибка": list_of_common_errors[3]})

        # Проверка наличия необходимых секций в отчете
        missing_sections = check_report_sections(doc, lab_config['report'])
        if missing_sections:
            raise HTTPException(status_code=400, detail={"Отсутствующие секции в отчете": missing_sections})

        # Возвращение успешного результата, если все проверки пройдены
        return {"Результат": "Отчет корректен", "Отсутствующие секции": missing_sections}
    finally:
        # Удаление временного файла
        os.remove(tmp_path)

# Запуск приложения FastAPI с помощью Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)




