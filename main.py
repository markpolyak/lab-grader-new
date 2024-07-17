import yaml
from fastapi import FastAPI, Path, Body
from fastapi.responses import JSONResponse
from googleapiclient.errors import HttpError

import google_docs
import github_api
import utils
from config_loader import COURSES_DIR
import os
from utils import parseDateFromStr, extract_taskid, extract_grading_reduction, allValuesEqual
from logger import Log

app = FastAPI()


@app.get('/courses/', response_model=list)
def get_courses():
    courses_info = []

    if not os.path.exists(COURSES_DIR) or not os.path.isdir(COURSES_DIR):
        return []

    for filename in os.listdir(COURSES_DIR):
        file_path = os.path.join(COURSES_DIR, filename)
        if os.path.isfile(file_path) and filename.endswith('.yaml'):
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    course_config = yaml.safe_load(file)
                    course_info = {
                        'id': filename[:-5],  # Получение только название файла
                        'name': course_config.get('course', {}).get('name', ''),
                        'semester': course_config.get('course', {}).get('semester', '')
                    }
                    courses_info.append(course_info)
                except Exception as e:
                    Log.debug('get_courses reading file exception', str(e))
                    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    return courses_info


@app.get('/courses/{course_id}/', response_model=dict)
def get_course(course_id: str = Path(..., description="Course ID")):
    Log.debug(f"Endpoint /courses/{course_id}/ accessed")

    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        Log.warning(f"Course file {course_file} not found")
        return JSONResponse(status_code=404, content={"message": "Курс не найден"})

    try:
        with open(course_file, 'r', encoding='utf-8') as file:
            try:
                course_config = yaml.safe_load(file)
                course_info = {
                    'id': course_id,
                    'config': f'{course_id}.yaml',
                    'name': course_config.get('course', {}).get('name', ''),
                    'semester': course_config.get('course', {}).get('semester', ''),
                    'email': course_config.get('course', {}).get('email', ''),
                    'github-organization': course_config.get('course', {}).get('github', {}).get('organization', ''),
                    'google-spreadsheet': course_config.get('course', {}).get('google', {}).get('spreadsheet', '')
                }
                return course_info
            except Exception as e:
                Log.error(f"Error reading YAML file {course_file}: {str(e)}")
                return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    except Exception as e:
        Log.error(f"Error accessing file {course_file}: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})


@app.get('/courses/{course_id}/groups', response_model=list)
def get_course_groups(course_id: str = Path(..., description="Course ID")):
    Log.debug(f"Endpoint /courses/{course_id}/groups accessed")

    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        Log.warning(f"Course file {course_file} not found")
        return JSONResponse(status_code=404, content={"message": "Курс не найден"})

    try:
        with open(course_file, 'r', encoding='utf-8') as file:
            course_config = yaml.safe_load(file)
            google_spreadsheet_field = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')

            if not google_spreadsheet_field:
                Log.warning(f"No Google spreadsheet configured for course {course_id}")
                return JSONResponse(status_code=500,
                                    content={"message": "Google spreadsheet not configured for course"})

            groups = google_docs.get_course_groups(google_spreadsheet_field)

            info_sheet_name = course_config.get('course', {}).get('google', {}).get('info-sheet', '')

            if info_sheet_name in groups:
                groups.remove(info_sheet_name)

            return groups

    except Exception as e:
        Log.error(f"Error processing course groups for {course_id}: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})


@app.get('/courses/{course_id}/groups/{group_id}/labs', response_model=list)
def get_course_group_labs(
        course_id: str = Path(..., description="Course ID"),
        group_id: str = Path(..., description="Group ID")
):
    Log.debug(f"Endpoint /courses/{course_id}/groups/{group_id}/labs accessed")

    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        Log.warning(f"Course file {course_file} not found")
        return JSONResponse(status_code=404, content={"message": "Course not found"})

    try:
        with open(course_file, 'r', encoding='utf-8') as file:
            course_config = yaml.safe_load(file)
            google_spreadsheet = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')

            if not google_spreadsheet:
                Log.warning(f"No Google spreadsheet configured for course {course_id}")
                return JSONResponse(status_code=500,
                                    content={"message": "Google spreadsheet not configured for course"})

            lab_short_names = []

            # Извлекаем сокращенные названия лабораторных работ из конфигурационного файла
            lab_config = course_config.get('course', {}).get('labs', {})
            for lab_key in lab_config:
                short_name = lab_config[lab_key].get('short-name', '')
                if short_name:
                    lab_short_names.append(short_name)

            group_sheets_labs = google_docs.get_course_group_labs(google_spreadsheet, group_id)[1]
            group_labs = []

            for group in lab_short_names:
                if group in group_sheets_labs:
                    group_labs.append(group)

            return group_labs
    except HttpError as e:
        Log.error(f"HttpError processing labs for course {course_id}, group {group_id}: {str(e)}")
        if e.status_code == 400:
            return JSONResponse(status_code=404, content={"message": "Группа не найдена"})

        return JSONResponse(status_code=500, content={"message": "Internal server error"})

    except Exception as e:
        Log.error(f"Error processing labs for course {course_id}, group {group_id}: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})


@app.post("/courses/{course_id}/groups/{group_id}/register")
def register_student(
        data=Body(...),
        course_id: str = Path(..., description="Course ID"),
        group_id: str = Path(..., description="Group ID")
):
    Log.debug(f"Endpoint /courses/{course_id}/groups/{group_id}/register accessed")

    # Проверка наличия и длины полей
    required_fields = ["name", "surname", "github"]
    for field in required_fields:
        if field not in data or not isinstance(data[field], str) or len(data[field]) == 0:
            Log.warning(f"Validation error: Missing or invalid field '{field}' in request")
            return JSONResponse(status_code=400,
                                content={"message": f"Validation error: Missing or invalid field '{field}'"})

    # Проверка patronymic
    if "patronymic" in data and not isinstance(data["patronymic"], str):
        Log.warning("Validation error: 'patronymic' field must be a string")
        return JSONResponse(status_code=422,
                            content={"message": "Validation error: 'patronymic' field must be a string"})

    # Чтение конфига курса
    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        Log.warning(f"Course file {course_file} not found")
        return JSONResponse(status_code=404, content={"message": "Курс не найден"})

    try:
        with open(course_file, 'r', encoding='utf-8') as file:
            course_config = yaml.safe_load(file)
            google_spreadsheet = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')

            if not google_spreadsheet:
                Log.error("Google spreadsheet field not found in course configuration")
                return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    except Exception as e:
        Log.error(f"Error reading course config file {course_file}: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    try:
        groups = google_docs.get_course_groups(google_spreadsheet)
        if group_id not in groups:
            Log.warning(f"Group {group_id} not found in course {course_id}")
            return JSONResponse(status_code=404, content={"message": "Группа не найдена на курсе"})

        students = google_docs.get_students_of_group(google_spreadsheet, group_id)

    except Exception as e:
        Log.error(f"Error getting course groups: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    full_name = f"{data['surname']} {data['name']}"
    if data['patronymic']:
        full_name += f" {data['patronymic']}"

    if full_name not in students:
        Log.warning(f"Student {full_name} not found in group {group_id}")
        return JSONResponse(status_code=404, content={"message": "Студент не найден"})

    try:
        if not github_api.is_user_exist(data['github']):
            Log.warning(f"GitHub user {data['github']} not found")
            return JSONResponse(status_code=404, content={"message": "Пользователь GitHub не найден"})
    except Exception as e:
        Log.error(f"Error checking GitHub user {data['github']}: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    try:
        github_column = google_docs.find_github_column(google_spreadsheet, group_id)
        if github_column is None:
            Log.error("Error finding GitHub column in Google spreadsheet")
            return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

        student_index = students.index(full_name) + 3

        result = google_docs.update_cell(
            google_spreadsheet,
            group_id,
            github_column, str(student_index),
            data['github'],
            check_null=True
        )
        if result == 202:
            return JSONResponse(status_code=202, content={
                "message":
                    "Этот аккаунт GitHub уже был указан ранее для этого же студента. "
                    "Для изменения аккаунта обратитесь к преподавателю"
            })
        elif result == 422:
            return JSONResponse(status_code=422, content={
                "message": "Аккаунт GitHub уже был указан ранее. Для изменения аккаунта обратитесь к преподавателю"
            })

    except Exception as e:
        Log.error(f"Error updating Google spreadsheet: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    Log.info(f"GitHub account '{data['github']}' successfully assigned for {full_name}")
    return JSONResponse(status_code=200, content={"message": "Аккаунт GitHub успешно задан"})


@app.post("/courses/{course_id}/groups/{group_id}/labs/{lab_id}/grade")
def get_grade(
        data=Body(),
        course_id: str = Path(..., description="Course ID"),
        group_id: str = Path(..., description="Group ID"),
        lab_id: str = Path(..., description="Lab ID"),
):
    Log.debug(f"Starting get_grade function for course_id: {course_id}, group_id: {group_id}, lab_id: {lab_id}")

    required_fields = ["github"]
    for field in required_fields:
        if field not in data or not isinstance(data[field], str) or len(data[field]) == 0:
            return JSONResponse(status_code=422, content={"message": "Validation error"})

        # Чтение конфига курса
    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        Log.warning(f"Course file {course_file} not found")
        return JSONResponse(status_code=404, content={"message": "Курс не найден"})

    with open(course_file, 'r', encoding='utf-8') as file:
        try:
            course_config = yaml.safe_load(file)
            google_spreadsheet = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')
            organisation = course_config.get('course', {}).get('github', {}).get('organization', '')

            if not google_spreadsheet:
                return JSONResponse(status_code=500, content="")

        except Exception as e:
            Log.error(e)
            return JSONResponse(status_code=500, content="")

    try:
        groups = google_docs.get_course_groups(google_spreadsheet)
        if group_id not in groups:
            return JSONResponse(status_code=404, content={"message": "Группа не найдена"})

        github_column = google_docs.find_github_column(google_spreadsheet, group_id)
        if github_column is None:
            return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

        github_range = f"{group_id}!{github_column}1:{github_column}50"

        github_students = google_docs.get_values_by_range(google_spreadsheet, github_range)

        student_row = 1
        for i in github_students:
            if len(i) != 0 and i[0] == data["github"]:
                break
            student_row += 1

        group_sheets_labs = google_docs.get_course_group_labs(google_spreadsheet, group_id)
        labs_ids = group_sheets_labs[1]
        labs_dates = group_sheets_labs[0]

    except Exception as e:
        Log.error(e)
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    try:
        lab_index = labs_ids.index(lab_id)
    except ValueError:
        Log.error(f"Для выбранной группы {group_id} проверка лабораторной работы {lab_id} недоступна")
        return JSONResponse(status_code=403,
                            content={
                                "message": "Для выбранной группы проверка данной лабораторной работы недоступна"
                            })

    lab_deadline = parseDateFromStr(labs_dates[lab_index], course_config.get('course').get('timezone', 'UTC'))
    if lab_deadline is None:
        Log.error(f"lab_deadline validation error. date: {labs_dates[lab_index]}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    try:
        lab_column = google_docs.column_index_to_letter(lab_index + 2)

        grade_range = f"{group_id}!{lab_column}{student_row}"
        grade_value = google_docs.get_values_by_range(google_spreadsheet, grade_range)
        if len(grade_value) != 0 and grade_value[0][0][0] != "?":
            Log.error(f"Grade value {grade_value} for lab {lab_id} already exists ({data['github']})")
            return JSONResponse(
                status_code=409,
                content={"message": "Проверка лабораторной работы уже была пройдена ранее. "
                                    "Для повторной проверки обратитесь к преподавателю"}
            )
    except Exception as e:
        Log.error(e)
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    lab_config = None
    labs = course_config.get('course', {}).get('labs', {})
    for lab_key in labs:
        short_name = labs[lab_key].get('short-name', '')
        if short_name == lab_id:
            lab_config = labs[lab_key]

    if lab_config is None:
        return JSONResponse(status_code=404, content={"message": "Лабораторная не найдена"})

    lab_prefix = lab_config.get('github-prefix', '')
    repo_name = f"{lab_prefix}-{data['github']}"

    github_ogr_repo = github_api.get_org_repo(organisation, repo_name)

    if github_ogr_repo is None:
        return JSONResponse(status_code=404, content={"message": "Репозиторий GitHub не найден"})

    ci = lab_config.get('ci', {})
    if not isinstance(ci, list):
        workflow_config_list = ci.get("workflows", [])
    else:
        workflow_config_list = []

    try:
        workflows_times, logs_urls = github_api.check_workflows_runs(github_ogr_repo, workflow_config_list)
    except RuntimeError:
        return JSONResponse(status_code=400, content={"message": "Пройдены не все обязательные тесты"})
    except Exception as e:
        Log.error(e)
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    latest_job_time = max(workflows_times)

    dates_diff = (latest_job_time - lab_deadline).days
    max_penalty = lab_config.get('penalty-max')
    penalty = utils.calculatePenalty(dates_diff, max_penalty)

    logs_details = []
    for log_url in logs_urls:
        logs_details.append(github_api.get_logs_from_url(log_url))

    try:
        ign_t_id_key = 'ignore-task-id'
        check_task = True

        if ign_t_id_key in lab_config:  # ignore-task-id существует в конфиге
            flag = lab_config.get(ign_t_id_key, True)  # Дефолтное значение - True, если значения нет
            if flag or flag is None:  # Если значения нет или оно True
                check_task = False

        if check_task:
            task_ids = []
            for logs in logs_details:
                task_id = extract_taskid(logs)
                if task_id:
                    for task in task_id:
                        task_ids.append(task)

            if not allValuesEqual(task_ids):
                Log.error(f"Несоответствие номеров вариантов заданий в логах. task_ids: {task_ids} ({data['github']})")
                return JSONResponse(status_code=400, content={
                    "message": "Подозрение на несанкционированное внесение изменений в тесты в связи с несоответствием "
                               "варианта задания. Верните тесты в исходное состояние или обратитесь к преподавателю"
                })

            if len(task_ids) != 0:
                task_id_from_logs = task_ids[0]
            else:
                raise Exception("Ошибка с получением номера варианта задания")

            task_id_column = course_config.get('course', {}).get('google', {}).get('task-id-column', 0)

            task_id_range = f"{group_id}!{google_docs.column_index_to_letter(task_id_column)}{student_row}"

            task_id_value = int(google_docs.get_values_by_range(google_spreadsheet, task_id_range)[0][0])

            task_id_shift = lab_config.get('taskid-shift', 0)
            task_id_max = lab_config.get('taskid-max', -1)

            if task_id_max == -1:
                raise Exception(f"Ошибка получения task_id_max для {lab_id} ({data['github']})")

            task_id_value = (task_id_value + task_id_shift) % task_id_max

            if task_id_from_logs != task_id_value:
                Log.info(f"Wrong task id for {lab_id} of {data['github']}")
                google_docs.update_cell(
                    google_spreadsheet,
                    group_id,
                    lab_column,
                    str(student_row),
                    value="?! Wrong TASKID!",
                    check_null=False
                )

                return JSONResponse(
                    status_code=400,
                    content={"message": "Выполнен чужой вариант задания, лабораторная работа не принята"}
                )

        grading_reductions = []
        for logs in logs_details:
            for red in extract_grading_reduction(logs):
                grading_reductions.append(red)

        grading_reduced_value = 0
        if len(grading_reductions) > 0:
            if allValuesEqual(grading_reductions):
                grading_reduced_value = grading_reductions[0]
            else:
                raise Exception("Не все значения Grading reduced равны")

        reducing_coef = round(grading_reduced_value / 100, 2)
        if reducing_coef > 0:
            m_str = f"*{reducing_coef}"
        else:
            m_str = ""

        ignore_date = lab_config.get('ignore-completion-date', False)

        if not ignore_date and penalty > 0:
            p_str = f"-{penalty}"
        else:
            p_str = ""

        cell_grade_value = f"v{m_str}{p_str}"

        google_docs.update_cell(
            google_spreadsheet,
            group_id,
            lab_column,
            str(student_row),
            value=cell_grade_value,
            check_null=False
        )

    except Exception as e:
        Log.error(e)
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    return {"message": "Проверка пройдена успешно"}
