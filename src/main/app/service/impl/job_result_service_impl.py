"""JobResult domain service impl"""

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
from src.main.app.mapper.job_result_mapper import JobResultMapper
from src.main.app.model.job_result_model import JobResultDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.job_result_schema import JobResultQuery, JobResultPage, JobResultDetail, JobResultCreate
from src.main.app.service.impl.service_base_impl import ServiceBaseImpl
from src.main.app.service.job_result_service import JobResultService


class JobResultServiceImpl(ServiceBaseImpl[JobResultMapper, JobResultDO], JobResultService):
    """
    Implementation of the JobResultService interface.
    """

    def __init__(self, mapper: JobResultMapper):
        """
        Initialize the JobResultServiceImpl instance.

        Args:
            mapper (JobResultMapper): The JobResultMapper instance to use for database operations.
        """
        super().__init__(mapper=mapper)
        self.mapper = mapper

    async def fetch_job_result_by_page(self, job_result_query: JobResultQuery, request: Request) -> PageResult:
        eq = {}
        ne = {}
        gt = {}
        ge = {}
        lt = {}
        le = {}
        between = {}
        like = {}
        if job_result_query.id is not None and job_result_query.id != "" :
            eq["id"] = job_result_query.id
        if job_result_query.result_key is not None and job_result_query.result_key != "" :
            eq["result_key"] = job_result_query.result_key
        if job_result_query.create_time is not None and job_result_query.create_time != "" :
            eq["create_time"] = job_result_query.create_time
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
            current=job_result_query.current,
            pageSize=job_result_query.pageSize,
            **filters
        )
        if total == 0:
            return PageResult(records=[], total=total)
        if "sort" in JobResultDO.model_fields and total > 1:
            records.sort(key=lambda x: x['sort'])
        records = [JobResultPage(**record.model_dump()) for record in records]
        return PageResult(records=records, total=total)

    async def fetch_job_result_detail(self, *, id: int, request: Request) -> Optional[JobResultDetail]:
        job_result_do: JobResultDO =await self.mapper.select_by_id(id=id)
        if job_result_do is None:
            return None
        return JobResultDetail(**job_result_do.model_dump())

    async def export_job_result_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:
        if ids is None or len(ids) == 0:
            return None
        job_result_list: List[JobResultDO] = await self.retrieve_by_ids(ids = ids)
        if job_result_list is None or len(job_result_list) == 0:
            return None
        job_result_page_list = [JobResultPage(**job_result.model_dump()) for job_result in job_result_list]
        return await export_excel(schema=JobResultPage, file_name="job_result_data_export", data_list=job_result_page_list)

    async def create_job_result(self, job_result_create: JobResultCreate, request: Request) -> JobResultDO:
        job_result: JobResultDO = JobResultDO(**job_result_create.model_dump())
        # job_result.user_id = request.state.user_id
        return await self.save(data=job_result)

    async def batch_create_job_result(self, *, job_result_create_list: List[JobResultCreate], request: Request) -> List[int]:
        job_result_list: List[JobResultDO] = [JobResultDO(**job_result_create.model_dump()) for job_result_create in job_result_create_list]
        await self.batch_save(datas=job_result_list)
        return [job_result.id for job_result in job_result_list]

    @staticmethod
    async def import_job_result(*, file: UploadFile, request: Request) -> Union[List[JobResultCreate], None]:
        contents = await file.read()
        import_df = pd.read_excel(io.BytesIO(contents))
        import_df = import_df.fillna("")
        job_result_records = import_df.to_dict(orient="records")
        if job_result_records is None or len(job_result_records) == 0:
            return None
        for record in job_result_records:
            for key, value in record.items():
                if value == "":
                    record[key] = None
        job_result_create_list = []
        for job_result_record in job_result_records:
            try:
                job_result_create = JobResultCreate(**job_result_record)
                job_result_create_list.append(job_result_create)
            except Exception as e:
                valid_data = {k: v for k, v in job_result_record.items() if k in JobResultCreate.model_fields}
                job_result_create = JobResultCreate.model_construct(**valid_data)
                job_result_create.err_msg = ValidateService.get_validate_err_msg(e)
                job_result_create_list.append(job_result_create)
                return job_result_create_list

        return job_result_create_list