"""Job schema"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Union
from pydantic import BaseModel, Field
from src.main.app.schema.common_schema import PageBase

class JobStatus(Enum):
    WAITING = 1
    EXECUTING = 2
    COMPLETED = 3

class JobPage(BaseModel):
    """
    任务分页信息
    """
    # 主键
    id: int
    # 任务名称
    job_name: Optional[str] = None
    # 父任务号
    parent_job_id: Optional[int] = None
    # 状态
    status: Optional[int] = None
    # 描述
    comment: Optional[str] = None
    # 创建时间
    creat_time: Optional[datetime] = None

class JobQuery(PageBase):
    """
    任务查询参数
    """
    # 主键
    id: Optional[int] = None
    # 任务名称
    job_name: Optional[str] = None
    # 状态
    status: Optional[int] = None
    # 创建时间
    creat_time: Optional[datetime] = None

class JobCreate(BaseModel):
    """
    任务新增
    """
    # 任务名称
    job_name: Optional[str] = None
    # 父任务号
    parent_job_id: Optional[int] = None
    # 状态
    status: Optional[int] = None
    # 描述
    comment: Optional[str] = None
    # 创建时间
    creat_time: Optional[datetime] = None
    # 错误信息
    err_msg: Optional[str] = Field(None, alias="errMsg")

class JobSubmit(BaseModel):
    """
    任务新增
    """
    model: int
    # 任务名称
    job_name: Optional[str] = None
    # 任务类型
    job_type: int
    # 文件标识
    file_info: str
    # 物种信息
    species: int
    # 细胞的索引
    cell_index: Union[str, int] = None
    # 每个细胞返回的结果数
    result_cell_count: Optional[int] = 1
    # 父任务号
    parent_job_id: Optional[int] = None
    # 状态
    status: Optional[int] = 1
    # 描述
    comment: Optional[str] = None
    # 创建时间
    creat_time: Optional[datetime] = None
    # 错误信息
    err_msg: Optional[str] = Field(None, alias="errMsg")

class JobModify(BaseModel):
    """
    任务更新
    """
    # 主键
    id: int
    # 任务名称
    job_name: Optional[str] = None
    # 父任务号
    parent_job_id: Optional[int] = None
    # 状态
    status: Optional[int] = None
    # 描述
    comment: Optional[str] = None
    # 创建时间
    creat_time: Optional[datetime] = None

class JobBatchModify(BaseModel):
    """
    任务批量更新
    """
    ids: List[int]
    # 任务名称
    job_name: Optional[str] = None
    # 父任务号
    parent_job_id: Optional[int] = None
    # 状态
    status: Optional[int] = None
    # 描述
    comment: Optional[str] = None
    # 创建时间
    creat_time: Optional[datetime] = None

class JobDetail(BaseModel):
    """
    任务详情
    """
    # 主键
    id: int
    # 任务名称
    job_name: Optional[str] = None
    # 父任务号
    parent_job_id: Optional[int] = None
    # 状态
    status: Optional[int] = None
    # 描述
    comment: Optional[str] = None
    # 创建时间
    creat_time: Optional[datetime] = None