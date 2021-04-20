import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Lesson(SqlAlchemyBase):
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    items = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    top_image = sqlalchemy.Column(sqlalchemy.BLOB, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    images = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    #modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
