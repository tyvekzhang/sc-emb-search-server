"""File Service"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from fastapi import UploadFile, Request
from starlette.responses import StreamingResponse
from src.main.app.model.file_model import FileDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.file_schema import FileQuery, FileDetail, FileCreate
from src.main.app.service.service_base import ServiceBase


class FileService(ServiceBase[FileDO], ABC):

    @abstractmethod
    async def fetch_file_by_page(self, *, file_query: FileQuery, request: Request) -> PageResult:...

    @abstractmethod
    async def fetch_file_detail(self, *, id: int, request: Request) -> Optional[FileDetail]:...

    @abstractmethod
    async def export_file_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:...

    @abstractmethod
    async def create_file(self, *, file_create: FileCreate, request: Request) -> FileDO:...

    @abstractmethod
    async def batch_create_file(self, *, file_create_list: List[FileCreate], request: Request) -> List[int]:...

    @abstractmethod
    async def import_file(self, *, file: UploadFile, request: Request) -> List[FileCreate]:...

    @abstractmethod
    async def upload_file(self, file: UploadFile, request: Request):
        pass