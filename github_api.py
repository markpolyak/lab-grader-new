import io
import re
import zipfile

import requests
from github import Github
from github import Auth, Repository
from config_loader import GITHUB_TOKEN
from logger import Log

auth = Auth.Token(GITHUB_TOKEN)

DEFAULT_JOBS = ["run-autograding-tests", "test", "build", "Autograding"]


def is_user_exist(username: str) -> bool:
    """
        Проверяет существование пользователя GitHub по имени пользователя.

        Args:
            username (str): Имя пользователя GitHub.

        Returns:
            bool: True, если пользователь существует, иначе False.
        """
    g = Github(auth=auth)
    try:
        user = g.get_user(username)
        g.close()
        return user is not None
    except Exception as e:
        g.close()
        raise e


def get_org_repo(org_name: str, repo_name: str) -> Repository:
    """
        Возвращает объект репозитория GitHub для указанной организации и репозитория.

        Args:
            org_name (str): Название организации GitHub.
            repo_name (str): Название репозитория GitHub.

        Returns:
            Repository: Объект репозитория GitHub, если найден, иначе None.
        """
    g = Github(auth=auth)
    try:
        org = g.get_organization(org_name)
        repo = org.get_repo(repo_name)

        g.close()
        return repo
    except Exception as e:
        Log.error(e)
        g.close()
        return None


def check_workflows_runs(repository: Repository, workflows_list: list):
    """
        Проверяет успешное выполнение последних workflow runs для указанного репозитория.

        Args:
            repository (Repository): Объект репозитория GitHub.
            workflows_list (list): Список workflow jobs для проверки (по умолчанию DEFAULT_JOBS).

        Raises:
            Exception: Если хотя бы один из workflow runs завершился неудачно.

        Returns:
            tuple: Кортеж с временами выполнения успешных workflow runs и их URL логов.
    """
    check_list = False
    if len(workflows_list) == 0:
        workflows_list = DEFAULT_JOBS
    else:
        check_list = True

    default_branch = repository.default_branch

    commits = repository.get_commits(sha=default_branch)
    latest_commit_sha = commits[0].sha

    workflow_runs = repository.get_workflow_runs(branch=default_branch)

    runs = []
    logs = []
    for workflow_run in workflow_runs:
        if workflow_run.head_sha == latest_commit_sha:
            if workflow_run.status == "completed" and workflow_run.conclusion == "success":
                runs.append(workflow_run.updated_at)
                logs.append(workflow_run.logs_url)
                if check_list and workflow_run.name in workflows_list:
                    workflows_list.remove(workflow_run.name)
            else:
                raise RuntimeError("repository has unsuccessful jobs")

    if check_list and len(workflows_list) != 0:
        raise RuntimeError(f"Обязательные workflow jobs не были выполнены: {', '.join(workflows_list)}")

    return runs, logs


def get_logs_from_url(url):
    """
        Получает содержимое логов из указанного URL.

        Args:
            url (str): URL для получения логов.

        Returns:
            str: Содержимое логов в виде строки.

        Raises:
            ValueError: Если URL имеет неверный формат.
            Exception: Если не удалось получить логи (например, неподдерживаемый тип контента или ошибка HTTP).
    """

    pattern = r'^https://api\.github\.com/repos/[^/]+/[^/]+/actions/runs/\d+/logs$'

    if not re.match(pattern, url):
        raise ValueError("Invalid URL format")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')

        if 'application/zip' in content_type:
            zip_file = io.BytesIO(response.content)
            logs_content = ""

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    with zip_ref.open(file_info) as log_file:
                        logs_content += log_file.read().decode('utf-8')

            return logs_content
        else:
            raise "Unknown content type"
    else:
        raise f"Failed to retrieve logs. Status Code: {response.status_code}"
