import requests
from config import server

address = server

def get_subjects():
    return requests.get(address + "/courses")
    
def get_groups(course_id):
    return requests.get(address + "/courses/" + course_id + "/groups")

def get_labs(course_id, group_id):
    return requests.get(address + "/courses/" + course_id + "/groups/" + group_id + "/labs")
                    
def register_student(course_id, group_id, student):
    return requests.post(address + "/courses/" + course_id + "/groups/" + group_id + "/register", json=student.__dict__)

def grade_lab(course_id, group_id, lab_id, github):
    return requests.post(address + "/courses/" + course_id + "/groups/" + group_id + "/labs/" + lab_id + "/grade", json={"github":github})