from fastapi import FastAPI, HTTPException

from os import listdir
from os.path import isfile, join

import requests
import datetime
import pytz

from config_handler import ConfigHandler
from spreadsheet import SpreadsheetHandler

def get_course_filenames(location: str) -> list:
    names = [filename for filename in listdir(location) if isfile(join(location, filename))]
    return names

def get_course_filepaths(location: str) -> list:
    names = get_course_filenames(location)
    return [join(location, filename) for filename in names]


def get_courses() -> list:
    config = ConfigHandler("config.yaml")
    location = config.get("courses.config.location")
    result = []
    descriptors = get_course_filepaths(location)
    for i in range(len(descriptors)):
        config = ConfigHandler(descriptors[i])
        result.append({
            "id" : i + 1,
            "name" : config.get("course.name"),
            "semester" : config.get("course.semester"),
        })
    return result

def get_course_config(course_id: int) -> ConfigHandler:
    config = ConfigHandler("config.yaml")
    location = config.get("courses.config.location")
    names = get_course_filenames(location)
    if not(1 <= course_id <= len(names)):
        raise HTTPException(status_code=404, detail="Не найдены данные курса")
    filepath = join(location, names[course_id - 1])
    config = ConfigHandler(filepath)
    return config

def get_course_details_data(course_id: int) -> dict:
    config = get_course_config(course_id)
    return {
        "id" : course_id,
        "config" : config.get_name(),
        "name"  : config.get("course.name"),
        "semester" : config.get("course.semester"),
        "email" : config.get("course.email"),
        "github-organization" : config.get("course.github.organization"),
        "google-spreadsheet": config.get("course.google.spreadsheet")
    }

def get_course_groups(course_id : int):
    config = get_course_config(course_id)
    spreadsheet = SpreadsheetHandler(config.get("course.google.spreadsheet"))
    info_sheet = config.get("course.google.info-sheet")
    names = spreadsheet.get_sheet_names()
    names = [name for name in names if name != info_sheet]
    return names

def check_group(course_id: int, group_name: str):
    if group_name not in get_course_groups(course_id):
        raise HTTPException(status_code=404, detail="Не найдена группа")


def get_labs_short_names(course_id: int, group_name: str):
    config = get_course_config(course_id)
    labs = config.get("course.labs")
    short_names = [value.get('short-name') for key, value in labs.items()]
    check_group(course_id, group_name)

    spreadsheet = SpreadsheetHandler(config.get("course.google.spreadsheet"))
    table_labs = set(spreadsheet.get_range(group_name, "2:2")[0])
    short_names = [item for item in short_names if item in table_labs]
    return short_names

def get_id_by_shortname(course_id: int, name: str):
    config = get_course_config(course_id)
    labs = config.get("course.labs")
    for key, value in labs.items():
        if value.get('short-name') == name:
            return key
    raise HTTPException(status_code=404, detail="Не найдена лабораторная работа")

def check_github_user(username: str):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False

def assign_github_login(course_id: int, group_name: str, student_name: str, github_login : str):
    check_group(course_id, group_name)
    config = get_course_config(course_id)
    spreadsheet = SpreadsheetHandler(config.get("course.google.spreadsheet"))
    github_column_index_str = spreadsheet.number_to_column_letter(spreadsheet.find_column_id(group_name, "GitHub"))
    student_row_id_str = str(spreadsheet.number_to_row_id(spreadsheet.find_student_row_id(group_name, int(config.get("course.google.student-name-column")), student_name)))
    request_range = github_column_index_str + student_row_id_str
    if check_github_user(github_login):
        old = spreadsheet.get_range(group_name, request_range)
        if not old:
            spreadsheet.print_range(group_name, request_range, [[github_login]])
        elif old[0] == github_login:
            return None
        else:
            raise HTTPException(status_code=422, detail="Аккаунт GitHub уже был указан ранее. Для изменения аккаунта обратитесь к преподавателю")
    else:
        raise HTTPException(status_code=404, detail="Пользователь GitHub не найден")
    return 0

def get_github_headers():
    config = ConfigHandler("config.yaml")
    token = config.get("github.token")
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    return headers

