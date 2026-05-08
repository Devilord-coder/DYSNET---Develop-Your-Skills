from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from flask_wtf.file import FileAllowed
from wtforms import SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    """Форма добавления новостей"""

    title = StringField("Заголовок", validators=[DataRequired()])
    content = TextAreaField("Содержание")
    image = FileField(
        "Изображение", validators=[FileAllowed(["jpg", "png", "jpeg", "gif"])]
    )
    submit = SubmitField("Применить")
