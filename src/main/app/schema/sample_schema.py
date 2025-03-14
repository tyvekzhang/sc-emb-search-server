"""Sample schema"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from src.main.app.schema.common_schema import PageBase

class SamplePage(BaseModel):
    """
    样本分页信息
    """
    # 主键
    id: int
    # 物种
    species: Optional[str] = None
    # 样本名
    sample_id: Optional[str] = None
    # 项目名
    project_id: Optional[str] = None
    # 组织、器官
    tissue: Optional[str] = None
    # 细胞数
    cell_count: Optional[int] = None
    # 项目标题
    project_title: Optional[str] = None
    # 项目总结
    project_summary: Optional[str] = None
    # 测序平台
    platform: Optional[str] = None
    # 扩展字段
    ext: Optional[str] = None
    # 创建时间
    create_time: Optional[datetime] = None

class SampleExport(BaseModel):
    """
    样本分页信息
    """
    # 物种
    species: Optional[str] = None
    # 样本名
    sample_id: Optional[str] = None
    # 项目名
    project_id: Optional[str] = None
    # 组织、器官
    tissue: Optional[str] = None
    # 细胞数
    cell_count: Optional[int] = None
    # 项目标题
    project_title: Optional[str] = None
    # 项目总结
    project_summary: Optional[str] = None
    # 测序平台
    platform: Optional[str] = None
    # 创建时间
    create_time: Optional[datetime] = None

class SampleQuery(PageBase):
    """
    样本查询参数
    """
    # 主键
    id: Optional[int] = None
    # 物种
    species: Optional[str] = None
    # 组织、器官
    tissue: Optional[str] = None
    # 细胞数
    cell_count: Optional[int] = None
    # 项目标题
    project_title: Optional[str] = None
    # 样本名
    sample_id: Optional[str] = None
    # 项目总结
    project_summary: Optional[str] = None
    # 测序平台
    platform: Optional[str] = None
    # 扩展字段
    ext: Optional[str] = None
    # 创建时间
    create_time: Optional[datetime] = None

class SampleCreate(BaseModel):
    """
    样本新增
    """
    # 物种
    species: Optional[str] = None
    # 样本名
    sample_id: Optional[str] = None
    # 项目名
    project_id: Optional[str] = None
    # 组织、器官
    tissue: Optional[str] = None
    # 细胞数
    cell_count: Optional[int] = None
    # 项目标题
    project_title: Optional[str] = None
    # 项目总结
    project_summary: Optional[str] = None
    # 测序平台
    platform: Optional[str] = None
    # 扩展字段
    ext: Optional[str] = None
    # 错误信息
    err_msg: Optional[str] = Field(None, alias="errMsg")

class SampleModify(BaseModel):
    """
    样本更新
    """
    # 主键
    id: int
    # 物种
    species: Optional[str] = None
    # 样本名
    sample_id: Optional[str] = None
    # 项目名
    project_id: Optional[str] = None
    # 组织、器官
    tissue: Optional[str] = None
    # 细胞数
    cell_count: Optional[int] = None
    # 项目标题
    project_title: Optional[str] = None
    # 项目总结
    project_summary: Optional[str] = None
    # 测序平台
    platform: Optional[str] = None
    # 扩展字段
    ext: Optional[str] = None

class SampleBatchModify(BaseModel):
    """
    样本批量更新
    """
    ids: List[int]
    # 物种
    species: Optional[str] = None
    # 样本名
    sample_id: Optional[str] = None
    # 项目名
    project_id: Optional[str] = None
    # 组织、器官
    tissue: Optional[str] = None
    # 细胞数
    cell_count: Optional[int] = None
    # 项目标题
    project_title: Optional[str] = None
    # 项目总结
    project_summary: Optional[str] = None
    # 测序平台
    platform: Optional[str] = None
    # 扩展字段
    ext: Optional[str] = None

class SampleOptions(BaseModel):
    id: int
    # 样本名
    sample_id: str = None
    # 组织、器官
    tissue: Optional[str] = None

class SampleDetail(BaseModel):
    """
    样本详情
    """
    # 主键
    id: int
    # 物种
    species: Optional[str] = None
    # 样本名
    sample_id: Optional[str] = None
    # 项目名
    project_id: Optional[str] = None
    # 组织、器官
    tissue: Optional[str] = None
    # 细胞数
    cell_count: Optional[int] = None
    # 项目标题
    project_title: Optional[str] = None
    # 项目总结
    project_summary: Optional[str] = None
    # 测序平台
    platform: Optional[str] = None
    # 扩展字段
    ext: Optional[str] = None
    # 创建时间
    create_time: Optional[datetime] = None