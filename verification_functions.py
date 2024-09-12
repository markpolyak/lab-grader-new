import requests

# Отчество может быть пустым (""),
 # все остальные поля должны быть заданы как строки длины > 0.
def is_keys_empty(surname: str,
                  name: str,
                  patronymic: str,
                  telegram: str,
                  github: str) :
    if (len(name) < 0 or
     len(surname) < 0 or
     len(patronymic) < 0 or
     len(telegram) < 0 or
     len(github) < 0) :
        return True

    return False


def is_keys_valid(surname: str,
                  name: str,
                  patronymic: str,
                  telegram: str,
                  github: str) :
    if (name is None or
     surname is None or
     patronymic is None or
     telegram is None or
     github is None):
        return True

    return False



# проверка существования профиля Git
def is_git_profile_exists(username):
    url = f"https://api.github.com/users/{username}"

    user_data = requests.get(url).json()

   # pprint(user_data)

    if 'message' in user_data:
        if user_data["message"] == "Not Found":
            return False
    else:
            return True


def is_course_real(course_id: int) :
    if course_id < 0 or course_id > len(yaml_files):
        return False
    return True