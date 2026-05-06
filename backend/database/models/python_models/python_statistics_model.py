from ...db_session import SqlAlchemyBase
import sqlalchemy as sa
from sqlalchemy import orm
from datetime import datetime


class PythonStatistics(SqlAlchemyBase):
    __tablename__ = "python_statistics"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    datetime = sa.Column(sa.DateTime, default=datetime.now)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    user = orm.relationship("User", back_populates="python_statistics")
    task_id = sa.Column(sa.String, sa.ForeignKey('python_tasks.id'))
    task = orm.relationship("PythonTask", back_populates='answers')
    status = sa.Column(sa.Boolean, nullable=False)
    code = sa.Column(sa.String, nullable=False)
    tests_json = sa.Column(sa.String, nullable=False)