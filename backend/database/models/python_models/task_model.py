from ...db_session import SqlAlchemyBase
import sqlalchemy as sa
from sqlalchemy import orm


class PythonTask(SqlAlchemyBase):
    """Модель для заданий по Python"""

    __tablename__ = "python_tasks"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    task_type = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=False)
    tests = orm.relationship("PythonTest", back_populates="task")
