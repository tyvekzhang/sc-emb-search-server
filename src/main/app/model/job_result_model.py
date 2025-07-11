"""JobResult data object"""

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


class JobResultBase(SQLModel):
    
    id: int = Field(
        default_factory=snowflake_id,
        primary_key=True,
        sa_type=BigInteger,
        sa_column_kwargs={"comment": "主键"},
    )
    job_id: Optional[int] = Field(
        sa_column=Column(
            BigInteger,
            nullable=True,
            default=None,
            comment="任务Id"
        )
    )
    file_id: Optional[int] = Field(
        sa_column=Column(
            BigInteger,
            nullable=True,
            default=None,
            comment="文件Id"
        )
    )
    result_key: Optional[str] = Field(
        sa_column=Column(
            String(64),
            nullable=True,
            default=None,
            comment="关键字"
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


class JobResultDO(JobResultBase, table=True):
    __tablename__ = "job_result"
    __table_args__ = (
        {"comment": "任务结果表"}
    )