from fastapi import APIRouter

from .odt import odt
from .list_configs import list_configs

report_router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

report_router.add_api_route(
    "/odt",
    odt,
    methods=['POST']
)

report_router.add_api_route(
    "/list_configs",
    list_configs,
    methods=['GET']
)
