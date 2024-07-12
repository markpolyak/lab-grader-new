from fastapi import FastAPI, Query, Body

from src.report_generator.latex_template_generate import get_courses_course_id, get_template, FormatType, LabRequest

app = FastAPI(title="Генерация шаблона отчета")
@app.get("/courses/{course_id}/staff")
def get_courses_staff(course_id: str):
    return get_courses_course_id(course_id)

@app.post("/courses/{course_id}/groups/{group_id}/labs/{lab_id}")
def get_lab_template(
        course_id: str,
        group_id: str,
        lab_id: str,
        format: str = Query(..., enum=["docx", "odf", "latex"]),
        request_data: LabRequest = Body(...)
):
    format_enum = FormatType(format)
    return get_template(
        course_id=course_id,
        group_id=group_id,
        lab_id=lab_id,
        format=format_enum,
        request_data=request_data
    )
