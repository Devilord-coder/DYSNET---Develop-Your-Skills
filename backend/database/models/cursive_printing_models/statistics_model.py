import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class CursivePrintingStatistics(SqlAlchemyBase):
    """Модель таблицы статистики скоропечатания"""

    __tablename__ = "cursive_printing_statistics"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    datetime = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    training_time = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    quantity_symbols = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    speed = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    quantity_errors = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    language = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    mode = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
        nullable=False,
    )
    user_relationship = orm.relationship(
        "User", back_populates="cursive_printing_statistics"
    )
