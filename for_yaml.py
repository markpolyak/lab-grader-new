import os
import yaml

# Указываем путь к директории, где лежат YAML файлы курсов
directory = "./courses"

# Получаем список файлов
yaml_files = os.listdir(directory)

def open_yaml_file(course_id: int):
    path_ = f"{directory}/{yaml_files[course_id]}"

    # reading a YAML file
    with open(path_, 'r', encoding="utf8") as file:
        config_course = yaml.safe_load(file)

    return config_course
