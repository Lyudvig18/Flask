import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Messages(SqlAlchemyBase):
	__tablename__ = "messages"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	message = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	room = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
	created_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

	user = orm.relation("User")