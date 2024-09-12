from fastapi import FastAPI
from fastapi import Request

app = FastAPI(
    title='Grader-New'
)

from routers import report_router

################################################################################

app.include_router(report_router)

################################################################################
