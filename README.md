<<<<<<< HEAD
# lab-grader-new

## Описание проекта
Генерация шаблонов отчетов по лабораторным работам (формат odf), бэкенд. 

## Содержимое проекта
- main.py - основной файл
- lab_template_generation.py - файл генерации шаблона отчёта
- credentials_1.json - пример файла аккаунта google cloud
- operating-systems-2024_1.yaml - пример конифг файла

## Дополнительно 
Ссылка на таблицу - https://docs.google.com/spreadsheets/d/1hMTpt_HIAR0WUdm-GiNItaRlGw94OqbVcKJ3X2kWwmk/edit?gid=0#gid=0

Запуск сервера - `uvicorn main:app --reload`

REST эндпоинт 1 (пример) - 'curl http://localhost:8000/courses/1/staff'
REST эндпоинт 2 (пример) - 'curl -X POST "http://localhost:8000/courses/1/groups/4136/labs/1/template?format=odf" -H "Content-Type: application/json" -d "{\"github\": \"n1\",\"name\": \"Бобрович Николай Сергеевич\",\"reviewer\": {\"name\": \"Поляк М. Д.\",\"title\": \"ст. пр.\"}}" --output report.odt'

Пример конифг файла также можно найти здесь - https://github.com/markpolyak/lab-grader-new/issues/7
=======
# lab-grader-new
>>>>>>> parent of 7d1ea43 (template_generation_odf)
