from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired


class EditProfileForm(FlaskForm):
    """Форма для изменения профиля"""

    avatar = FileField(
        "Загрузите картинку",
        validators=[
            FileAllowed(
                ["jpg", "png", "jpeg", "gif", "ico"], message="Только изображения!"
            )
        ],
    )
    name = StringField("Имя")
    surname = StringField("Фамилия")
    aboutme = TextAreaField("Расскажите о себе")
    submit = SubmitField("Сохранить")
