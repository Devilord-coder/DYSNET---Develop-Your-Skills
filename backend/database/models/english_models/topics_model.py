import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class EnglishTopics(SqlAlchemyBase):
    """Модель таблицы тем английских слов"""

    __tablename__ = "english_topics"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    words = orm.relationship("EnglishWords", back_populates="topic_relationship")
