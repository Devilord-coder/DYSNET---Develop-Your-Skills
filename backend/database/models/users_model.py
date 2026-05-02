import datetime
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    """Модель таблицы пользователей"""

    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(
        sqlalchemy.String, index=True, unique=True, nullable=False
    )
    aboutme = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="user")
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    confirmation_token = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    reset_token = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    reset_token_expires = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)

    cursive_printing_statistics = orm.relationship(
        "CursivePrintingStatistics", back_populates="user_relationship"
    )
    english_statistics = orm.relationship(
        "EnglishStatistics", back_populates="user_relationship"
    )
    clicker_statistics = orm.relationship(
        "ClickerStatistics", back_populates="user_relationship"
    )
    memory_statistics = orm.relationship(
        "MemoryStatistics", back_populates="user_relationship"
    )
    news = orm.relationship("News", back_populates="author")

    def set_password(self, password):
        """Создание пароля"""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Проверка равенства паролей"""
        return check_password_hash(self.hashed_password, password)

    def set_avatar(self, avatar_path: str):
        """Изменение аватара"""
        self.avatar = avatar_path

    def set_name(self, name: str):
        """Изменение имени"""
        self.name = name

    def set_surname(self, surname: str):
        """Изменение фамилии"""
        self.surname = surname

    def set_aboutme(self, aboutme: str):
        """Изменение раздела о себе"""
        self.aboutme = aboutme
