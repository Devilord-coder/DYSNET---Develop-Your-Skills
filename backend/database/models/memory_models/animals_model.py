import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class Animals(SqlAlchemyBase):
    """Модель таблицы животных"""

    __tablename__ = "animals"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    emoji = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
