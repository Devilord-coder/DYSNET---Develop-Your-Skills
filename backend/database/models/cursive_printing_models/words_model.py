import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class CursivePrintingWords(SqlAlchemyBase):
    """Модель таблицы слов для скоропечатания"""

    __tablename__ = "cursive_printing_words"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    mode = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("cursive_printing_modes.id"),
        nullable=False,
    )
    mode_relationship = orm.relationship("CursivePrintingModes", back_populates="words")
