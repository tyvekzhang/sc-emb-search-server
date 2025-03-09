"""JobResult 前端控制器"""

from __future__ import annotations
from typing import Dict, Annotated, List, Any, Union
from fastapi import APIRouter, Query, UploadFile, Form, Request
from starlette.responses import StreamingResponse
from src.main.app.common.schema.response_schema import HttpResponse
from src.main.app.common.util.excel_util import export_excel
from src.main.app.mapper.job_result_mapper import jobResultMapper
from src.main.app.model.job_result_model import JobResultDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.job_result_schema import JobResultQuery, JobResultModify, JobResultCreate, \
    JobResultBatchModify, JobResultDetail
from src.main.app.service.impl.job_result_service_impl import JobResultServiceImpl
from src.main.app.service.job_result_service import JobResultService

job_result_router = APIRouter()
job_result_service: JobResultService = JobResultServiceImpl(mapper=jobResultMapper)

@job_result_router.get("/page")
async def fetch_job_result_by_page(
    job_result_query: Annotated[JobResultQuery, Query()], request: Request
) -> Dict[str, Any]:
    job_result_page_result: PageResult = await job_result_service.fetch_job_result_by_page(
        job_result_query=job_result_query,
        request=request
    )
    return HttpResponse.success(job_result_page_result)

@job_result_router.get("/detail/{id}")
async def fetch_job_result_detail(
    id: int, request: Request
) -> Dict[str, Any]:
    job_result_detail: JobResultDetail = await job_result_service.fetch_job_result_detail(id=id, request=request)
    return HttpResponse.success(job_result_detail)

@job_result_router.get("/export-template")
async def export_template(request: Request) -> StreamingResponse:
    return await export_excel(schema=JobResultCreate, file_name="job_result_import_tpl")

@job_result_router.get("/export")
async def export_job_result_page(
    request: Request, ids: list[int] = Query(...)
) -> StreamingResponse:
    return await job_result_service.export_job_result_page(ids=ids, request=request)

@job_result_router.post("/create")
async def create_job_result(
    job_result_create: JobResultCreate, request: Request
) -> Dict[str, Any]:
    job_result: JobResultDO = await job_result_service.create_job_result(job_result_create=job_result_create, request=request)
    return HttpResponse.success(job_result.id)

@job_result_router.post("/batch-create")
async def batch_create_job_result(
    job_result_create_list: List[JobResultCreate], request: Request
) -> Dict[str, Any]:
    ids: List[int] = await job_result_service.batch_create_job_result(job_result_create_list=job_result_create_list, request=request)
    return HttpResponse.success(ids)

@job_result_router.post("/import")
async def import_job_result(
    request: Request, file: UploadFile = Form()
) -> Dict[str, Any]:
    job_result_create_list: List[JobResultCreate] = await job_result_service.import_job_result(file=file, request=request)
    return HttpResponse.success(job_result_create_list)

@job_result_router.delete("/remove/{id}")
async def remove(
    id: int, request: Request
) -> Dict[str, Any]:
    await job_result_service.remove_by_id(id=id)
    return HttpResponse.success()

@job_result_router.delete("/batch-remove")
async def batch_remove(
    request: Request, ids: List[int] = Query(...),
) -> Dict[str, Any]:
    await job_result_service.batch_remove_by_ids(ids=ids)
    return HttpResponse.success()

@job_result_router.put("/modify")
async def modify(
    job_result_modify: JobResultModify, request: Request
) -> Dict[str, Any]:
    await job_result_service.modify_by_id(data=JobResultDO(**job_result_modify.model_dump(exclude_unset=True)))
    return HttpResponse.success()

@job_result_router.put("/batch-modify")
async def batch_modify(job_result_batch_modify: JobResultBatchModify, request: Request) -> Dict[str, Any]:
    cleaned_data = {k: v for k, v in job_result_batch_modify.model_dump().items() if v is not None and k != "ids"}
    if len(cleaned_data) == 0:
        return HttpResponse.fail("内容不能为空")
    await job_result_service.batch_modify_by_ids(ids=job_result_batch_modify.ids, data=cleaned_data)
    return HttpResponse.success()