from contextlib import AbstractContextManager
from typing import Any, Callable, Type, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.config import configs
from app.core.exceptions import DuplicatedError, NotFoundError
from app.model.base_model import BaseModel
from app.util.query_builder import dict_to_sqlalchemy_filter_options
from loguru import logger

T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]], model: Type[T]) -> None:
        self.session_factory = session_factory
        self.model = model

    def read_by_options(self, schema: T, eager: bool = False) -> dict:
        with self.session_factory() as session:
            logger.bind(model=self.model.__name__).debug("read_by_options start")
            schema_as_dict: dict = schema.dict(exclude_none=True)
            ordering: str = schema_as_dict.get("ordering", configs.ORDERING)
            order_query = (
                getattr(self.model, ordering[1:]).desc()
                if ordering.startswith("-")
                else getattr(self.model, ordering).asc()
            )
            page = schema_as_dict.get("page", configs.PAGE)
            page_size = schema_as_dict.get("page_size", configs.PAGE_SIZE)
            filter_options = dict_to_sqlalchemy_filter_options(self.model, schema.dict(exclude_none=True))
            query = session.query(self.model)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            filtered_query = query.filter(filter_options)
            query = filtered_query.order_by(order_query)
            if page_size == "all":
                query = query.all()
            else:
                query = query.limit(page_size).offset((page - 1) * page_size).all()
            total_count = filtered_query.count()
            result = {
                "founds": query,
                "search_options": {
                    "page": page,
                    "page_size": page_size,
                    "ordering": ordering,
                    "total_count": total_count,
                },
            }
            logger.bind(model=self.model.__name__, count=len(query)).debug("read_by_options done")
            return result

    def read_by_id(self, id: int, eager: bool = False):
        with self.session_factory() as session:
            logger.bind(model=self.model.__name__, id=id).debug("read_by_id start")
            query = session.query(self.model)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            query = query.filter(self.model.id == id).first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            logger.bind(model=self.model.__name__, id=id).debug("read_by_id done")
            return query

    def create(self, schema: T):
        with self.session_factory() as session:
            logger.bind(model=self.model.__name__).debug("create start")
            query = self.model(**schema.dict())
            try:
                session.add(query)
                session.commit()
                session.refresh(query)
            except IntegrityError as e:
                logger.exception("create failed due to integrity error")
                raise DuplicatedError(detail=str(e.orig))
            logger.bind(model=self.model.__name__, id=query.id).debug("create done")
            return query

    def update(self, id: int, schema: T):
        with self.session_factory() as session:
            logger.bind(model=self.model.__name__, id=id).debug("update start")
            session.query(self.model).filter(self.model.id == id).update(schema.dict(exclude_none=True))
            session.commit()
            result = self.read_by_id(id)
            logger.bind(model=self.model.__name__, id=id).debug("update done")
            return result

    def update_attr(self, id: int, column: str, value: Any):
        with self.session_factory() as session:
            logger.bind(model=self.model.__name__, id=id, column=column).debug("update_attr start")
            session.query(self.model).filter(self.model.id == id).update({column: value})
            session.commit()
            result = self.read_by_id(id)
            logger.bind(model=self.model.__name__, id=id, column=column).debug("update_attr done")
            return result

    def whole_update(self, id: int, schema: T):
        with self.session_factory() as session:
            logger.bind(model=self.model.__name__, id=id).debug("whole_update start")
            session.query(self.model).filter(self.model.id == id).update(schema.dict())
            session.commit()
            result = self.read_by_id(id)
            logger.bind(model=self.model.__name__, id=id).debug("whole_update done")
            return result

    def delete_by_id(self, id: int):
        with self.session_factory() as session:
            logger.bind(model=self.model.__name__, id=id).debug("delete_by_id start")
            query = session.query(self.model).filter(self.model.id == id).first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            session.delete(query)
            session.commit()
            logger.bind(model=self.model.__name__, id=id).debug("delete_by_id done")

    def close_scoped_session(self):
        with self.session_factory() as session:
            return session.close()
