from sqlmodel import create_engine, SQLModel, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import pandas as pd
from typing import List
import asyncio

from src.main.app.model.sample_model import SampleDO


# 异步数据库操作
async def delete_missing_samples():
    # 1. 创建异步数据库引擎
    database_url = "postgresql+asyncpg://postgres:123456@172.21.14.53:5433/postgres"
    engine = create_async_engine(database_url)

    # 2. 读取Excel文件获取缺失样本ID
    excel_path = r"C:\Users\ZJ\Desktop\missing_samples.xlsx"
    df = pd.read_excel(excel_path)
    missing_sample_ids: List[int] = df["missing_sample_id"].tolist()

    print(f"找到 {len(missing_sample_ids)} 个需要删除的样本ID")

    # 3. 删除数据库中存在的这些样本
    async with AsyncSession(engine) as session:
        # 批量删除
        stmt = select(SampleDO).where(SampleDO.sample_id.in_(missing_sample_ids))
        result = await session.execute(stmt)
        samples_to_delete = result.scalars().all()

        if samples_to_delete:
            for sample in samples_to_delete:
                await session.delete(sample)
            await session.commit()
            print(f"成功删除 {len(samples_to_delete)} 条记录")
        else:
            print("没有找到匹配的记录需要删除")

# 运行异步函数
asyncio.run(delete_missing_samples())