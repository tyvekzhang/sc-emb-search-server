"""Project health probe"""

from typing import Dict

from fastapi import APIRouter

from src.main.app.common import result

probe_router = APIRouter()


@probe_router.get("/liveness")
async def liveness() -> Dict:
    """
    Check the system's live status.

    Returns:
        dict: A status object with a 'code' and a 'msg' indicating liveness.
    """
    return result.success()
