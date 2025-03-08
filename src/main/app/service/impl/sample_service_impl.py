"""Sample domain service impl"""

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
from src.main.app.mapper.sample_mapper import SampleMapper
from src.main.app.model.sample_model import SampleDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.sample_schema import SampleQuery, SamplePage, SampleDetail, SampleCreate
from src.main.app.service.impl.service_base_impl import ServiceBaseImpl
from src.main.app.service.sample_service import SampleService


class SampleServiceImpl(ServiceBaseImpl[SampleMapper, SampleDO], SampleService):
    """
    Implementation of the SampleService interface.
    """

    def __init__(self, mapper: SampleMapper):
        """
        Initialize the SampleServiceImpl instance.

        Args:
            mapper (SampleMapper): The SampleMapper instance to use for database operations.
        """
        super().__init__(mapper=mapper)
        self.mapper = mapper

    async def fetch_sample_by_page(self, sample_query: SampleQuery, request: Request) -> PageResult:
        eq = {}
        ne = {}
        gt = {}
        ge = {}
        lt = {}
        le = {}
        between = {}
        like = {}
        if sample_query.id is not None and sample_query.id != "" :
            eq["id"] = sample_query.id
        if sample_query.species is not None and sample_query.species != "" :
            eq["species"] = sample_query.species
        if sample_query.tissue is not None and sample_query.tissue != "" :
            eq["tissue"] = sample_query.tissue
        if sample_query.cell_count is not None and sample_query.cell_count != "" :
            eq["cell_count"] = sample_query.cell_count
        if sample_query.project_title is not None and sample_query.project_title != "" :
            eq["project_title"] = sample_query.project_title
        if sample_query.project_summary is not None and sample_query.project_summary != "" :
            eq["project_summary"] = sample_query.project_summary
        if sample_query.platform is not None and sample_query.platform != "" :
            eq["platform"] = sample_query.platform
        if sample_query.ext is not None and sample_query.ext != "" :
            eq["ext"] = sample_query.ext
        if sample_query.create_time is not None and sample_query.create_time != "" :
            eq["create_time"] = sample_query.create_time
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
            current=sample_query.current,
            pageSize=sample_query.pageSize,
            **filters
        )
        if total == 0:
            return PageResult(records=[], total=total)
        if "sort" in SampleDO.model_fields and total > 1:
            records.sort(key=lambda x: x['sort'])
        records = [SamplePage(**record.model_dump()) for record in records]
        return PageResult(records=records, total=total)

    async def fetch_sample_detail(self, *, id: int, request: Request) -> Optional[SampleDetail]:
        sample_do: SampleDO =await self.mapper.select_by_id(id=id)
        if sample_do is None:
            return None
        return SampleDetail(**sample_do.model_dump())

    async def export_sample_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:
        if ids is None or len(ids) == 0:
            return None
        sample_list: List[SampleDO] = await self.retrieve_by_ids(ids = ids)
        if sample_list is None or len(sample_list) == 0:
            return None
        sample_page_list = [SamplePage(**sample.model_dump()) for sample in sample_list]
        return await export_excel(schema=SamplePage, file_name="sample_data_export", data_list=sample_page_list)

    async def create_sample(self, sample_create: SampleCreate, request: Request) -> SampleDO:
        sample: SampleDO = SampleDO(**sample_create.model_dump())
        # sample.user_id = request.state.user_id
        return await self.save(data=sample)

    async def batch_create_sample(self, *, sample_create_list: List[SampleCreate], request: Request) -> List[int]:
        sample_list: List[SampleDO] = [SampleDO(**sample_create.model_dump()) for sample_create in sample_create_list]
        await self.batch_save(datas=sample_list)
        return [sample.id for sample in sample_list]

    @staticmethod
    async def import_sample(*, file: UploadFile, request: Request) -> Union[List[SampleCreate], None]:
        contents = await file.read()
        import_df = pd.read_excel(io.BytesIO(contents))
        import_df = import_df.fillna("")
        sample_records = import_df.to_dict(orient="records")
        if sample_records is None or len(sample_records) == 0:
            return None
        for record in sample_records:
            for key, value in record.items():
                if value == "":
                    record[key] = None
        sample_create_list = []
        for sample_record in sample_records:
            try:
                sample_create = SampleCreate(**sample_record)
                sample_create_list.append(sample_create)
            except Exception as e:
                valid_data = {k: v for k, v in sample_record.items() if k in SampleCreate.model_fields}
                sample_create = SampleCreate.model_construct(**valid_data)
                sample_create.err_msg = ValidateService.get_validate_err_msg(e)
                sample_create_list.append(sample_create)
                return sample_create_list

        return sample_create_list