import sqlalchemy
from ...db_session import SqlAlchemyBase


class EnglishTexts(SqlAlchemyBase):
    """Модель таблицы английских текстов"""

    __tablename__ = "english_texts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    answers = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
