import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Connection(SqlAlchemyBase):
	__tablename__ = "connection"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	id_chat = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("chats.id"), nullable=True)
	created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
	id_user = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"), nullable=True)

	user = orm.relation('User')
	chat = orm.relation('Chats')

