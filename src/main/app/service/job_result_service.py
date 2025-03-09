"""JobResult Service"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from fastapi import UploadFile, Request
from starlette.responses import StreamingResponse
from src.main.app.model.job_result_model import JobResultDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.job_result_schema import JobResultQuery, JobResultDetail, JobResultCreate
from src.main.app.service.service_base import ServiceBase


class JobResultService(ServiceBase[JobResultDO], ABC):

    @abstractmethod
    async def fetch_job_result_by_page(self, *, job_result_query: JobResultQuery, request: Request) -> PageResult:...

    @abstractmethod
    async def fetch_job_result_detail(self, *, id: int, request: Request) -> Optional[JobResultDetail]:...

    @abstractmethod
    async def export_job_result_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:...

    @abstractmethod
    async def create_job_result(self, *, job_result_create: JobResultCreate, request: Request) -> JobResultDO:...

    @abstractmethod
    async def batch_create_job_result(self, *, job_result_create_list: List[JobResultCreate], request: Request) -> List[int]:...

    @abstractmethod
    async def import_job_result(self, *, file: UploadFile, request: Request) -> List[JobResultCreate]:...