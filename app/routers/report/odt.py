from fastapi import UploadFile, File, Form, HTTPException
from odf.opendocument import load
from odf.text import P
from odf import text, draw
from xml.etree import ElementTree as ET

from typing import Annotated
import os
import re

from globals import config
from globals import read_config
from globals import parse_student_info
from globals import fix_full_name
from globals import transform_name_format

from globals import extract_digits
from globals import fix_full_name
from globals import all_names_varians

def read_odt(file_path):
    document = OpenDocumentText(file_path)
    paragraphs = []

    for element in document.getElementsByType(P):
        paragraphs.append(element.firstChild.data)

    return paragraphs

async def odt(
    course_id: Annotated[str, Form()],
    lab_id: Annotated[str, Form()],
    student_fio: Annotated[str, Form()],
    group_number: Annotated[str, Form()],
    file: UploadFile = File(...)
):
    """
    Проверка odt файла на корректность
    """
    if not file.filename.endswith('.odt'):
        raise HTTPException(status_code=400, detail="File type not supported. Please upload an ODT file")

    ############################################################################

    try:
        lab_config = read_config(f"courses/{course_id}.yaml", lab_id)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Error reading course file: File not found")
    print(lab_config)
    reports = [s.lower() for s in lab_config["report"]]
    print(reports)

    teacher_name = lab_config['staff'][1]['name']
    teacher_name = fix_full_name(teacher_name)
    teacher_name_with_space, teacher_name_without_space = transform_name_format(teacher_name)
    teacher_title = lab_config['staff'][0]['title']
    teacher_title_no_spaces = teacher_title.replace(" ", "")

    ############################################################################

    file_path = os.path.join(config.get("reports")["path"], file.filename)

    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    doc = load(file_path)
    xml_content = doc.xml()

    # Парсим XML и извлекаем текст
    root = ET.fromstring(xml_content)
    text_elements = root.findall('.//text:p', namespaces={'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'})

    extracted_text = []
    for elem in text_elements:
        text = ''.join(elem.itertext())
        if len(text) > 0:
            extracted_text.append(text)

    title_page = []
    # Регулярное выражение для поиска "Санкт-Петербург" и года
    target_pattern = re.compile(r"Санкт-Петербург\s+\d{4}", re.IGNORECASE)

    # Ищем титульный лист
    for i, text in enumerate(extracted_text):
        if target_pattern.search(text):
            title_page = extracted_text[:i]
            title_lower_page = [s.lower() for s in extracted_text[:i]]
            extracted_lower_text = [s.lower() for s in extracted_text[:i]]
            extracted_lower_text = [s.lower() for s in extracted_text[i + 1:]]
            break
    else:
        raise HTTPException(status_code=400, detail="Failed to detect cover page")
    error_list = []

    ############################################################################

    # проверяем титульник
    student_info = parse_student_info(" ".join(title_page))
    print(student_info)

    full_extracted_name = all_names_varians(student_info["student_name"])
    print(full_extracted_name)
    full_student_name = fix_full_name(student_fio)
    print(full_student_name)

    if (extract_digits(student_info["group_number"]) != extract_digits(group_number)):
        error_list.append("Group numbers do not match")

    if (full_extracted_name != full_student_name):
        error_list.append("Student name do not match")
    # print([teacher_name, teacher_name_with_space, teacher_name_without_space])
    # print([teacher_title, teacher_title_no_spaces])
    # print(title_lower_page)
    find_flag = False
    for teacher in [teacher_name, teacher_name_with_space, teacher_name_without_space]:
        for line in title_lower_page:
            if line.find(teacher.lower()) != -1:
                find_flag = True
                break
    if not find_flag:
        error_list.append("No teacher's name")
        # break

    find_flag = False
    for title in [teacher_title, teacher_title_no_spaces]:
        for line in title_lower_page:
            if line.find(title.lower()) != -1:
                find_flag = True
                break
    if not find_flag:
        error_list.append("No teacher's title")
        # break

    # for teacher in [teacher_name, teacher_name_with_space, teacher_name_without_space]:
    #     find_flag = False
    #     for line in title_lower_page:
    #         if line.find(teacher.lower()) != -1:
    #             find_flag = True
    #             break
    #     if not find_flag:
    #         error_list.append("No student name")

    ############################################################################

    # проверяем основной отчёт (заголовки)
    for report in reports:
        find_flag = False
        for line in extracted_lower_text:
            if line.find(report) != -1:
                find_flag = True
                break
        if not find_flag:
            error_list.append("Not found in report: " + report)

    # os.remove(file.filename)

    # return {"checklist": reports, "errors": error_list, "title": title_page, "body": extracted_text}
    if len(error_list) > 0:
        raise HTTPException(status_code=400, detail=error_list)

    return {"result": "The report is correct"}
