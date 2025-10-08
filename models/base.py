import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column

from utils.json import convert_type


class Base(DeclarativeBase):
    id: MappedColumn[str] = mapped_column(UUID(as_uuid=False), primary_key=True)        

    def model_dump(self, _parents_tablenames: list[str] = None, **kwargs):
        if _parents_tablenames is None:
            _parents_tablenames = []
        parent_tables = _parents_tablenames.copy() + [self.__tablename__]

        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            data[column.name] = convert_type(value)

        for rs in self.__mapper__.relationships.keys():
            if rs in _parents_tablenames:
                continue

            is_list = self.__mapper__.relationships[rs].uselist
            attr = getattr(self, rs)
            if is_list:
                if attr:
                    data[rs] = tuple(
                        model.model_dump(_parents_tablenames=parent_tables) for model in attr
                    )
            else:
                data[rs] = attr.model_dump(_parents_tablenames=parent_tables)

        if data.get("id") is None:
            data["id"] = uuid.uuid4()
        data["id"] = str(data["id"])

        return data
