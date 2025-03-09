"""JobResult mapper"""

from src.main.app.mapper.mapper_base_impl import SqlModelMapper
from src.main.app.model.job_result_model import JobResultDO


class JobResultMapper(SqlModelMapper[JobResultDO]):
    pass


jobResultMapper = JobResultMapper(JobResultDO)