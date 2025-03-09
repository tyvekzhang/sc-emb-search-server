"""Sample 前端控制器"""

from __future__ import annotations

from typing import Dict, Annotated, List, Any

from fastapi import APIRouter, Query, UploadFile, Form, Request
from src.main.app.common.schema.response_schema import HttpResponse
from src.main.app.common.util.excel_util import export_excel
from src.main.app.mapper.sample_mapper import sampleMapper
from src.main.app.model.sample_model import SampleDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.sample_schema import SampleQuery, SampleModify, SampleCreate, \
    SampleBatchModify, SampleDetail, SampleOptions
from src.main.app.service.impl.sample_service_impl import SampleServiceImpl
from src.main.app.service.sample_service import SampleService
from starlette.responses import StreamingResponse

sample_router = APIRouter()
sample_service: SampleService = SampleServiceImpl(mapper=sampleMapper)

@sample_router.get("/page")
async def fetch_sample_by_page(
    sample_query: Annotated[SampleQuery, Query()], request: Request
) -> Dict[str, Any]:
    sample_page_result: PageResult = await sample_service.fetch_sample_by_page(
        sample_query=sample_query,
        request=request
    )
    return HttpResponse.success(sample_page_result)

@sample_router.get("/list")
async def fetch_all_sample_by_species(
    species: Annotated[str, Query()], request: Request
) -> Dict[str, Any]:
    service_response: List[SampleOptions] = await sample_service.fetch_all_sample_by_species(species=species, request=request)
    return HttpResponse.success(service_response)

@sample_router.get("/detail/{id}")
async def fetch_sample_detail(
    id: int, request: Request
) -> Dict[str, Any]:
    sample_detail: SampleDetail = await sample_service.fetch_sample_detail(id=id, request=request)
    return HttpResponse.success(sample_detail)

@sample_router.get("/export-template")
async def export_template(request: Request) -> StreamingResponse:
    return await export_excel(schema=SampleCreate, file_name="sample_import_tpl")

@sample_router.get("/export")
async def export_sample_page(
    request: Request, ids: list[int] = Query(...)
) -> StreamingResponse:
    return await sample_service.export_sample_page(ids=ids, request=request)

@sample_router.get("/download")
async def download_sample_page(
    request: Request, id: int = Query(...)
) -> StreamingResponse:
    return await sample_service.download_sample_page(id=id, request=request)

@sample_router.post("/create")
async def create_sample(
    sample_create: SampleCreate, request: Request
) -> Dict[str, Any]:
    sample: SampleDO = await sample_service.create_sample(sample_create=sample_create, request=request)
    return HttpResponse.success(sample.id)

@sample_router.post("/batch-create")
async def batch_create_sample(
    sample_create_list: List[SampleCreate], request: Request
) -> Dict[str, Any]:
    ids: List[int] = await sample_service.batch_create_sample(sample_create_list=sample_create_list, request=request)
    return HttpResponse.success(ids)

@sample_router.post("/import")
async def import_sample(
    request: Request, file: UploadFile = Form()
) -> Dict[str, Any]:
    sample_create_list: List[SampleCreate] = await sample_service.import_sample(file=file, request=request)
    return HttpResponse.success(sample_create_list)

@sample_router.delete("/remove/{id}")
async def remove(
    id: int, request: Request
) -> Dict[str, Any]:
    await sample_service.remove_by_id(id=id)
    return HttpResponse.success()

@sample_router.delete("/batch-remove")
async def batch_remove(
    request: Request, ids: List[int] = Query(...),
) -> Dict[str, Any]:
    await sample_service.batch_remove_by_ids(ids=ids)
    return HttpResponse.success()

@sample_router.put("/modify")
async def modify(
    sample_modify: SampleModify, request: Request
) -> Dict[str, Any]:
    await sample_service.modify_by_id(data=SampleDO(**sample_modify.model_dump(exclude_unset=True)))
    return HttpResponse.success()

@sample_router.put("/batch-modify")
async def batch_modify(sample_batch_modify: SampleBatchModify, request: Request) -> Dict[str, Any]:
    cleaned_data = {k: v for k, v in sample_batch_modify.model_dump().items() if v is not None and k != "ids"}
    if len(cleaned_data) == 0:
        return HttpResponse.fail("内容不能为空")
    await sample_service.batch_modify_by_ids(ids=sample_batch_modify.ids, data=cleaned_data)
    return HttpResponse.success()