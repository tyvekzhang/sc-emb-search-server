import asyncio
from typing import List

from sqlmodel import SQLModel, select, insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.main.app.model.sample_model import SampleDO

# 数据库连接配置
MYSQL_URL = "mysql+aiomysql://root:123456@localhost:3306/sc-emb-search"
PGSQL_URL = "postgresql+asyncpg://postgres:123456@172.21.14.53:5433/postgres"

def chunked(data: List, size: int):
    for i in range(0, len(data), size):
        yield data[i:i + size]


async def migrate_data():
    # 创建引擎
    mysql_engine = create_async_engine(MYSQL_URL, echo=True)
    pgsql_engine = create_async_engine(PGSQL_URL, echo=True)

    # 在PostgreSQL中创建表
    async with pgsql_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # 从MySQL读取数据
    async with AsyncSession(mysql_engine) as mysql_session:
        result = await mysql_session.exec(select(SampleDO))
        samples: List[SampleDO] = result.all()

        # 写入PostgreSQL
    async with AsyncSession(pgsql_engine) as pgsql_session:
        for batch in chunked(samples, 100):
            statement = insert(SampleDO).values(
                [data.dict() for data in batch]  # 或 model_dump()
            )
            await pgsql_session.exec(statement)
            await pgsql_session.commit()

    print(f"成功迁移 {len(samples)} 条记录")

if __name__ == "__main__":
    asyncio.run(migrate_data())