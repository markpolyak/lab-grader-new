# lab-grader-new

## Описание проекта
Генерация шаблонов отчетов по лабораторным работам (формат odf), бэкенд. 

## Содержимое проекта
- praktika1_Bobrovich_4136.py - бэкенд для проекта

## Дополнительно 
Ссылка на таблицу (пример) - https://docs.google.com/spreadsheets/d/1hMTpt_HIAR0WUdm-GiNItaRlGw94OqbVcKJ3X2kWwmk/edit?gid=0#gid=0

Запуск сервера - `uvicorn praktika1_Bobrovich_4136:app --reload`

REST эндпоинт 1 (пример) - 'curl http://localhost:8000/courses/1/staff'
REST эндпоинт 2 (пример) - 'curl -X POST "http://localhost:8000/courses/1/groups/4136/labs/1/template?format=odf" -H "Content-Type: application/json" -d "{\"github\": \"n1\",\"name\": \"Бобрович Николай Сергеевич\",\"reviewer\": {\"name\": \"Поляк М. Д.\",\"title\": \"ст. пр.\"}}" --output report.odt'

Пример конифг файла можно найти здесь - https://github.com/markpolyak/lab-grader-new/issues/7
