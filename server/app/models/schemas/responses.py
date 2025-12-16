from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    status: Literal["success", "error"]
    code: str
    message: str
    data: Optional[T] = None
