from datetime import datetime
from typing import Optional
from sqlmodel import (
    SQLModel,
    Field,
    Column,
    BigInteger,
    String,
    DateTime,
)
from pgvector.sqlalchemy import Vector
from src.main.app.common.util.snowflake_util import snowflake_id


class MetadataBase(SQLModel):
    id: int = Field(
        default_factory=snowflake_id,
        primary_key=True,
        sa_type=BigInteger,
        sa_column_kwargs={"comment": "主键"},
    )
    barcode: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="细胞标识"
        )
    )

    sample_id: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="样本ID"
        )
    )

    assay: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="测序平台"
        )
    )

    organism: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="物种"
        )
    )

    development_stage: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="发育阶段"
        )
    )

    tissue: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="组织类型"
        )
    )

    disease: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="疾病状态"
        )
    )

    sex: Optional[str] = Field(
        sa_column=Column(
            String(50),
            nullable=True,
            default=None,
            comment="性别"
        )
    )

    cell_type: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="细胞类型"
        )
    )

    # 使用 pgvector 存储 cell_embedding 向量
    cell_embedding: Optional[list[float]] = Field(
        sa_column=Column(
            Vector(512),
            nullable=True,
            default=None,
            comment="细胞向量"
        )
    )

    create_time: Optional[datetime] = Field(
        sa_type=DateTime,
        default_factory=datetime.now,
        sa_column_kwargs={"comment": "创建时间"},
    )

    update_time: Optional[datetime] = Field(
        sa_type=DateTime,
        default_factory=datetime.now,
        sa_column_kwargs={
            "onupdate": datetime.now,
            "comment": "更新时间",
        },
    )


class MetadataEntity(MetadataBase, table=True):
    __tablename__ = "metadata"
    __table_args__ = (
        {"comment": "元数据表"}
    )