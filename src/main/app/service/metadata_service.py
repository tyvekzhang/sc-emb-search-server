"""Metadata Service"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from fastapi import UploadFile, Request
from starlette.responses import StreamingResponse
from src.main.app.model.metadata_model import MetadataEntity
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.metadata_schema import MetadataQuery, MetadataDetail, MetadataCreate
from src.main.app.service.service_base import ServiceBase


class MetadataService(ServiceBase[MetadataEntity], ABC):

    @abstractmethod
    async def fetch_metadata_by_page(self, *, metadata_query: MetadataQuery, request: Request) -> PageResult:...

    @abstractmethod
    async def fetch_metadata_detail(self, *, id: int, request: Request) -> Optional[MetadataDetail]:...

    @abstractmethod
    async def export_metadata_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:...

    @abstractmethod
    async def create_metadata(self, *, metadata_create: MetadataCreate, request: Request) -> MetadataEntity:...

    @abstractmethod
    async def batch_create_metadata(self, *, metadata_create_list: List[MetadataCreate], request: Request) -> List[int]:...

    @abstractmethod
    async def import_metadata(self, *, file: UploadFile, request: Request) -> List[MetadataCreate]:...