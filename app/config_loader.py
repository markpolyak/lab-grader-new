import yaml
import os
from typing import List, Dict
from app.models import CourseConfig, CourseDetails, LabReportTemplate


def load_config(file_path: str) -> CourseConfig:
    with open(file_path, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)

    # Преобразуем данные, чтобы они соответствовали модели
    course_data = config_data.get("course", {})
    labs_data = course_data.get("labs", {})

    labs = {}
    for lab_id, lab_info in labs_data.items():
        labs[lab_id] = LabReportTemplate(
            github_prefix=lab_info.get("github-prefix", ""),
            short_name=lab_info.get("short-name", ""),
            penalty_max=lab_info.get("penalty-max", 0),
            report=lab_info.get("report", [])
        )

    course_details = CourseDetails(
        name=course_data.get("name", ""),
        alt_names=course_data.get("alt-names", []),
        semester=course_data.get("semester", ""),
        email=course_data.get("email", ""),
        timezone=course_data.get("timezone", ""),
        github=course_data.get("github", {}),
        google=course_data.get("google", {}),
        staff=course_data.get("staff", []),
        labs=labs
    )

    return CourseConfig(course=course_details, misc=config_data.get("misc", {}))


def load_all_configs(directory: str) -> List[Dict]:
    configs = []
    for filename in os.listdir(directory):
        if filename.endswith(".yaml"):
            file_path = os.path.join(directory, filename)
            config = load_config(file_path)
            configs.append({
                "id": str(len(configs) + 1),
                "config": filename,
                "name": config.course.name,
                "semester": config.course.semester,
                "email": config.course.email,
                "github-organization": config.course.github.get("organization", ""),
                "google-spreadsheet": config.course.google.get("spreadsheet", "")
            })
    return configs
