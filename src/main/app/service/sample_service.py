"""Sample Service"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from fastapi import UploadFile, Request
from starlette.responses import StreamingResponse
from src.main.app.model.sample_model import SampleDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.sample_schema import SampleQuery, SampleDetail, SampleCreate
from src.main.app.service.service_base import ServiceBase


class SampleService(ServiceBase[SampleDO], ABC):

    @abstractmethod
    async def fetch_sample_by_page(self, *, sample_query: SampleQuery, request: Request) -> PageResult:...

    @abstractmethod
    async def fetch_sample_detail(self, *, id: int, request: Request) -> Optional[SampleDetail]:...

    @abstractmethod
    async def export_sample_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:...

    @abstractmethod
    async def create_sample(self, *, sample_create: SampleCreate, request: Request) -> SampleDO:...

    @abstractmethod
    async def batch_create_sample(self, *, sample_create_list: List[SampleCreate], request: Request) -> List[int]:...

    @abstractmethod
    async def import_sample(self, *, file: UploadFile, request: Request) -> List[SampleCreate]:...

    @abstractmethod
    async def download_sample_page(self, id: int, request: Request):...

    @abstractmethod
    async def fetch_all_sample_by_species(self, species: str, request: Request): ...