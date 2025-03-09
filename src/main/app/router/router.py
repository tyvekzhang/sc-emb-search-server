"""Routing of system modules"""

from fastapi import APIRouter

from src.main.app.controller.probe_controller import probe_router
from src.main.app.controller.sample_controller import sample_router
from src.main.app.controller.file_controller import file_router
from src.main.app.controller.job_controller import job_router
from src.main.app.controller.job_result_controller import job_result_router


def create_router() -> APIRouter:
    router = APIRouter()
    router.include_router(probe_router, tags=["probe"], prefix="/probe")
    router.include_router(sample_router, tags=["sample"], prefix="/sample")
    router.include_router(file_router, tags=["file"], prefix="/file")
    router.include_router(job_router, tags=["job"], prefix="/job")
    router.include_router(job_result_router, tags=["job-result"], prefix="/job-result")
    return router
