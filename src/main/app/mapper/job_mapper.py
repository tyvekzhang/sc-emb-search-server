"""Job mapper"""

from src.main.app.mapper.mapper_base_impl import SqlModelMapper
from src.main.app.model.job_model import JobDO


class JobMapper(SqlModelMapper[JobDO]):
    pass


jobMapper = JobMapper(JobDO)