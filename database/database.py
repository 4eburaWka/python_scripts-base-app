import asyncio
import logging

from sqlalchemy import Select, asc, desc, or_, text
from sqlalchemy.dialects.postgresql import insert as _insert
from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import MappedColumn
from typing import AsyncGenerator, Type, TypeVar

from configs import config
from configs.constants import LOCAL_ENV
from schemas.query import Query, OrderDir


def get_engine(url: str) -> AsyncEngine:
    return create_async_engine(url=url, echo=config.ENV == LOCAL_ENV, pool_size=50, max_overflow=100)


def get_sessionmaker(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)


engine = get_engine(config.DB_URL)
async_session = get_sessionmaker(engine)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session.begin() as sess:
        yield sess


def process_select_query(
    db_query: Select, query: Query, search_by_columns: list[MappedColumn]
) -> Select:
    order_dir_func = asc if query.order_dir == OrderDir.asc else desc
    
    db_query = (
        db_query.offset((query.page - 1) * query.limit)
        .limit(query.limit)
    )
    if query.search:
        search_conds = []
        for column in search_by_columns:
            search_conds.append(column.ilike(f"{query.search}%"))
        db_query = db_query.filter(or_(*search_conds))

    if query.order_by:
        db_query = db_query.order_by(order_dir_func(text(query.order_by)))

    return db_query


PSQL_QUERY_ALLOWED_MAX_ARGS = 32767


Model = TypeVar('T')
async def pg_bulk_insert(
    session: AsyncSession, 
    table: Type[Model],
    data: list[Model], 
    statement_modifier: function = None,
):

    if statement_modifier is None:
        statement_modifier = lambda q: q

    complete_batches = []

    current_batch = []
    current_count = 0
    for row in data:
        params_count = len(row)
        current_count += params_count
        if current_count >= PSQL_QUERY_ALLOWED_MAX_ARGS:
            complete_batches.append(current_batch)
            current_batch = [row]
            current_count = params_count
        else:
            current_batch.append(row)
    if len(current_batch) > 0:
        complete_batches.append(current_batch)

    for batch in complete_batches:
        statement = statement_modifier(
            _insert(table)
            .values(batch)
        )
        await session.execute(statement)


def retry_on_failure(
    max_retries=2, retry_exceptions=(InterfaceError, OperationalError), delay=1
):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except retry_exceptions as e:
                    retries += 1
                    logging.warning(f"Retry {retries}/{max_retries} due to error: {e}")
                    await asyncio.sleep(delay)
            raise Exception(f"Failed after {max_retries} retries")

        return wrapper

    return decorator
