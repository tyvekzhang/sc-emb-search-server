import asyncio
import os

import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.main.app.model.metadata_model import MetadataEntity

# 数据库配置
DATABASE_URL = "postgresql+asyncpg://postgres:123456@172.21.14.53:5433/postgres"
engine = create_async_engine(DATABASE_URL)



async def process_files(embedding_file: str, metadata_file: str, batch_size: int = 1000):
    """
    处理两个Excel文件并将数据存入数据库

    Args:
        embedding_file: 包含细胞嵌入的文件路径
        metadata_file: 包含元数据的文件路径
        batch_size: 批量插入的大小
    """
    # 读取细胞嵌入数据
    print(f"正在读取细胞嵌入文件: {embedding_file}")
    embedding_df = pd.read_csv(embedding_file)

    # 提取barcode和嵌入向量
    # 创建一个空字典
    barcode_vector_dict = {}

    # 遍历DataFrame的每一行
    for index, row in embedding_df.iterrows():
        barcode = row['barcode']
        # 提取512维度的向量（从列0到511）
        vector = row[list(range(512))].values.tolist()
        barcode_vector_dict[barcode] = vector

    # 读取元数据
    print(f"正在读取元数据文件: {metadata_file}")
    metadata_df = pd.read_excel(metadata_file, index_col=0)
    total = len(embedding_df)
    i = 0

    # 批量插入数据
    print("开始批量插入数据...")
    async with AsyncSession(engine) as session:
        records = []
        for barcode, row in metadata_df.iterrows():
            if barcode not in barcode_vector_dict:
                continue
            i = i + 1
            record = MetadataEntity(
                barcode=barcode,
                cell_embedding=barcode_vector_dict[barcode],
                sample_id=row.get('sample_id'),
                assay=row.get('assay'),
                organism=row.get('organism'),
                development_stage=row.get('development_stage'),
                tissue=row.get('tissue'),
                disease=row.get('disease'),
                sex=row.get('sex'),
                cell_type=row.get('cell_type')
            )
            records.append(record)

        session.add_all(records)
        await session.commit()


    print(f"数据处理完成，共插入 {i}/{total} 条记录。")

if __name__ == "__main__":
    # 文件路径配置
    embedding_file = r"D:\Container\Download\Fdm\embedding\20250627TghAfjMr.csv"
    metadata_file = r"D:\Container\Download\Fdm\obs_excel\6f41ade2-3654-4589-abb7-35cd803472dc.xlsx"

    # 检查文件是否存在
    if not os.path.exists(embedding_file):
        raise FileNotFoundError(f"细胞嵌入文件 {embedding_file} 不存在")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"元数据文件 {metadata_file} 不存在")

    # 处理文件
    asyncio.run(process_files(embedding_file, metadata_file))