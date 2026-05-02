import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from ..db_session import SqlAlchemyBase

ARTICLE_TYPES = [
    "text",
    "html",
    "md"
]


class Article(SqlAlchemyBase):
    """Таблица для статей"""

    __tablename__ = "articles"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)
    theme_id = sa.Column(sa.Integer, sa.ForeignKey("themes.id"))
    theme = orm.relationship("Theme", back_populates="articles")
    tags = sa.Column(sa.String)
    created_date = sa.Column(sa.DateTime, default=datetime.datetime.now,
                             nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    author = orm.relationship("User", back_populates="articles")
    type = sa.Column(sa.String, default=ARTICLE_TYPES[0])
    text = sa.Column(sa.String, nullable=False)