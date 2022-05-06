import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase):
	__tablename__ = "chats"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

	connection = orm.relation("Connection", back_populates='chat')
