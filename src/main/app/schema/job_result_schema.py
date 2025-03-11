"""JobResult schema"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from src.main.app.schema.common_schema import PageBase

class cell_emb_result(BaseModel):
    index: Optional[int] = None
    study: Optional[str] = None
    sample: Optional[str] = None
    prediction: Optional[str] = None
    tissue: Optional[str] = None
    cell_line: Optional[bool] = None
    disease: Optional[str] = None

class JobResultPage(BaseModel):
    """
    任务结果分页信息
    """
    # 主键
    id: int
    # 任务Id
    job_id: Optional[int] = None
    # 文件Id
    file_id: Optional[int] = None
    # 关键字
    result_key: Optional[str] = None
    # 创建时间
    create_time: Optional[datetime] = None

class JobResultQuery(PageBase):
    """
    任务结果查询参数
    """
    # 主键
    id: Optional[int] = None
    # 关键字
    result_key: Optional[str] = None
    # 创建时间
    create_time: Optional[datetime] = None

class JobResultCreate(BaseModel):
    """
    任务结果新增
    """
    # 任务Id
    job_id: Optional[int] = None
    # 文件Id
    file_id: Optional[int] = None
    # 关键字
    result_key: Optional[str] = None
    # 错误信息
    err_msg: Optional[str] = Field(None, alias="errMsg")

class JobResultModify(BaseModel):
    """
    任务结果更新
    """
    # 主键
    id: int
    # 任务Id
    job_id: Optional[int] = None
    # 文件Id
    file_id: Optional[int] = None
    # 关键字
    result_key: Optional[str] = None

class JobResultBatchModify(BaseModel):
    """
    任务结果批量更新
    """
    ids: List[int]
    # 任务Id
    job_id: Optional[int] = None
    # 文件Id
    file_id: Optional[int] = None
    # 关键字
    result_key: Optional[str] = None

class JobResultDetail(BaseModel):
    """
    任务结果详情
    """
    # 主键
    id: int
    # 任务Id
    job_id: Optional[int] = None
    # 文件Id
    file_id: Optional[int] = None
    # 关键字
    result_key: Optional[str] = None
    # 创建时间
    create_time: Optional[datetime] = None