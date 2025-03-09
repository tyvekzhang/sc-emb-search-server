"""Job Service"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from fastapi import UploadFile, Request
from starlette.responses import StreamingResponse
from src.main.app.model.job_model import JobDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.job_schema import JobQuery, JobDetail, JobCreate, JobSubmit
from src.main.app.service.service_base import ServiceBase


class JobService(ServiceBase[JobDO], ABC):

    @abstractmethod
    async def fetch_job_by_page(self, *, job_query: JobQuery, request: Request) -> PageResult:...

    @abstractmethod
    async def fetch_job_detail(self, *, id: int, request: Request) -> Optional[JobDetail]:...

    @abstractmethod
    async def export_job_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:...

    @abstractmethod
    async def create_job(self, *, job_create: JobCreate, request: Request) -> JobDO:...

    @abstractmethod
    async def submit_job(self, *, job_submit: JobSubmit, request: Request) -> JobDO:...

    @abstractmethod
    async def batch_create_job(self, *, job_create_list: List[JobCreate], request: Request) -> List[int]:...

    @abstractmethod
    async def import_job(self, *, file: UploadFile, request: Request) -> List[JobCreate]:...

    @abstractmethod
    async def get_result(self, job_id: int, request: Request, current: int , page_size: int ):...