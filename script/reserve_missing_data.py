from sqlmodel import create_engine, SQLModel, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import pandas as pd
from typing import List
import asyncio

from src.main.app.model.sample_model import SampleDO


async def delete_missing_samples():
    # 1. 创建异步数据库引擎
    database_url = "postgresql+asyncpg://postgres:123456@172.21.14.53:5433/postgres"
    engine = create_async_engine(database_url)

    # 2. 读取Excel文件获取需要保留的sample_id列表
    excel_path = r"D:\Container\Download\Fdm\built-in.csv"
    df = pd.read_csv(excel_path)
    keep_sample_ids: List[int] = df["sample_id"].tolist()

    print(f"找到 {len(keep_sample_ids)} 个需要保留的样本ID")

    # 3. 删除数据库中不在keep_sample_ids列表中的样本
    async with AsyncSession(engine) as session:
        # 查询不在keep_sample_ids列表中的样本
        stmt = select(SampleDO).where(SampleDO.sample_id.not_in(keep_sample_ids))
        result = await session.execute(stmt)
        samples_to_delete = result.scalars().all()

        if samples_to_delete:
            for sample in samples_to_delete:
                await session.delete(sample)
            await session.commit()
            print(f"成功删除 {len(samples_to_delete)} 条不在Excel中的记录")
        else:
            print("所有数据库记录都在Excel中，无需删除")

# 运行异步函数
asyncio.run(delete_missing_samples())