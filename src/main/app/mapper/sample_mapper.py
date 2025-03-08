"""Sample mapper"""

from src.main.app.mapper.mapper_base_impl import SqlModelMapper
from src.main.app.model.sample_model import SampleDO


class SampleMapper(SqlModelMapper[SampleDO]):
    pass


sampleMapper = SampleMapper(SampleDO)