from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired


class EditProfileForm(FlaskForm):
    """Форма для изменения профиля"""

    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    aboutme = TextAreaField("Расскажите о себе", validators=[DataRequired()])
    submit = SubmitField("Сохранить")