import datetime
import uuid

from sqlalchemy import VARCHAR, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


class Base(DeclarativeBase):
    id: MappedColumn[str] = mapped_column(UUID(as_uuid=False), primary_key=True)

    def model_dump(self, convert_types: bool = True, _parents_tablenames: list[str] = None):
        if _parents_tablenames is None:
            _parents_tablenames = []
        _parents_tablenames.append(self.__tablename__)

        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if convert_types:
                if isinstance(value, datetime.date):
                    value = str(value)
            data[column.name] = value

        for rs in self.__mapper__.relationships.keys():
            if rs in _parents_tablenames:
                continue

            is_list = self.__mapper__.relationships[rs].uselist
            if is_list:
                if convert_types or getattr(self, rs):
                    data[rs] = tuple(
                        model.model_dump(_parents_tablenames=_parents_tablenames) for model in getattr(self, rs)
                    )
            else:
                data[rs] = getattr(self, rs).model_dump(_parents_tablenames=_parents_tablenames)

        if data.get("id") is None:
            data["id"] = uuid.uuid4()
        data["id"] = str(data["id"])

        return data
