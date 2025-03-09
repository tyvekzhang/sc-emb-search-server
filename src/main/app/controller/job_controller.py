"""Job 前端控制器"""

from __future__ import annotations
from typing import Dict, Annotated, List, Any, Union
from fastapi import APIRouter, Query, UploadFile, Form, Request
from starlette.responses import StreamingResponse
from src.main.app.common.schema.response_schema import HttpResponse
from src.main.app.common.util.excel_util import export_excel
from src.main.app.mapper.job_mapper import jobMapper
from src.main.app.model.job_model import JobDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.job_schema import JobQuery, JobModify, JobCreate, \
    JobBatchModify, JobDetail, JobSubmit
from src.main.app.service.impl.job_service_impl import JobServiceImpl
from src.main.app.service.job_service import JobService

job_router = APIRouter()
job_service: JobService = JobServiceImpl(mapper=jobMapper)

@job_router.get("/page")
async def fetch_job_by_page(
    job_query: Annotated[JobQuery, Query()], request: Request
) -> Dict[str, Any]:
    job_page_result: PageResult = await job_service.fetch_job_by_page(
        job_query=job_query,
        request=request
    )
    return HttpResponse.success(job_page_result)

@job_router.get("/detail/{id}")
async def fetch_job_detail(
    id: int, request: Request
) -> Dict[str, Any]:
    job_detail: JobDetail = await job_service.fetch_job_detail(id=id, request=request)
    return HttpResponse.success(job_detail)

@job_router.get("/export-template")
async def export_template(request: Request) -> StreamingResponse:
    return await export_excel(schema=JobCreate, file_name="job_import_tpl")

@job_router.get("/export")
async def export_job_page(
    request: Request, ids: list[int] = Query(...)
) -> StreamingResponse:
    return await job_service.export_job_page(ids=ids, request=request)

@job_router.post("/create")
async def create_job(
    job_create: JobCreate, request: Request
) -> Dict[str, Any]:
    job: JobDO = await job_service.create_job(job_create=job_create, request=request)
    return HttpResponse.success(job.id)

@job_router.post("/submit")
async def submit_job(
    job_submit: JobSubmit, request: Request
) -> Dict[str, Any]:
    job: JobDO = await job_service.submit_job(job_submit=job_submit, request=request)
    return HttpResponse.success(job.id)

@job_router.get("/getResult")
async def get_result(
    job_id: int, request: Request, current: int = 1, page_size: int = 10
) -> Dict[str, Any]:
    service_resp = await job_service.get_result(job_id=job_id, request=request, current = current, page_size=page_size)
    return HttpResponse.success(service_resp)

@job_router.post("/batch-create")
async def batch_create_job(
    job_create_list: List[JobCreate], request: Request
) -> Dict[str, Any]:
    ids: List[int] = await job_service.batch_create_job(job_create_list=job_create_list, request=request)
    return HttpResponse.success(ids)

@job_router.post("/import")
async def import_job(
    request: Request, file: UploadFile = Form()
) -> Dict[str, Any]:
    job_create_list: List[JobCreate] = await job_service.import_job(file=file, request=request)
    return HttpResponse.success(job_create_list)

@job_router.delete("/remove/{id}")
async def remove(
    id: int, request: Request
) -> Dict[str, Any]:
    await job_service.remove_by_id(id=id)
    return HttpResponse.success()

@job_router.delete("/batch-remove")
async def batch_remove(
    request: Request, ids: List[int] = Query(...),
) -> Dict[str, Any]:
    await job_service.batch_remove_by_ids(ids=ids)
    return HttpResponse.success()

@job_router.put("/modify")
async def modify(
    job_modify: JobModify, request: Request
) -> Dict[str, Any]:
    await job_service.modify_by_id(data=JobDO(**job_modify.model_dump(exclude_unset=True)))
    return HttpResponse.success()

@job_router.put("/batch-modify")
async def batch_modify(job_batch_modify: JobBatchModify, request: Request) -> Dict[str, Any]:
    cleaned_data = {k: v for k, v in job_batch_modify.model_dump().items() if v is not None and k != "ids"}
    if len(cleaned_data) == 0:
        return HttpResponse.fail("内容不能为空")
    await job_service.batch_modify_by_ids(ids=job_batch_modify.ids, data=cleaned_data)
    return HttpResponse.success()