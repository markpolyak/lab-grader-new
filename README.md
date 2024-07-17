# lab-grader-new
## Описание
Бэкенд для сервиса проверки студенческих работ в GitHub. 

## Запуск

Необходимо настроить Google Cloud окружение для работы с Google Sheets API.
Гайд: https://developers.google.com/sheets/api/quickstart/python?hl=ru
Данные для аутентификации должны быть в файле `config.yaml/google/credentials_file`(По умолчанию 'credentials.json')
При первом запуске потребуется OAuth вход в аккаунт Google.

Также необходимо сгенерировать токен авторизации Github и вставить в [Конфиг](./config.yaml).

### Docker
`docker compose up -d` - Запуск Docker контейнера 

### Локально
1. `pip install -r ./requirements.txt` - Загрузка зависимостей
2. `uvicorn main:app --reload` - Запуск сервера

Доступ к серверу предоставляется по REST. Со всеми endpoint'ами можно ознакомиться и запустить через коллекцию [Postman](https://www.postman.com/joint-operations-operator-99149269/workspace/my-workspace/collection/28284200-44e2ad96-0a17-4dee-95f4-880fa43bf928?action=share&creator=28284200).

## Содержимое проекта
- config_loader - загрузка конфига и получение значений их него
- github_api - работа с API GitHub
- google_docs - работа с API Google Sheets
- logger - инициализация логгера
- main - главный файл с определенными эндпоинтами
- utils - файл с вспомогательными функциями