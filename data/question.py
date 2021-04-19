import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    variants_f = sqlalchemy.Column(sqlalchemy.String)
    variants_s = sqlalchemy.Column(sqlalchemy.String)
    variants_t = sqlalchemy.Column(sqlalchemy.String)
    variants_f = sqlalchemy.Column(sqlalchemy.String)
    image = sqlalchemy.Column(sqlalchemy.BLOB, nullable=False)
