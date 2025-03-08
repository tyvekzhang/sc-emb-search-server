"""File 前端控制器"""

from __future__ import annotations
from typing import Dict, Annotated, List, Any, Union
from fastapi import APIRouter, Query, UploadFile, Form, Request
from starlette.responses import StreamingResponse
from src.main.app.common.schema.response_schema import HttpResponse
from src.main.app.common.util.excel_util import export_excel
from src.main.app.mapper.file_mapper import fileMapper
from src.main.app.model.file_model import FileDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.file_schema import FileQuery, FileModify, FileCreate, \
    FileBatchModify, FileDetail
from src.main.app.service.impl.file_service_impl import FileServiceImpl
from src.main.app.service.file_service import FileService

file_router = APIRouter()
file_service: FileService = FileServiceImpl(mapper=fileMapper)

@file_router.get("/page")
async def fetch_file_by_page(
    file_query: Annotated[FileQuery, Query()], request: Request
) -> Dict[str, Any]:
    file_page_result: PageResult = await file_service.fetch_file_by_page(
        file_query=file_query,
        request=request
    )
    return HttpResponse.success(file_page_result)

@file_router.get("/detail/{id}")
async def fetch_file_detail(
    id: int, request: Request
) -> Dict[str, Any]:
    file_detail: FileDetail = await file_service.fetch_file_detail(id=id, request=request)
    return HttpResponse.success(file_detail)

@file_router.get("/export-template")
async def export_template(request: Request) -> StreamingResponse:
    return await export_excel(schema=FileCreate, file_name="file_import_tpl")

@file_router.get("/export")
async def export_file_page(
    request: Request, ids: list[int] = Query(...)
) -> StreamingResponse:
    return await file_service.export_file_page(ids=ids, request=request)

@file_router.post("/create")
async def create_file(
    file_create: FileCreate, request: Request
) -> Dict[str, Any]:
    file: FileDO = await file_service.create_file(file_create=file_create, request=request)
    return HttpResponse.success(file.id)

@file_router.post("/batch-create")
async def batch_create_file(
    file_create_list: List[FileCreate], request: Request
) -> Dict[str, Any]:
    ids: List[int] = await file_service.batch_create_file(file_create_list=file_create_list, request=request)
    return HttpResponse.success(ids)

@file_router.post("/import")
async def import_file(
    request: Request, file: UploadFile = Form()
) -> Dict[str, Any]:
    file_create_list: List[FileCreate] = await file_service.import_file(file=file, request=request)
    return HttpResponse.success(file_create_list)

@file_router.delete("/remove/{id}")
async def remove(
    id: int, request: Request
) -> Dict[str, Any]:
    await file_service.remove_by_id(id=id)
    return HttpResponse.success()

@file_router.delete("/batch-remove")
async def batch_remove(
    request: Request, ids: List[int] = Query(...),
) -> Dict[str, Any]:
    await file_service.batch_remove_by_ids(ids=ids)
    return HttpResponse.success()

@file_router.put("/modify")
async def modify(
    file_modify: FileModify, request: Request
) -> Dict[str, Any]:
    await file_service.modify_by_id(data=FileDO(**file_modify.model_dump(exclude_unset=True)))
    return HttpResponse.success()

@file_router.put("/batch-modify")
async def batch_modify(file_batch_modify: FileBatchModify, request: Request) -> Dict[str, Any]:
    cleaned_data = {k: v for k, v in file_batch_modify.model_dump().items() if v is not None and k != "ids"}
    if len(cleaned_data) == 0:
        return HttpResponse.fail("内容不能为空")
    await file_service.batch_modify_by_ids(ids=file_batch_modify.ids, data=cleaned_data)
    return HttpResponse.success()