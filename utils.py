import re
from datetime import datetime, timezone
from dateutil.parser import parse


def parseDateFromStr(date_str: str, timezone: str) -> datetime:
    """
        Парсит строку с датой и временем в объект datetime.

        Args:
            date_str (str): Строка с датой и временем.
            timezone (str): Часовой пояс для преобразования.

        Returns:
            datetime: Объект datetime, представляющий дату и время.

        Если строка пустая или не удалось распознать дату, возвращает None.
        """
    if len(date_str) == 0:
        return None

    if len(date_str.split('.')) == 2:
        date_str += f'{datetime.now().year}'

    # add hours, minutes and seconds based on Moscow time
    date_str += ' 23:59:59 ' + timezone

    try:
        parsed_date = parse(date_str, dayfirst=True)
        return parsed_date
    except (ValueError, TypeError):
        return None


def calculatePenalty(dates_diff: int, penalty_max: int):
    """
        Вычисляет штрафные баллы на основе разницы в датах.

        Args:
            dates_diff (int): Разница в датах (в днях).
            penalty_max (int): Максимальный штраф за работу.

        Returns:
            int: Вычисленные штрафные баллы.

        Если разница в датах меньше 0, возвращает 0. Вычисляет количество недель
        разницы и ограничивает его значением penalty_max.
        """
    if dates_diff < 0:
        return 0

    penalty = dates_diff // 7
    penalty = min(penalty, penalty_max)

    return penalty


def extract_taskid(logs):
    """
        Извлекает значения TASKID из строк логов.

        Args:
            logs (str): Строки логов, в которых ищутся значения TASKID.

        Returns:
            list: Список целочисленных значений TASKID.

        Извлекает и возвращает все найденные значения TASKID из строк логов.
        """
    taskid_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z) TASKID is (\d+)'
    task_ids = []

    for line in logs.splitlines():
        match = re.match(taskid_pattern, line)
        if match:
            task_ids.append(int(match.group(2)))

    return task_ids


def extract_grading_reduction(logs):
    """
        Извлекает значения уменьшения оценки из строк логов.

        Args:
            logs (str): Строки логов, в которых ищутся значения уменьшения оценки.

        Returns:
            list: Список целочисленных значений уменьшения оценки.

        Извлекает и возвращает все найденные значения уменьшения оценки из строк логов.
        """
    grading_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z) Grading reduced by (\d+)%'
    grading_reductions = []

    for line in logs.splitlines():
        match = re.match(grading_pattern, line)
        if match:
            grading_reductions.append(int(match.group(2)))

    return grading_reductions


def allValuesEqual(values: list) -> bool:
    """
        Проверяет, все ли значения в списке равны.

        Args:
            values (list): Список значений для проверки.

        Returns:
            bool: True, если все значения в списке равны, иначе False.

        Проверяет все элементы списка на равенство друг другу.
        """
    if len(values) < 2:
        return True

    for i in range(1, len(values)):
        if values[i] != values[i - 1]:
            return False

    return True


def save_logs_to_files(logs):
    for index, log in enumerate(logs):
        try:
            file_name = f"log_{index + 1}.txt"
            with open(file_name, 'w', encoding='utf-8') as log_file:
                log_file.write(log)
            print(f"Logs saved to {file_name}")
        except (ValueError, RuntimeError) as e:
            print(f"Error processing {log}: {e}")

