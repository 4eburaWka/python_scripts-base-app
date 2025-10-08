import uuid
import datetime

from typing import Type, TypeVar
from types import NoneType
from pydantic import ValidationError

from sqlalchemy import UUID as BASE_UUID
from sqlalchemy.dialects.postgresql import UUID


SIMPLE_CLASSES = [bool, str, int, float, list, tuple, set, datetime.datetime, datetime.date, NoneType]


Model = TypeVar('Model')
def deserialize(model: Type[Model], json_dict) -> Model:
    try:
        row = model()
    except ValidationError:
        row = model(**json_dict)
    else:
        for k, v in json_dict.items():
            if isinstance(v, list):
                setattr(row, k, [deserialize(getattr(model, k).property.mapper.class_, x) for x in v])
            elif not any(isinstance(v, cls) for cls in SIMPLE_CLASSES):
                setattr(row, k, deserialize(getattr(model, k).property.mapper.class_, v))
            else:
                setattr(row, k, v)
    
    return row


def convert_type(value: any) -> any:
    if isinstance(value, datetime.date):
        value = value.strftime("%Y-%m-%d")
    elif isinstance(value, datetime.datetime):
        value = value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, (uuid.UUID, UUID, BASE_UUID)):
        value = str(value)
    elif isinstance(value, (list, tuple, set)):
        value = [convert_type(v) for v in value]
    elif isinstance(value, dict):
        value = {convert_type(k): convert_type(v) for k, v in value.items()}
    return value
