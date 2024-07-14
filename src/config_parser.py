import yaml

def load_course_config(course_file):
    with open(course_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def get_lab_config(course_config, lab_id):
    course = course_config.get('course', None)
    if course is None:
        return None
    labs = course.get('labs', None)
    if labs is None:
        return None
    lab_key = str(lab_id)
    return labs.get(lab_key, None)


# # Отладочный вывод
# print("Course config:", course_config)
#
# lab_config = get_lab_config(course_config, 1)
# print("Lab config:", lab_config)