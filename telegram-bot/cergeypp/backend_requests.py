import requests
from config import server_url

address = server_url

def get_courses():
    return requests.get(address + "/courses")

def get_course_by_id(id):
    return requests.get(address + "/courses/" + id)
    
def get_groups_by_course_id(course_id):
    return requests.get(address + "/courses/" + course_id + "/groups")

def get_labs_by_course_and_group(course_id, group_id):
    return requests.get(address + "/courses/" + course_id + "/groups/" + group_id + "/labs")
                    
def register_student(course_id, group_id, student):
    return requests.post(address + "/courses/" + course_id + "/groups/" + group_id + "/register", json=student.__dict__)

def grade_lab(course_id, group_id, lab_id, github):
    return requests.post(address + "/courses/" + course_id + "/groups/" + group_id + "/labs/" + lab_id + "/grade", json={"github":github})