def get_repo_workflows(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows'
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    return response.json()


def get_workflow_runs(org_name, repo, workflow_id):
    url = f'https://api.github.com/repos/{org_name}/{repo}/actions/workflows/{workflow_id}/runs'
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    return response.json()


def test_grade_lab(course_id: int, group_name: str, lab_id: str, github_target: str):
    config = get_course_config(course_id)
    org_name = config.get("course.github.organization")
    lab_config_id = get_id_by_shortname(course_id, lab_id)
    repo_prefix = config.get("course.labs." + lab_config_id + ".github-prefix")
    repo_name = repo_prefix + "-" + github_target
    print(repo_name)
    print(org_name)
    # required workflows
    required_workflows = config.get("course.labs." + lab_config_id + ".ci.workflows")
    if required_workflows == None:
        required_workflows = ["run-autograding-tests", "test", "build", "Autograding"]

    

    headers = get_github_headers() 
    url = f'https://api.github.com/orgs/{org_name}/repos'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    workflows = get_repo_workflows(org_name, repo_name)
    runs = get_workflow_runs(org_name, repo_name, 91170686)
    # print(runs
    return response.json()
    

def get_default_branch(org_name, repo):
    url = f'https://api.github.com/repos/{org_name}/{repo}'
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    repo_info = response.json()
    return repo_info['default_branch']

def get_commit_check_runs(org_name, repo, commit_sha):
    url = f'https://api.github.com/repos/{org_name}/{repo}/commits/{commit_sha}/check-runs'
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    return response.json()

def check_required_jobs(check_runs, required_jobs):
    completed_jobs = {check['name'] for check in check_runs['check_runs']}
    missing_jobs = [job for job in required_jobs if job not in completed_jobs]
    if missing_jobs:
        raise ValueError(f'Пройдены не все обязательные тесты: {", ".join(missing_jobs)}')

def get_latest_completion_time(check_runs):
    latest_time = datetime.datetime.min.replace(tzinfo=pytz.utc)
    for check in check_runs['check_runs']:
        if check['status'] == 'completed' and check['conclusion'] == 'success':
            completed_at = datetime.datetime.fromisoformat(check['completed_at'].replace('Z', '+00:00'))
            if completed_at > latest_time:
                latest_time = completed_at
    return latest_time

def calculate_penalty(latest_completion_time, deadline_date_str, penalty_max, tz):
    deadline_date = datetime.datetime.strptime(deadline_date_str, '%d.%m.%Y')
    if not deadline_date.tzinfo:
        deadline_date = deadline_date.replace(hour=23, minute=59, second=59, tzinfo=tz)
    
    if latest_completion_time <= deadline_date:
        return 0

    days_late = (latest_completion_time - deadline_date).days
    penalty_points = days_late // 7
    penalty_points = min(penalty_points, penalty_max)
    return penalty_points

def grade_lab(course_id, group_name, lab_id, github_target):
    config = get_course_config(course_id)  
    org_name = config.get("course.github.organization")
    lab_config_id = get_id_by_shortname(course_id, lab_id)
    repo_prefix = config.get(f"course.labs.{lab_config_id}.github-prefix")
    repo_name = f"{repo_prefix}-{github_target}"
    required_workflows = config.get(f"course.labs.{lab_config_id}.ci.workflows")
    if required_workflows is None:
        required_workflows = ["run-autograding-tests", "test", "build", "Autograding"]

    penalty_max = config.get(f"course.labs.{lab_config_id}.penalty-max")  

    spreadsheet = SpreadsheetHandler(config.get("course.google.spreadsheet"))
    deadline_date_str = spreadsheet.get_lab_deadline(group_name, lab_id)
    tz = pytz.timezone(config.get("course.timezone"))  

    default_branch = get_default_branch(org_name, repo_name)
    
    # Получение последнего коммита в ветке по умолчанию
    commits_url = f'https://api.github.com/repos/{org_name}/{repo_name}/commits/{default_branch}'
    commits_response = requests.get(commits_url, headers=get_github_headers())
    commits_response.raise_for_status()
    latest_commit_sha = commits_response.json()['sha']

    # Получение информации о проверках (джобах) последнего коммита
    check_runs = get_commit_check_runs(org_name, repo_name, latest_commit_sha)
    check_required_jobs(check_runs, required_workflows)
    latest_completion_time = get_latest_completion_time(check_runs)
    penalty_points = calculate_penalty(latest_completion_time, deadline_date_str, penalty_max, tz)

    mark = "vv"
    if penalty_points != 0:
        mark = mark + "-" + str(penalty_points)
    spreadsheet.print_mark(group_name, lab_id, github_target, mark)
    return {"message": f"Штрафные баллы: {penalty_points}"}
    


# print(grade_lab(1, "4132", "ЛР1", "CMPEQ0"))





    

    