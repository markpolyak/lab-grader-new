import gspread

from google.oauth2.service_account import Credentials
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from message import JSON_message
from for_yaml import *
from verification_functions import *

#область работы то, с чем мы работаем
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

#чтение файла конфигурации

#открытие таблицу по ID
def get_access_to_table(id_table: str) :
    needy_sheet = client.open_by_key(id_table)

    return needy_sheet



app = FastAPI()

# get list of groups
@app.get("/courses/{course_id}/groups")
async def get_list_of_groups(course_id: int):
    if not is_course_real(course_id):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                # "message": f"Дисциплина не найдена в списке."
                "message": JSON_message[0]
            }
        )

    # open needy sheet
    config_course = open_yaml_file(course_id-1)
    needy_sheet = get_access_to_table(config_course['course']['google']['spreadsheet'])

    # get list of groups
    group_lists = needy_sheet.worksheets()
    groups = [ws.title for ws in group_lists]

    not_need = config_course['course']['google']['info-sheet']

    if not_need in groups:
        groups.remove(not_need)

    return groups


# get student list of group
@app.get("/courses/{course_id}/{group}/students")
async def get_group_students(course_id: int,
                             group: str):
    try:
        if not is_course_real(course_id):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    # "message": f"Дисциплина не найдена в списке."
                    "message": JSON_message[0]
                }
            )

        # open needy sheet
        config_course = open_yaml_file(course_id - 1)
        needy_sheet = get_access_to_table(config_course['course']['google']['spreadsheet'])

        worksheet_group = needy_sheet.worksheet(group)
        stud_col = config_course['course']['google']['student-name-column']

        all_values = worksheet_group.col_values(stud_col + 1)
        print(all_values)
        student_index = all_values.index("Ф.И.О.") + 1

        students = all_values[student_index:]

        return students

    except gspread.exceptions.WorksheetNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": JSON_message[1]
            }
        )


@app.post("/courses/{course_id}/groups/{group_id}/register")
async def add_github_nickname(
        course_id: int,
        group_id: str,
        telegram: str,
        github: str,
        surname: str,
        name: str,
        patronymic: str = "",
):
    try:

        if is_keys_empty(surname, name, patronymic, telegram, github) :
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": JSON_message[2]
                }
            )

        if is_keys_valid(surname, name, patronymic, telegram, github) :
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": JSON_message[3]
                }
            )

        student = ""
        if patronymic == "":
            student = f"{surname} {name}"
        else:
            student = f"{surname} {name} {patronymic}"

        if not is_course_real(course_id):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    # "message": f"Дисциплина не найдена в списке."
                    "message": JSON_message[0]
                }
            )

        config_course = open_yaml_file(course_id - 1)
        needy_sheet = get_access_to_table(config_course['course']['google']['spreadsheet'])

        worksheet_group = needy_sheet.worksheet(group_id)#если вкладка не существует, то исключение WorksheetNotFound
        col = config_course['course']['google']['student-name-column'] + 1

        student_coord = worksheet_group.find(student, in_column=col)
        print(student_coord)

        if student_coord is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": JSON_message[4]
                }
            )

        if not is_git_profile_exists(github):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": JSON_message[5]
                }
            )

        telegram_coord = worksheet_group.find("Telegram")#Telegram column exists?
        github_coord = worksheet_group.find("GitHub")#если столбца не существует, то исключение CellNotFound

        telegram_col = telegram_coord.col
        github_col = github_coord.col
        student_row = student_coord.row

        github_cell = worksheet_group.cell(student_row, github_col)
        telegram_cell = worksheet_group.cell(student_row, telegram_col)

        if telegram_cell.value is None:
                worksheet_group.update_cell(student_row, telegram_col, telegram)

        github_val = github_cell.value

        if github_val is None:
            worksheet_group.update_cell(student_row, github_col, github)
        elif github_val == github :
            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={
                    "message": JSON_message[6]
                }
            )
        else:
            return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "message": JSON_message[7]
                    }
                )

        return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": JSON_message[8]
                }
            )

    except gspread.exceptions.WorksheetNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": JSON_message[9]
            }
        )
    except gspread.exceptions.CellNotFound as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": JSON_message[10]
            }
        )



