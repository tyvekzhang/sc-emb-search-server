"""Job domain service impl"""

from __future__ import annotations

import io
import os
import re
from typing import Optional, List
from typing import Union

import pandas as pd
import scanpy as sc
from fastapi import UploadFile, Request, BackgroundTasks
from loguru import logger
from scimilarity.utils import lognorm_counts, align_dataset
from starlette.responses import StreamingResponse

from src.main.app.common.cell_emb_search.cell_search_model import CellQuerySingleton
from src.main.app.common.config.config_manager import load_config
from src.main.app.common.enums.enum import FilterOperators
from src.main.app.common.util.excel_util import export_excel
from src.main.app.common.util.validate_util import ValidateService
from src.main.app.mapper.file_mapper import fileMapper
from src.main.app.mapper.job_mapper import JobMapper, jobMapper
from src.main.app.mapper.job_result_mapper import jobResultMapper
from src.main.app.mapper.sample_mapper import sampleMapper
from src.main.app.model.file_model import FileDO
from src.main.app.model.job_model import JobDO
from src.main.app.model.job_result_model import JobResultDO
from src.main.app.model.sample_model import SampleDO
from src.main.app.schema.common_schema import PageResult
from src.main.app.schema.job_result_schema import cell_emb_result
from src.main.app.schema.job_schema import JobQuery, JobPage, JobDetail, JobCreate, JobSubmit, JobStatus
from src.main.app.service.geneformer.cell_embedding import generate_cell_embedding, process_embeddings
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
        return await self.save(data=job)

    async def generate_search_result(self, job_submit: JobSubmit, job: JobDO):
        session = self.mapper.db.session
        job_id = job.id
        file_name = str(job_id) + ".xlsx"
        server_config = load_config().server
        output_dir = server_config.output_dir
        output_path = os.path.join(output_dir, file_name)
        try:
            h5ad_path: str = ""
            file_info = job_submit.file_info

            # 本地文件上传
            if job_submit.job_type == 1:
                customer_dir = server_config.customer_dir
                file_record: FileDO = await fileMapper.select_by_id(id=file_info, db_session=session)
                file_path = file_record.path
                h5ad_path = os.path.join(customer_dir, file_path)
            # 内置文件
            elif job_submit.job_type == 2:
                built_in_dir = server_config.built_in_dir
                sample_record: SampleDO = await sampleMapper.select_by_id(id=file_info, db_session=session)
                file_path = sample_record.sample_id + ".h5ad"
                h5ad_path = os.path.join(built_in_dir, file_path)

            adata = sc.read_h5ad(h5ad_path)

            cell_index = job_submit.cell_index
            result_cell_count = job_submit.result_cell_count

            if cell_index is None:
                cell_index = 1
                adata = adata[cell_index, :]
            else:
                try:
                    pattern = r'^-?\d+$'
                    num = bool(re.match(pattern, cell_index))
                    if num:
                        cell_index = int(cell_index)
                        if cell_index< 0 or cell_index > adata.n_obs:
                            cell_index = 1
                        adata = adata[cell_index, :]
                    else:
                        cell_index = cell_index.replace("，", ",")
                        cell_index = [index for index in cell_index.split(",")]
                        adata = adata[adata.obs_names.isin(cell_index)]
                except:
                    logger.error(f"不能够找到Barcode: {cell_index}")
                    raise

            if result_cell_count is None or result_cell_count < 1 or result_cell_count > 10000:
                result_cell_count = 10000
            model_dir = load_config().server.model_dir
            logger.info(f"开始加载模型")
            cq = CellQuerySingleton(model_dir)
            logger.info(f"模型加载完成")
            query_embedding = None
            df = None
            if job_submit.model == 2:
                query_embedding = generate_cell_embedding(adata, job)
                df = pd.DataFrame(query_embedding)
                query_embedding = process_embeddings(query_embedding)
            elif job_submit.model == 1:
                if "counts" not in adata.layers:
                    adata.layers['counts'] = adata.X.copy()
                adata = align_dataset(adata, cq.gene_order)
                adata = lognorm_counts(adata)
                adata.obsm["X_scimilarity"] = cq.get_embeddings(adata.X)
                query_embedding = adata.obsm["X_scimilarity"]
                df = pd.DataFrame(query_embedding)
            nn_idxs, nn_dists, results_metadata = cq.search_nearest(query_embedding, k=result_cell_count)
            # 将结果保存到 Excel 文件
            results_metadata.to_excel(output_path, index=False)
            emb_output_path = output_path.replace(".xlsx", "_emb.xlsx")
            df.to_excel(emb_output_path, index=False)


            # 更新任务状态
            job.status = 3
            await jobMapper.update_by_id(record=job, db_session=session)
            logger.info(f"job已完成{job}")

            # 保存文件记录
            file_data = FileDO(name=file_name, path=file_name, size=os.path.getsize(output_path))
            await fileMapper.insert(record=file_data, db_session=session)
            logger.info(f"文件记录已保存{file_data}")

            # 保存任务结果记录
            job_result_data = JobResultDO(job_id=job_id, file_id=file_data.id, result_key="cell_search")
            await jobResultMapper.insert(record=job_result_data, db_session=session)
            logger.info(f"任务结果已保存{job_result_data}")
            await session.commit()

        except Exception as e:
            logger.error(f"{e}")
            job.status = 4
            await jobMapper.update_by_id(record=job, db_session=session)
            await session.commit()
            logger.info(f"job已失败{job}")

    async def submit_job(self, job_submit: JobSubmit, request: Request, background_tasks: BackgroundTasks) -> JobDO:
        job: JobDO = JobDO(**job_submit.model_dump())
        # 正在进行中
        job.status=2

        await self.save(data=job)
        logger.info(f"job已保存{job}")

        # 异步执行 generate_search_result
        background_tasks.add_task(self.generate_search_result, job_submit, job)

        return job

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
        df = df.fillna("-")
        start = (current - 1) * page_size
        if start >= len(df):
            return {"status": status, "records": [], "total": len(df)}
        end = start + page_size
        paginated_df = df.iloc[start:end]
        data_dicts = paginated_df.to_dict(orient="records")
        cell_emb_results: List[cell_emb_result] = [cell_emb_result(**item) for item in data_dicts]
        return {"status": status, "records": cell_emb_results, "total": len(df)}

    @staticmethod
    async def export_result(job_id: int, request: Request, emb: bool):
        output_dir = load_config().server.output_dir
        file_name = str(job_id) + ".xlsx"

        download_file_name = "export_data_" + file_name
        if emb:
            download_file_name = download_file_name.replace(".xlsx", "_emb.xlsx")
            file_name = file_name.replace(".xlsx", "_emb.xlsx")
        result_path = os.path.join(output_dir, file_name)
        def file_iterator(file_path, chunk_size=1024 * 1024):
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    yield chunk

        headers = {"Content-Disposition": f"attachment; filename={download_file_name}"}

        return StreamingResponse(file_iterator(result_path), media_type="application/octet-stream", headers=headers)

