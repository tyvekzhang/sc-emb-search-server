"""Metadata domain service impl"""

from __future__ import annotations
import io
from typing import Optional, List
from typing import Union
import pandas as pd
from fastapi import UploadFile, Request
from fastapi.exceptions import ResponseValidationError
from starlette.responses import StreamingResponse
from src.main.app.common.enums.enum import FilterOperators
from src.main.app.common.util.excel_util import export_excel
from src.main.app.common.util.validate_util import ValidateService
from src.main.app.mapper.metadata_mapper import MetadataMapper
from src.main.app.model.metadata_model import MetadataEntity
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.metadata_schema import MetadataQuery, MetadataPage, MetadataDetail, MetadataCreate
from src.main.app.service.impl.service_base_impl import ServiceBaseImpl
from src.main.app.service.metadata_service import MetadataService


class MetadataServiceImpl(ServiceBaseImpl[MetadataMapper, MetadataEntity], MetadataService):
    """
    Implementation of the MetadataService interface.
    """

    def __init__(self, mapper: MetadataMapper):
        """
        Initialize the MetadataServiceImpl instance.

        Args:
            mapper (MetadataMapper): The MetadataMapper instance to use for database operations.
        """
        super().__init__(mapper=mapper)
        self.mapper = mapper

    async def fetch_metadata_by_page(self, metadata_query: MetadataQuery, request: Request) -> PageResult:
        eq = {}
        ne = {}
        gt = {}
        ge = {}
        lt = {}
        le = {}
        between = {}
        like = {}
        if metadata_query.id is not None and metadata_query.id != "" :
            eq["id"] = metadata_query.id
        if metadata_query.barcode is not None and metadata_query.barcode != "" :
            eq["barcode"] = metadata_query.barcode
        if metadata_query.assay is not None and metadata_query.assay != "" :
            eq["assay"] = metadata_query.assay
        if metadata_query.organism is not None and metadata_query.organism != "" :
            eq["organism"] = metadata_query.organism
        if metadata_query.development_stage is not None and metadata_query.development_stage != "" :
            eq["development_stage"] = metadata_query.development_stage
        if metadata_query.tissue is not None and metadata_query.tissue != "" :
            eq["tissue"] = metadata_query.tissue
        if metadata_query.disease is not None and metadata_query.disease != "" :
            eq["disease"] = metadata_query.disease
        if metadata_query.sex is not None and metadata_query.sex != "" :
            eq["sex"] = metadata_query.sex
        if metadata_query.cell_type is not None and metadata_query.cell_type != "" :
            eq["cell_type"] = metadata_query.cell_type
        if metadata_query.cell_embedding is not None and metadata_query.cell_embedding != "" :
            eq["cell_embedding"] = metadata_query.cell_embedding
        if metadata_query.create_time is not None and metadata_query.create_time != "" :
            eq["create_time"] = metadata_query.create_time
        filters = {
            FilterOperators.EQ: eq,
            FilterOperators.NE: ne,
            FilterOperators.GT: gt,
            FilterOperators.GE: ge,
            FilterOperators.LT: lt,
            FilterOperators.LE: le,
            FilterOperators.BETWEEN: between,
            FilterOperators.LIKE: like
        }
        records, total = await self.mapper.select_by_ordered_page(
            current=metadata_query.current,
            pageSize=metadata_query.pageSize,
            **filters
        )
        if total == 0:
            return PageResult(records=[], total=total)
        if "sort" in MetadataEntity.model_fields and total > 1:
            records.sort(key=lambda x: x['sort'])
        records = [MetadataPage(**record.model_dump()) for record in records]
        return PageResult(records=records, total=total)

    async def fetch_metadata_detail(self, *, id: int, request: Request) -> Optional[MetadataDetail]:
        metadata_do: MetadataEntity =await self.mapper.select_by_id(id=id)
        if metadata_do is None:
            return None
        return MetadataDetail(**metadata_do.model_dump())

    async def export_metadata_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:
        if ids is None or len(ids) == 0:
            return None
        metadata_list: List[MetadataEntity] = await self.retrieve_by_ids(ids = ids)
        if metadata_list is None or len(metadata_list) == 0:
            return None
        metadata_page_list = [MetadataPage(**metadata.model_dump()) for metadata in metadata_list]
        return await export_excel(schema=MetadataPage, file_name="metadata_data_export", data_list=metadata_page_list)

    async def create_metadata(self, metadata_create: MetadataCreate, request: Request) -> MetadataEntity:
        metadata: MetadataEntity = MetadataEntity(**metadata_create.model_dump())
        # metadata.user_id = request.state.user_id
        return await self.save(data=metadata)

    async def batch_create_metadata(self, *, metadata_create_list: List[MetadataCreate], request: Request) -> List[int]:
        metadata_list: List[MetadataEntity] = [MetadataEntity(**metadata_create.model_dump()) for metadata_create in metadata_create_list]
        await self.batch_save(datas=metadata_list)
        return [metadata.id for metadata in metadata_list]

    @staticmethod
    async def import_metadata(*, file: UploadFile, request: Request) -> Union[List[MetadataCreate], None]:
        contents = await file.read()
        import_df = pd.read_excel(io.BytesIO(contents))
        import_df = import_df.fillna("")
        metadata_records = import_df.to_dict(orient="records")
        if metadata_records is None or len(metadata_records) == 0:
            return None
        for record in metadata_records:
            for key, value in record.items():
                if value == "":
                    record[key] = None
        metadata_create_list = []
        for metadata_record in metadata_records:
            try:
                metadata_create = MetadataCreate(**metadata_record)
                metadata_create_list.append(metadata_create)
            except Exception as e:
                valid_data = {k: v for k, v in metadata_record.items() if k in MetadataCreate.model_fields}
                metadata_create = MetadataCreate.model_construct(**valid_data)
                metadata_create.err_msg = ValidateService.get_validate_err_msg(e)
                metadata_create_list.append(metadata_create)
                return metadata_create_list

        return metadata_create_list