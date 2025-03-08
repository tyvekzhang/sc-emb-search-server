"""Sample data object"""

from datetime import datetime
from typing import Optional
from sqlmodel import (
    SQLModel,
    Field,
    Column,
    BigInteger,
    DateTime,
    String,
    Integer,
)
from src.main.app.common.util.snowflake_util import snowflake_id


class SampleBase(SQLModel):
    
    id: int = Field(
        default_factory=snowflake_id,
        primary_key=True,
        sa_type=BigInteger,
        sa_column_kwargs={"comment": "主键"},
    )
    species: Optional[str] = Field(
        sa_column=Column(
            String(64),
            nullable=True,
            default=None,
            comment="物种"
        )
    )
    sample_id: Optional[str] = Field(
        sa_column=Column(
            String(64),
            nullable=True,
            default=None,
            comment="样本名"
        )
    )
    project_id: Optional[str] = Field(
        sa_column=Column(
            String(64),
            nullable=True,
            default=None,
            comment="项目名"
        )
    )
    tissue: Optional[str] = Field(
        sa_column=Column(
            String(64),
            nullable=True,
            default=None,
            comment="组织、器官"
        )
    )
    cell_count: Optional[int] = Field(
        sa_column=Column(
            Integer,
            nullable=True,
            default=None,
            comment="细胞数"
        )
    )
    project_title: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="项目标题"
        )
    )
    project_summary: Optional[str] = Field(
        sa_column=Column(
            String(1024),
            nullable=True,
            default=None,
            comment="项目总结"
        )
    )
    platform: Optional[str] = Field(
        sa_column=Column(
            String(64),
            nullable=True,
            default=None,
            comment="测序平台"
        )
    )
    ext: Optional[str] = Field(
        sa_column=Column(
            String(1024),
            nullable=True,
            default=None,
            comment="扩展字段"
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


class SampleDO(SampleBase, table=True):
    __tablename__ = "sample"
    __table_args__ = (
        {"comment": "样本表"}
    )