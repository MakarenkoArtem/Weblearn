import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Lesson(SqlAlchemyBase):
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    items = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    images = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
