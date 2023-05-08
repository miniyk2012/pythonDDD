# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

import abc
import contextlib
from typing import ContextManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config
from allocation.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    # should this class contain __enter__ and __exit__?
    # or should the context manager and the UoW be separate?
    # up to you!
    batches: repository.AbstractRepository

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session):
        self.session = session
        self.batches = repository.SqlAlchemyRepository(self.session)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()


# One alternative would be to define a `start_uow` function,
# or a UnitOfWorkStarter or UnitOfWorkManager that does the
# job of context manager, leaving the UoW as a separate class
# that's returned by the context manager's __enter__.
#
# A type like this could work?
# AbstractUnitOfWorkStarter = ContextManager[AbstractUnitOfWork]


@contextlib.contextmanager
def start(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory())
    try:
        yield uow
    finally:
        uow.rollback()
        uow.session.close()

