"""File domain service impl"""

from __future__ import annotations
import io
import os
import uuid
from pathlib import Path
from typing import Optional, List
from typing import Union
import pandas as pd
from fastapi import UploadFile, Request
from starlette.responses import StreamingResponse

from src.main.app.common.config.config_manager import load_config
from src.main.app.common.enums.enum import FilterOperators
from src.main.app.common.exception.exception import ParameterException
from src.main.app.common.util.excel_util import export_excel
from src.main.app.common.util.validate_util import ValidateService
from src.main.app.mapper.file_mapper import FileMapper
from src.main.app.model.file_model import FileDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.file_schema import FileQuery, FilePage, FileDetail, FileCreate
from src.main.app.service.impl.service_base_impl import ServiceBaseImpl
from src.main.app.service.file_service import FileService


class FileServiceImpl(ServiceBaseImpl[FileMapper, FileDO], FileService):
    """
    Implementation of the FileService interface.
    """

    def __init__(self, mapper: FileMapper):
        """
        Initialize the FileServiceImpl instance.

        Args:
            mapper (FileMapper): The FileMapper instance to use for database operations.
        """
        super().__init__(mapper=mapper)
        self.mapper = mapper

    async def fetch_file_by_page(self, file_query: FileQuery, request: Request) -> PageResult:
        eq = {}
        ne = {}
        gt = {}
        ge = {}
        lt = {}
        le = {}
        between = {}
        like = {}
        if file_query.id is not None and file_query.id != "" :
            eq["id"] = file_query.id
        if file_query.name is not None and file_query.name != "" :
            like["name"] = file_query.name
        if file_query.path is not None and file_query.path != "" :
            eq["path"] = file_query.path
        if file_query.size is not None and file_query.size != "" :
            eq["size"] = file_query.size
        if file_query.create_time is not None and file_query.create_time != "" :
            eq["create_time"] = file_query.create_time
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
            current=file_query.current,
            pageSize=file_query.pageSize,
            **filters
        )
        if total == 0:
            return PageResult(records=[], total=total)
        if "sort" in FileDO.model_fields and total > 1:
            records.sort(key=lambda x: x['sort'])
        records = [FilePage(**record.model_dump()) for record in records]
        return PageResult(records=records, total=total)

    async def fetch_file_detail(self, *, id: int, request: Request) -> Optional[FileDetail]:
        file_do: FileDO =await self.mapper.select_by_id(id=id)
        if file_do is None:
            return None
        return FileDetail(**file_do.model_dump())

    async def export_file_page(self, *, ids: List[int], request: Request) -> Optional[StreamingResponse]:
        if ids is None or len(ids) == 0:
            return None
        file_list: List[FileDO] = await self.retrieve_by_ids(ids = ids)
        if file_list is None or len(file_list) == 0:
            return None
        file_page_list = [FilePage(**file.model_dump()) for file in file_list]
        return await export_excel(schema=FilePage, file_name="file_data_export", data_list=file_page_list)

    async def create_file(self, file_create: FileCreate, request: Request) -> FileDO:
        file: FileDO = FileDO(**file_create.model_dump())
        # file.user_id = request.state.user_id
        return await self.save(data=file)

    async def batch_create_file(self, *, file_create_list: List[FileCreate], request: Request) -> List[int]:
        file_list: List[FileDO] = [FileDO(**file_create.model_dump()) for file_create in file_create_list]
        await self.batch_save(datas=file_list)
        return [file.id for file in file_list]

    @staticmethod
    async def import_file(*, file: UploadFile, request: Request) -> Union[List[FileCreate], None]:
        contents = await file.read()
        import_df = pd.read_excel(io.BytesIO(contents))
        import_df = import_df.fillna("")
        file_records = import_df.to_dict(orient="records")
        if file_records is None or len(file_records) == 0:
            return None
        for record in file_records:
            for key, value in record.items():
                if value == "":
                    record[key] = None
        file_create_list = []
        for file_record in file_records:
            try:
                file_create = FileCreate(**file_record)
                file_create_list.append(file_create)
            except Exception as e:
                valid_data = {k: v for k, v in file_record.items() if k in FileCreate.model_fields}
                file_create = FileCreate.model_construct(**valid_data)
                file_create.err_msg = ValidateService.get_validate_err_msg(e)
                file_create_list.append(file_create)
                return file_create_list

        return file_create_list

    async def upload_file(self, file: UploadFile, request: Request):
        file_name = file.filename
        if not file_name.endswith(".h5ad"):
            raise ParameterException
        home_dir = Path(str(load_config().server.customer_dir))
        if not os.path.exists(home_dir):
            os.makedirs(home_dir)
        save_file_name = uuid.uuid4().hex + ".h5ad"
        h5ad_path = home_dir / save_file_name
        try:
            with open(h5ad_path, "wb") as f:
                contents = await file.read()
                f.write(contents)
        except Exception as e:
            raise Exception(f"Error writing file: {e}")
        file_data = FileDO(name=file_name, path=save_file_name, size=file.size)
        await self.save(data=file_data)
        return file_data.id
        