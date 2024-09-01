import logging
import time

import disnake
from disnake import MessageInteraction, ModalInteraction


class ButtonView(disnake.ui.View):
    def __init__(self, ctx, users_info):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.users_info = users_info

    @disnake.ui.button(label="Переслать данные", style=disnake.ButtonStyle.grey, custom_id="button1")
    async def button1(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_modal(StudentDataModal(self.ctx, self.users_info))

    async def on_error(self, event, *args, **kwargs):
        message = args[0]
        logging.error(message)


class StudentDataModal(disnake.ui.Modal):
    def __init__(self, ctx, users_info):
        components = [
            disnake.ui.TextInput(label='ФИО без сокращений:', placeholder='ФИО без сокращений', custom_id='full_name'),
            disnake.ui.TextInput(label='Никнейм на GitHub:', placeholder='Никнейм на GitHub',
                                 custom_id='github_nickname')
        ]

        super().__init__(title='Введите Ваши данные', components=components, custom_id='student_modal')
        self.ctx = ctx
        self.users_info = users_info

    async def callback(self, interaction: ModalInteraction, /) -> None:
        full_name = interaction.text_values['full_name']
        github_nickname = interaction.text_values['github_nickname']

        self.users_info['full_name'] = full_name
        self.users_info['github_nickname'] = github_nickname

        logging.info(f"got name {full_name}, and github nickname {github_nickname}")

        status_code, demo_response = register_student(
            self.users_info['course'],
            self.users_info['group'],
            self.users_info['full_name'],
            self.users_info['github_nickname']
        )

        if status_code not in [200, 422]:
            logging.info(f"student with name '{full_name}', '{github_nickname}' is not found")
            if status_code == 404:
                await interaction.response.send_message(
                    f" {demo_response['message']} Пожалуйста, введите данные корректно.")
                await self.ctx.send(view=ButtonView(self.ctx, self.users_info))

        else:

            embed = disnake.Embed(title='Лабораторная работа проверяется')
            await interaction.response.send_message(embed=embed, ephemeral=True)

            response = grade_lab(
                self.users_info['course'],
                self.users_info['group'],
                self.users_info['lab'],
                self.users_info['github_nickname']
            )

            embed = disnake.Embed(title=response["message"])
            await self.ctx.send(embed=embed)


class SelectTemplate(disnake.ui.Select):
    def __init__(self, custom_id, items_list, placeholder, ctx, view):
        options = [disnake.SelectOption(label=item, value=item) for item in items_list]

        super().__init__(custom_id=custom_id,
                         placeholder=placeholder,
                         options=options,
                         min_values=0,
                         max_values=1)
        self.chosen_value = None
        self.ctx = ctx
        self.bot_view = view

    async def callback(self, interaction: MessageInteraction):
        self.chosen_value = interaction.values[0]
        self.disabled = True
        self.placeholder = self.chosen_value
        logging.info(f"user has chosen '{self.chosen_value}' value")

    async def on_error(self, event, *args, **kwargs):
        message = args[0]
        logging.error(message)


def create_lr_embed(description: str):
    """
    Creates disnake embed
    :param description:
    :type description: str
    :return: embed
    :rtype: disnake.Embed
    """
    embed = disnake.Embed(color=0x2F3136)
    embed.set_author(name="Проверка лабораторной работы")
    embed.description = description
    return embed


def get_courses_info():
    """
    Get all names of courses
    :return: List of courses names
    :rtype: List[Str]
    """

    # обращение к эндпоинту GET /courses/
    status_code = 200
    if status_code != 200:
        logging.error(
            f"GET request to /courses/, пришедшее сообщение об ошибке"
        )

    response = [
        {
            "id": "1",
            "name": "Операционные системы",
            "semester": "значение поля course/semester",
        },
        {
            "id": "2",
            "name": "Основы машинного обучения",
            "semester": "значение поля course/semester",
        }
    ]

    course_list = {course["name"]: course["id"] for course in response} if response else {}

    return course_list


def get_groups_list(course_id):
    """
    Get groups that are listeners of the course
    :param course_id:
    :type course_id: id
    :return: List of groups that are listeners of the course
    :rtype: List[str]
    """

    # обращение к эндпоинту GET /courses/{course_id}/groups
    status_code = 200
    if status_code != 200:
        logging.error(
            f"GET request to /courses/course_id/groups returned {status_code}, пришедшее сообщение об ошибке"
        )

    groups_list = ["4131", "4132", "4133K", "4134K", "4136"]

    return groups_list


def get_labs_list(course_id, group):
    """
    Get lab list in course for dedicated group
    :param course_id:
    :type course_id: int
    :param group: group number
    :type group: str
    :return: list of labs short names
    :rtype: List[str]
    """
    # обращение к эндпоинту GET /courses/{course_id}/groups/{group_id}/labs
    status_code = 200
    if status_code != 200:
        logging.error(
            f"GET request to /courses/course_id/groups/group_id/labs returned {status_code}, пришедшее сообщение об ошибке"
        )

    labs_list = ["ЛР0", "ЛР0.1", "ЛР1", "ЛР2", "ЛР3", "ЛР4", "ЛР5", "ЛР6", "ЛР7"]
    return labs_list


def register_student(course_id, group_id, full_name, github):
    """
    Checks students data
    :param course_id:
    :type course_id: int
    :param group_id: group number
    :type group_id: str
    :param full_name:
    :type full_name: str
    :param github: github nickname
    :type github: str
    :return: dict
    """
    full_name_parts = full_name.strip().split()
    if len(full_name_parts) < 2:
        name, surname, patronymic = full_name_parts, "", ""
    else:
        patronymic = "" if len(full_name_parts) == 2 else full_name_parts[2]
        surname, name = full_name_parts[0], full_name_parts[1]

    request_body =  \
        {
          "name": name,
          "surname": surname,
          "patronymic": patronymic,
          "github": github
        }

    # вызов эндпоинта POST /courses/{course_id}/groups/{group_id}/register
    status_code = 200
    if status_code != 200:
        logging.error(
            f"GET request to POST /courses/course_id/groups/group_id/register, пришедшее сообщение об ошибке"
        )

    return get_test_data(request_body)


def get_test_data(request_body):
    """
    Stub for tests
    :param request_body:
    :return: test response
    :rtype: dict
    """
    test_student = \
    {
        "name": "Анастасия",
        "surname": "Ершова",
        "patronymic": "Дмитриевна",
        "github": "BloodyChain"
    }
    if request_body == test_student:
        return 200, {"message": "Студент найден!"}
    else:
        return 404, {"message": "Студент не найден!"}


def grade_lab(course_id, group_id, lab_id, github_nickname):
    """
    Request to grade lab endpoint
    :param course_id:
    :type course_id: int
    :param group_id:
    :type group_id: str
    :param lab_id:
    :type lab_id: str
    :param github_nickname:
    :type github_nickname: str
    :return: endpoint response
    :rtype: dict
    """

    request_body = {
        "github": github_nickname
    }

    # обращение к эндпоинту POST /courses/{course_id}/groups/{group_id}/labs/{lab_id}/grade
    status_code = 200
    if status_code != 200:
        logging.error(
            f"GET request to POST /courses/course_id/groups/group_id/labs/lab_id/grade, пришедшее сообщение об ошибке"
        )

    demo_response = {
        "message": "Тестовый результат работы эндпоинта grade"
    }
    return demo_response
