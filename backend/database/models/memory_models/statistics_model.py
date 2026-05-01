import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class MemoryStatistics(SqlAlchemyBase):
    '''Модель таблицы статистики памяти'''
    __tablename__ = "memory_statistics"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    grid_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    moves = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    found_pairs = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False
    )

    user_relationship = orm.relationship("User", back_populates="memory_statistics")
