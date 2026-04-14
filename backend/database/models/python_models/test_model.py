from ...db_session import SqlAlchemyBase
import sqlalchemy as sa
from sqlalchemy import orm


class PythonTest(SqlAlchemyBase):
    """Модель для теста программы на Python"""

    __tablename__ = "python_tests"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    # id задания
    task_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("python_tasks.id"),
        nullable=False
    )
    args = sa.Column(sa.String)
    result = sa.Column(sa.String)
    # связь с заданиями
    task = orm.relationship("PythonTask", back_populates="tests")