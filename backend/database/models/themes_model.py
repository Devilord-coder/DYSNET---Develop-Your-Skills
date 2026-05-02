import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from ..db_session import SqlAlchemyBase


class Theme(SqlAlchemyBase):
    __tablename__ = "themes"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    articles = orm.relationship("Article", back_populates="theme")