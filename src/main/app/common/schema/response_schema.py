from typing import TypeVar, Dict, Any, Generic
from pydantic import BaseModel

T = TypeVar("T")

DEFAULT_SUCCESS_CODE: int = 0
DEFAULT_FAIL_CODE: int = -1
DEFAULT_SUCCESS_MSG: str = "success"

class HttpResponse(BaseModel, Generic[T]):
    @staticmethod
    def success(
        data: T = None,
        msg: str = DEFAULT_SUCCESS_MSG,
        code: int = DEFAULT_SUCCESS_CODE,
    ) -> Dict[str, Any]:
        """
        Generate a success response dictionary

        Args:
            data: Response data of generic model DataType
            msg: Success message
            code: Success status code

        Returns:
            Dict containing response data
        """
        response = {"code": code, "msg": msg}
        if data is not None:
            response["data"] = data
        return response

    @staticmethod
    def fail(msg: str, code: int = DEFAULT_FAIL_CODE) -> Dict[str, Any]:
        """
        Generate a failure response dictionary

        Args:
            msg: Error message
            code: Error status code

        Returns:
            Dict containing error response
        """
        return {"code": code, "msg": msg}