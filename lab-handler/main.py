from fastapi import FastAPI, HTTPException, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict

from read_courses import get_course_details_data, get_course_groups, get_courses, get_labs_short_names, assign_github_login, grade_lab

app = FastAPI()


class Course(BaseModel):
    id: str
    name: str
    semester: str

class CourseDetail(BaseModel):
    id: str
    config: str
    name: str
    semester: str
    email: str
    github_organization: str
    google_spreadsheet: str

@app.get("/courses/", response_model=List[Course])
def get_courses_list():
    courses = get_courses()
    return JSONResponse(status_code=200, content=courses)


@app.get("/courses/{course_id}", response_model=CourseDetail)
def get_course_detail(course_id: int):
    details = get_course_details_data(course_id)
    return JSONResponse(status_code=200, content=details)

@app.get("/courses/{course_id}/groups", response_model=List[str])
def get_course_groups_req(course_id: int):
    groups = get_course_groups(course_id)
    return JSONResponse(status_code=200, content=groups)
    raise HTTPException(status_code=501, detail="Not implemented")

@app.get("/courses/{course_id}/groups/{group_id}/labs", response_model=List[str])
def get_course_group_labs(course_id: int, group_id: str):
    labs = get_labs_short_names(course_id, group_id)
    return JSONResponse(status_code=200, content=labs)

class StudentRegistration(BaseModel):
    name: str = Field(..., min_length=1)
    surname: str = Field(..., min_length=1)
    patronymic: str = Field("", min_length=0)
    github: str = Field(..., min_length=1)

    @field_validator("patronymic")
    def validate_patronymic(cls, v):
        return v if v else ""
    

@app.post("/courses/{course_id}/groups/{group_id}/register")
def register_student(
    course_id: int = Path(..., description="Идентификатор курса"),
    group_id: str = Path(..., description="Идентификатор группы"),
    student: StudentRegistration = Body(..., description="Информация о студенте")
):
    name = student.surname + " " + student.name
    if student.patronymic:
        name = name + " " + student.patronymic
    if assign_github_login(course_id, group_id, name, student.github) == None:
        return JSONResponse(status_code=202, content={'message': "Этот аккаунт GitHub уже был указан ранее для этого же студента. Для изменения аккаунта обратитесь к преподавателю"})
    else:
        return JSONResponse(status_code=200, content={'message': "Аккаунт Github успешно создан"})



# Модель данных для тела запроса
class GradeRequest(BaseModel):
    github: str

@app.post("/courses/{course_id}/groups/{group_id}/labs/{lab_id}/grade")
async def grade_lab_req(course_id: str, group_id: str, lab_id: str, request: GradeRequest):
    grade_lab(course_id, group_id, lab_id, request.github)
    return {"message": "Lab successfully graded"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


