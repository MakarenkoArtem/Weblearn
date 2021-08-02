import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import os
SqlAlchemyBase = dec.declarative_base()

__factory = None

def global_init():
    global __factory

    if __factory:
        return

    # if not db_file or not db_file.strip():
    #     raise Exception("Необходимо указать файл базы данных.")
    if 'HEROKU_POSTGRESQL_ONYX_URL' in os.environ:
        conn_str = os.environ['HEROKU_POSTGRESQL_ONYX_URL'].replace('postgres://', 'postgresql://')  # сработает на Heroku
    elif 'DATABASE_URL' in os.environ:
        conn_str = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://')  # сработает на Heroku
    else:
        from config import LOCAL_DB, DB  # сработает локально
        conn_str = LOCAL_DB
        #conn_str = DB.replace('postgres://', 'postgresql://')
    print(conn_str)
    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)

def create_session() -> Session:
    global __factory
    return __factory()