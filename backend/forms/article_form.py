from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

ARTICLE_TYPES = [
    ("", "-- Формат написания статьи --"),
    ("text", "Text"),
    ("html", "Html"),
    ("md", "Markdown")
]


class ArticleForm(FlaskForm):
    """Форма для написания статьи"""

    title = StringField("Введите название статьи", validators=[DataRequired()])
    tags = StringField("Введите теги (через запятую с пробелом)")
    type = SelectField(
        "Выберите тип статьи",
        choices=ARTICLE_TYPES,
        validators=[DataRequired()]
        )
    text = TextAreaField(
        "Введите текст статьи",
        validators=[DataRequired()]
    )
    submit = SubmitField("Опубликовать")