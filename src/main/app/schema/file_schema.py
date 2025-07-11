"""File schema"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from src.main.app.schema.common_schema import PageBase

class FilePage(BaseModel):
    """
    文件分页信息
    """
    # 主键
    id: int
    # 文件名
    name: Optional[str] = None
    # 地址
    path: Optional[str] = None
    # 大小(MB)
    size: Optional[int] = None
    # 创建时间
    create_time: Optional[datetime] = None

class FileQuery(PageBase):
    """
    文件查询参数
    """
    # 主键
    id: Optional[int] = None
    # 文件名
    name: Optional[str] = None
    # 地址
    path: Optional[str] = None
    # 大小(MB)
    size: Optional[int] = None
    # 创建时间
    create_time: Optional[datetime] = None

class FileCreate(BaseModel):
    """
    文件新增
    """
    # 文件名
    name: Optional[str] = None
    # 地址
    path: Optional[str] = None
    # 大小(MB)
    size: Optional[int] = None
    # 错误信息
    err_msg: Optional[str] = Field(None, alias="errMsg")

class FileModify(BaseModel):
    """
    文件更新
    """
    # 主键
    id: int
    # 文件名
    name: Optional[str] = None
    # 地址
    path: Optional[str] = None
    # 大小(MB)
    size: Optional[int] = None

class FileBatchModify(BaseModel):
    """
    文件批量更新
    """
    ids: List[int]
    # 文件名
    name: Optional[str] = None
    # 地址
    path: Optional[str] = None
    # 大小(MB)
    size: Optional[int] = None

class FileDetail(BaseModel):
    """
    文件详情
    """
    # 主键
    id: int
    # 文件名
    name: Optional[str] = None
    # 地址
    path: Optional[str] = None
    # 大小(MB)
    size: Optional[int] = None
    # 创建时间
    create_time: Optional[datetime] = None

class UploadResponse(BaseModel):
    file_id: int
    barcode_list: List[str]