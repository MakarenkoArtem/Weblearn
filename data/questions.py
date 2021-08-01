import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String)
    variants_f = sqlalchemy.Column(sqlalchemy.String)
    variants_s = sqlalchemy.Column(sqlalchemy.String)
    variants_t = sqlalchemy.Column(sqlalchemy.String)
    variants_fo = sqlalchemy.Column(sqlalchemy.String)
    right = sqlalchemy.Column(sqlalchemy.Integer)
    image = sqlalchemy.Column(sqlalchemy.LargeBinary)
