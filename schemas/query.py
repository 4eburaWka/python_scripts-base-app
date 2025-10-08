from enum import StrEnum
from pydantic import BaseModel, Field


class OrderDir(StrEnum):
    asc = "asc"
    desc = "desc"


class Query(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=10, le=1000)
    order_by: str = Field(default="")
    order_dir: OrderDir = Field(default=OrderDir.asc)
    search: str = Field(default="")
