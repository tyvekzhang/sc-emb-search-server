"""Sample mapper"""
from typing import Union

from src.main.app.mapper.mapper_base_impl import SqlModelMapper
from src.main.app.model.sample_model import SampleDO
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


class SampleMapper(SqlModelMapper[SampleDO]):
    async def fetch_all_sample_by_species(self, species: str, db_session: Union[AsyncSession, None] = None):
        db_session = db_session or self.db.session
        statement = select(SampleDO.id, SampleDO.sample_id, SampleDO.tissue).where(SampleDO.species == species)
        db_response = await db_session.exec(statement)
        return db_response.all()


sampleMapper = SampleMapper(SampleDO)