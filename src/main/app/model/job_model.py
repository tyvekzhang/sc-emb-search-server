"""Job data object"""

from datetime import datetime
from typing import Optional
from sqlmodel import (
    SQLModel,
    Field,
    Column,
    BigInteger,
    String,
    Integer,
    DateTime,
)
from src.main.app.common.util.snowflake_util import snowflake_id


class JobBase(SQLModel):
    
    id: int = Field(
        default_factory=snowflake_id,
        primary_key=True,
        sa_type=BigInteger,
        sa_column_kwargs={"comment": "主键"},
    )
    job_name: Optional[str] = Field(
        sa_column=Column(
            String(32),
            nullable=True,
            default=None,
            comment="任务名称"
        )
    )
    parent_job_id: Optional[str] = Field(
        sa_column=Column(
            String(32),
            nullable=True,
            default=None,
            comment="父任务号"
        )
    )
    status: Optional[int] = Field(
        sa_column=Column(
            Integer,
            nullable=True,
            default=None,
            comment="状态"
        )
    )
    comment: Optional[str] = Field(
        sa_column=Column(
            String(255),
            nullable=True,
            default=None,
            comment="描述"
        )
    )
    creat_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=True,
            default=None,
            comment="创建时间"
        )
    )
    update_time: Optional[datetime] = Field(
        sa_type=DateTime,
        default_factory=datetime.now,
        sa_column_kwargs={
            "onupdate": datetime.now,
            "comment": "更新时间",
        },
    )


class JobDO(JobBase, table=True):
    __tablename__ = "job"
    __table_args__ = (
        {"comment": "任务表"}
    )