import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class ClickerStatistics(SqlAlchemyBase):
    """Модель таблицы статистики кликера"""

    __tablename__ = "clicker_statistics"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    datetime = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    quantity_correct_answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
        nullable=False,
    )
    user_relationship = orm.relationship("User", back_populates="clicker_statistics")
