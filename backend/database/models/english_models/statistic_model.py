import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class EnglishStatistics(SqlAlchemyBase):
    """Модель таблицы статистики английских навыков"""

    __tablename__ = "english_statistics"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    quantity_correct_answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    english_word = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    russian_word = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    language = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    skill = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
        nullable=False,
    )
    user_relationship = orm.relationship("User", back_populates="english_statistics")
