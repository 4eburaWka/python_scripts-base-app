import datetime

from sqlalchemy import VARCHAR, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


class Base(DeclarativeBase):
    id: MappedColumn[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
