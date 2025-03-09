"""Job domain service impl"""

from __future__ import annotations

import io
import os
from typing import Optional, List
from typing import Union

import pandas as pd
from fastapi import UploadFile, Request
from starlette.responses import StreamingResponse

from src.main.app.common.config.config_manager import load_config
from src.main.app.common.enums.enum import FilterOperators
from src.main.app.common.util.excel_util import export_excel
from src.main.app.common.util.validate_util import ValidateService
from src.main.app.mapper.file_mapper import fileMapper
from src.main.app.mapper.job_mapper import JobMapper
from src.main.app.mapper.job_result_mapper import jobResultMapper
from src.main.app.model.file_model import FileDO
from src.main.app.model.job_model import JobDO
from src.main.app.model.job_result_model import JobResultDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.job_result_schema import cell_emb_result
from src.main.app.schema.job_schema import JobQuery, JobPage, JobDetail, JobCreate, JobSubmit, JobStatus
from src.main.app.service.impl.service_base_impl import ServiceBaseImpl
from src.main.app.service.job_service import JobService


class JobServiceImpl(ServiceBaseImpl[JobMapper, JobDO], JobService):
    """
    Implementation of the JobService interface.
    """

    def __init__(self, mapper: JobMapper):
        """
        Initialize the JobServiceImpl instance.

        Args:
            mapper (JobMapper): The JobMapper instance to use for database operations.
        """
        super().__init__(mapper=mapper)
        self.mapper = mapper

    async def fetch_job_by_page(self, job_query: JobQuery, request: Request) -> PageResult:
        eq = {}
        ne = {}
        gt = {}
        ge = {}
        lt = {}
        le = {}
        between = {}
        like = {}
        if job_query.id is not None and job_query.id != "":
            eq["id"] = job_query.id
        if job_query.job_name is not None and job_query.job_name != "":
            like["job_name"] = job_query.job_name
        if job_query.status is not None and job_query.status != "":
            eq["status"] = job_query.status
        if job_query.creat_time is not None and job_query.creat_time != "":
            eq["creat_time"] = job_query.creat_time
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
            current=job_query.current,
            pageSize=job_query.pageSize,
            **filters
        )
        if total == 0:
            return PageResult(records=[], total=total)
        if "sort" in JobDO.model_fields and total > 1:
            records.sort(key=lambda x: x['sort'])
        records = [JobPage(**record.model_dump()) for record in records]
        return PageResult(records=records, total=total)

    async def fetch_job_detail(self, *, id: int, request: Request) -> Optional[JobDetail]:
        job_do: JobDO = await self.mapper.select_by_id(id=id)
        if job_do is None:
            return None
        return JobDetail(**job_do.model_dump())

    async def export_job_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:
        if ids is None or len(ids) == 0:
            return None
        job_list: List[JobDO] = await self.retrieve_by_ids(ids=ids)
        if job_list is None or len(job_list) == 0:
            return None
        job_page_list = [JobPage(**job.model_dump()) for job in job_list]
        return await export_excel(schema=JobPage, file_name="job_data_export", data_list=job_page_list)

    async def create_job(self, job_create: JobCreate, request: Request) -> JobDO:
        job: JobDO = JobDO(**job_create.model_dump())
        # job.user_id = request.state.user_id
        return await self.save(data=job)

    async def submit_job(self, job_submit: JobSubmit, request: Request) -> JobDO:
        if job_submit.job_type == 1:
            fileMapper.select_by_id(id=job_submit.file_info)
        job: JobDO = JobDO(**job_submit.model_dump())
        # job.user_id = request.state.user_id
        return await self.save(data=job)

    async def batch_create_job(self, *, job_create_list: List[JobCreate], request: Request) -> List[int]:
        job_list: List[JobDO] = [JobDO(**job_create.model_dump()) for job_create in job_create_list]
        await self.batch_save(datas=job_list)
        return [job.id for job in job_list]

    @staticmethod
    async def import_job(*, file: UploadFile, request: Request) -> Union[List[JobCreate], None]:
        contents = await file.read()
        import_df = pd.read_excel(io.BytesIO(contents))
        import_df = import_df.fillna("")
        job_records = import_df.to_dict(orient="records")
        if job_records is None or len(job_records) == 0:
            return None
        for record in job_records:
            for key, value in record.items():
                if value == "":
                    record[key] = None
        job_create_list = []
        for job_record in job_records:
            try:
                job_create = JobCreate(**job_record)
                job_create_list.append(job_create)
            except Exception as e:
                valid_data = {k: v for k, v in job_record.items() if k in JobCreate.model_fields}
                job_create = JobCreate.model_construct(**valid_data)
                job_create.err_msg = ValidateService.get_validate_err_msg(e)
                job_create_list.append(job_create)
                return job_create_list

        return job_create_list

    async def get_result(self, job_id: int, request: Request, current: int = 1, page_size: int = 10):
        job_record: JobDO = await self.mapper.select_by_id(id=job_id)
        status = job_record.status
        if status != JobStatus.COMPLETED.value:
            return {"status": status, "records": [], "total": 0}
        eq = {"job_id": job_record.id}
        filters = {
            FilterOperators.EQ: eq,
        }
        records, total_count = await jobResultMapper.select_by_page(**filters)
        if total_count == 0:
            return PageResult(records=[], total=total_count)
        record: JobResultDO = records[0]
        file_id = record.file_id
        file_record: FileDO = await fileMapper.select_by_id(id=file_id)
        file_path = file_record.path
        output_dir = load_config().server.output_dir
        df = pd.read_excel(os.path.join(output_dir, file_path))
        start = (current - 1) * page_size
        if start >= len(df):
            return {"status": status, "records": [], "total": len(df)}
        end = start + page_size
        paginated_df = df.iloc[start:end]
        data_dicts = paginated_df.to_dict(orient="records")
        cell_emb_results: List[cell_emb_result] = [cell_emb_result(**item) for item in data_dicts]
        return {"status": status, "records": cell_emb_results, "total": len(df)}
