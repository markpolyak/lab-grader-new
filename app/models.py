from pydantic import BaseModel
from typing import List, Dict, Any


class LabReportTemplate(BaseModel):
    github_prefix: str
    short_name: str
    penalty_max: int
    report: List[str]


class CourseDetails(BaseModel):
    name: str
    alt_names: List[str]
    semester: str
    email: str
    timezone: str
    github: Dict[str, Any]
    google: Dict[str, Any]
    staff: List[Dict[str, str]]
    labs: Dict[str, LabReportTemplate]


class CourseConfig(BaseModel):
    course: CourseDetails
    misc: Dict[str, int]
