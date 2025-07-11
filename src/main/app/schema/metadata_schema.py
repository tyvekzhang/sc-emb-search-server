"""Metadata schema"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from src.main.app.schema.common_schema import PageBase

class MetadataPage(BaseModel):
    """
    元数据分页信息
    """
    # 主键
    id: int
    # 细胞标识
    barcode: Optional[str] = None
    # 样本ID
    sample_id: Optional[str] = None
    # 测序平台
    assay: Optional[str] = None
    # 物种
    organism: Optional[str] = None
    # 发育阶段
    development_stage: Optional[str] = None
    # 组织类型
    tissue: Optional[str] = None
    # 疾病状态
    disease: Optional[str] = None
    # 性别
    sex: Optional[str] = None
    # 细胞类型
    cell_type: Optional[str] = None
    # 细胞向量
    cell_embedding: Optional[List[float]] = None
    # 创建时间
    create_time: Optional[datetime] = None

class MetadataQuery(PageBase):
    """
    元数据查询参数
    """
    # 主键
    id: Optional[int] = None
    # 细胞标识
    barcode: Optional[str] = None
    # 测序平台
    assay: Optional[str] = None
    # 物种
    organism: Optional[str] = None
    # 发育阶段
    development_stage: Optional[str] = None
    # 组织类型
    tissue: Optional[str] = None
    # 疾病状态
    disease: Optional[str] = None
    # 性别
    sex: Optional[str] = None
    # 细胞类型
    cell_type: Optional[str] = None
    # 细胞向量
    cell_embedding: Optional[List[float]] = None
    # 创建时间
    create_time: Optional[datetime] = None

class MetadataCreate(BaseModel):
    """
    元数据新增
    """
    # 细胞标识
    barcode: Optional[str] = None
    # 样本ID
    sample_id: Optional[str] = None
    # 测序平台
    assay: Optional[str] = None
    # 物种
    organism: Optional[str] = None
    # 发育阶段
    development_stage: Optional[str] = None
    # 组织类型
    tissue: Optional[str] = None
    # 疾病状态
    disease: Optional[str] = None
    # 性别
    sex: Optional[str] = None
    # 细胞类型
    cell_type: Optional[str] = None
    # 细胞向量
    cell_embedding: Optional[List[float]] = None
    # 错误信息
    err_msg: Optional[str] = Field(None, alias="errMsg")

class MetadataModify(BaseModel):
    """
    元数据更新
    """
    # 主键
    id: int
    # 细胞标识
    barcode: Optional[str] = None
    # 样本ID
    sample_id: Optional[str] = None
    # 测序平台
    assay: Optional[str] = None
    # 物种
    organism: Optional[str] = None
    # 发育阶段
    development_stage: Optional[str] = None
    # 组织类型
    tissue: Optional[str] = None
    # 疾病状态
    disease: Optional[str] = None
    # 性别
    sex: Optional[str] = None
    # 细胞类型
    cell_type: Optional[str] = None
    # 细胞向量
    cell_embedding: Optional[List[float]] = None

class MetadataBatchModify(BaseModel):
    """
    元数据批量更新
    """
    ids: List[int]
    # 细胞标识
    barcode: Optional[str] = None
    # 样本ID
    sample_id: Optional[str] = None
    # 测序平台
    assay: Optional[str] = None
    # 物种
    organism: Optional[str] = None
    # 发育阶段
    development_stage: Optional[str] = None
    # 组织类型
    tissue: Optional[str] = None
    # 疾病状态
    disease: Optional[str] = None
    # 性别
    sex: Optional[str] = None
    # 细胞类型
    cell_type: Optional[str] = None
    # 细胞向量
    cell_embedding: Optional[List[float]] = None

class MetadataDetail(BaseModel):
    """
    元数据详情
    """
    # 主键
    id: int
    # 细胞标识
    barcode: Optional[str] = None
    # 样本ID
    sample_id: Optional[str] = None
    # 测序平台
    assay: Optional[str] = None
    # 物种
    organism: Optional[str] = None
    # 发育阶段
    development_stage: Optional[str] = None
    # 组织类型
    tissue: Optional[str] = None
    # 疾病状态
    disease: Optional[str] = None
    # 性别
    sex: Optional[str] = None
    # 细胞类型
    cell_type: Optional[str] = None
    # 细胞向量
    cell_embedding: Optional[List[float]] = None
    # 创建时间
    create_time: Optional[datetime] = None