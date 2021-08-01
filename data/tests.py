import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Test(SqlAlchemyBase, UserMixin):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    questions = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)
