import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Test(SqlAlchemyBase):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    questions = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    #modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
