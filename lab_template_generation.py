from typing import List
from odf.opendocument import OpenDocumentText
from odf.text import P
from odf.style import Style, TextProperties, ParagraphProperties
from datetime import datetime
import yaml
import os
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run()

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

def format_name(name_parts):
    if len(name_parts) == 3:
        return f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."
    return " ".join(name_parts)

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
    #return f"<a href='/download/{file_name}'>Download Lab Template</a>"
    return open(file_name, 'rb').read()

# получение разделов ЛР
def get_lab_content(lab_id: int):
    if 'course' not in config or 'labs' not in config['course']:
        raise KeyError("Key 'labs' not found in configuration file")
    
    lab_sections = config['course']['labs'][str(lab_id)]['report']
    return lab_sections
