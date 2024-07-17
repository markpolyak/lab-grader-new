import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config_loader import (GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, LABS_SHEETS_RANGE,
                           STUDENTS_SHEETS_RANGE, HEADERS_SHEETS_RANGE, GITHUB_HEADER)

creds = None

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

if os.path.exists(GOOGLE_TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            GOOGLE_CREDENTIALS_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)

    with open(GOOGLE_TOKEN_FILE, "w") as token:
        token.write(creds.to_json())


def column_index_to_letter(index):
    """
    Конвертирует индекс столбца (начиная с 0) в буквенное обозначение (A, B, C, ..., AA, AB, ...).

    Args:
        index (int): Индекс столбца.

    Returns:
        str: Буквенное обозначение столбца.
    """
    letters = ""
    while index >= 0:
        letters = chr(index % 26 + ord('A')) + letters
        index = index // 26 - 1
    return letters


def get_course_groups(google_spreadsheet_id: str) -> list[str]:
    """
        Получает список групп курса из указанной Google таблицы.

        Args:
            google_spreadsheet_id (str): ID Google таблицы.

        Returns:
            list[str]: Список названий групп курса.
    """
    if creds is None:
        raise Exception('credentials is None')

    service = build("sheets", "v4", credentials=creds)
    spreadsheet = service.spreadsheets().get(spreadsheetId=google_spreadsheet_id).execute()

    sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]

    return sheets


def get_course_group_labs(google_spreadsheet_id: str, group: str) -> list[str]:
    """
        Получает список лабораторных работ для указанной группы из Google таблицы.

        Args:
            google_spreadsheet_id (str): ID Google таблицы.
            group (str): Название группы.

        Returns:
            list[str]: Список лабораторных работ для указанной группы.
    """
    spreadsheet_range = f"{group}!{LABS_SHEETS_RANGE}"

    return get_values_by_range(google_spreadsheet_id, spreadsheet_range)


def get_students_of_group(google_spreadsheet_id: str, group: str) -> list[str]:
    """
        Получает список студентов для указанной группы из Google таблицы.

        Args:
            google_spreadsheet_id (str): ID Google таблицы.
            group (str): Название группы.

        Returns:
            list[str]: Список студентов для указанной группы.
    """
    spreadsheet_range = f"{group}!{STUDENTS_SHEETS_RANGE}"

    values = get_values_by_range(google_spreadsheet_id, spreadsheet_range)

    return [row[0] for row in values]


def find_github_column(google_spreadsheet_id: str, group: str) -> str:
    """
        Находит столбец, содержащий заголовок GitHub, для указанной группы из Google таблицы.

        Args:
            google_spreadsheet_id (str): ID Google таблицы.
            group (str): Название группы.

        Returns:
            str: Буквенное обозначение столбца, содержащего заголовок GitHub, или None, если заголовок не найден.
    """
    spreadsheet_range = f"{group}!{HEADERS_SHEETS_RANGE}"

    headers = get_values_by_range(google_spreadsheet_id, spreadsheet_range)[0]

    try:
        index = headers.index(GITHUB_HEADER)
        return f"{column_index_to_letter(index)}"

    except ValueError:
        return None


def update_cell(google_spreadsheet_id: str, sheet: str, col: str, row: str, value: str, check_null: bool = False):
    """
        Обновляет содержимое указанной ячейки в Google таблице.

        Args:
            google_spreadsheet_id (str): ID Google таблицы.
            sheet (str): Название листа в таблице.
            col (str): Буквенное обозначение столбца (например, 'A', 'B', 'C', ...).
            row (str): Номер строки (например, '1', '2', '3', ...).
            value (str): Новое значение для ячейки.
            check_null (bool, optional): Проверять наличие пустого значения в ячейке перед обновлением. По умолчанию False.

        Raises:
            ValueError: Если указанный аккаунт GitHub уже был указан ранее для этого же студента.

        Returns:
            None
    """
    if creds is None:
        raise Exception('credentials is None')

    service = build("sheets", "v4", credentials=creds)
    cell = f"{sheet}!{col}{row}"

    if check_null:
        existing_value = service.spreadsheets().values().get(
            spreadsheetId=google_spreadsheet_id,
            range=cell
        ).execute().get("values", [[""]])[0][0]

        if existing_value == value:
            return 202

        elif existing_value is not None and existing_value != '':
            return 422

    body = {
        "range": cell,
        "values": [
            [value]
        ]
    }

    service.spreadsheets().values().update(
        spreadsheetId=google_spreadsheet_id,
        range=cell,
        valueInputOption="RAW",
        body=body
    ).execute()

    return 200


def get_values_by_range(google_spreadsheet_id: str, spreadsheet_range: str):
    """
        Получает значения из Google таблицы для указанного диапазона.

        Args:
            google_spreadsheet_id (str): ID Google таблицы.
            spreadsheet_range (str): Диапазон ячеек таблицы (например, 'Sheet1!A1:B10').

        Returns:
            list[list]: Список списков значений из указанного диапазона.
    """
    if creds is None:
        raise Exception('credentials is None')

    service = build("sheets", "v4", credentials=creds)

    spreadsheet = service.spreadsheets().values().get(
        spreadsheetId=google_spreadsheet_id,
        range=spreadsheet_range
    ).execute()

    return spreadsheet.get("values", [])
