#!/usr/bin/env python

#   Demo for fast-api with CRUD for all table auto generation    
#   Run app with "uvicorn auto-crud-demo:app --reload"

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi_crudrouter import DatabasesCRUDRouter, SQLAlchemyCRUDRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import Session, query, mapper, sessionmaker
from sqlalchemy.sql.expression import *
from sqlalchemy import or_, and_, text

from contextlib import contextmanager
from loguru import logger
import os
from models import *


@contextmanager
def session_scope(session: Session):
    """Provide a transactional scope around a series of operations."""
    tx = session.transaction
    # logger.info(dir(session))
    logger.info('start transaction ' + str(id(tx)) + ' on connection ' + str(
        id(tx.connection)))
    try:
        yield session
        session.commit()
        logger.info('commit transaction ' + str(id(tx)))
    except Exception as err:
        session.rollback()
        logger.info('rollback transaction ' + str(id(tx)))
        raise err
    finally:
        pass


def db_init(host="127.0.0.1", port="3306", username="root", password="",
            database=""):
    """
        for engine creation, refer http://docs.sqlalchemy.org/en/latest/core/engines.html
        max_overflow=10,  # 超过连接池大小外最多创建的连接
        pool_size=5,  # 连接池大小
        pool_timeout=10,  # 池中没有线程最多等待的时间，否则报错
        pool_recycle=600 # 多久之后对线程池中的线程进行一次连接的回收（重置）
    """
    engine = sqlalchemy.create_engine(
        f'mysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4',
        echo=False, isolation_level='READ_COMMITTED',
        max_overflow=10,
        pool_size=5,
        pool_timeout=10,
        pool_recycle=600)
    metadata = sqlalchemy.MetaData(engine)
    metadata.reflect(bind=engine)
    return engine, metadata


def get_session(engine) -> Session:
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    return Session()


def create_app():
    engine, metadata =  db_init(password="lt7116", database="ppds")    
    app = FastAPI()
    l_dict = globals()
    l = [k for k in l_dict.keys() if k != 'l_dict' and callable(l_dict[k]) and hasattr(l_dict[k], '__tablename__')]
    def router_session():
        session = get_session(engine)
        tx = session.transaction
        # logger.info(dir(session))
        logger.info('start transaction ' + str(id(tx)) + ' on connection ' + str(
            id(tx.connection)))
        try:
            yield session
            session.commit()
            logger.info('commit transaction ' + str(id(tx)))
        except Exception as err:
            session.rollback()
            logger.info('rollback transaction ' + str(id(tx)))
            raise err
        finally:
            session.close()        
    for k in l:
        router = SQLAlchemyCRUDRouter(
            schema=sqlalchemy_to_pydantic(l_dict[k]),
            db_model=l_dict[k],
            paginate=20,
            db=router_session,            
        )
        print(f'add router for {k}')
        app.include_router(router)
    return app


app = create_app()


def test_query(db_session: Session) -> None:
    with session_scope(db_session) as session:
        rs = session.execute("""
            select id, column_code, column_name, column_is_optional, 
            column_is_term_definition from provision_columns
        """)
        rs_list = rs.fetchall()
        # print(rs_list)
        for r in rs_list:
            print(r)
        rs.close()


def reflect_column(c: sqlalchemy.sql.schema.Column,
                   session: sqlalchemy.orm.Session):
    print('---------', c, c.foreign_keys, c.primary_key, c.default, c.index,
          c.server_default)
    print('desc=', c.desc)
    print('description=', c.description)
    print('comment=', c.comment)
    print('doc=', c.doc)
    print('expression=', c.expression)        


def reflect_table(table: sqlalchemy.sql.schema.Table,
                  session: sqlalchemy.orm.Session):
    print("##########", type(table), table, session.query(table).count())
    for c in table.columns:
        reflect_column(c, session)


def reflect_db(metadata, session):
    # do database inspection    
    for table_name in metadata.tables:
        print(type(table_name), table_name)
        table = metadata.tables[table_name]
        reflect_table(table, session)


if __name__ == '__main__':
    # disclaimer()
    engine, metadata = db_init(username="root", password="lt7116", database="ppds")
    test_query(get_session(engine))
    reflect_db(metadata, get_session(engine))

