import sqlalchemy
from sqlalchemy import orm
from ...db_session import SqlAlchemyBase


class EnglishWords(SqlAlchemyBase):
    """Модель таблицы слов для английских навыков"""

    __tablename__ = "english_words"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    russian_word = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    english_word = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    topic = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("english_topics.id"),
        nullable=False,
    )
    topic_relationship = orm.relationship("EnglishTopics", back_populates="words")
