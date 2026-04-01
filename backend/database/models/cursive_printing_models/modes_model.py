import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class CursivePrintingModes(SqlAlchemyBase):
    """Модель таблицы режимов скоропечатания"""

    __tablename__ = "cursive_printing_modes"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    mode = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    words = orm.relationship("CursivePrintingWords", back_populates="mode_relationship")
