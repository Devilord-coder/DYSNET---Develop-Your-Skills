from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class CodeForm(FlaskForm):
    code = TextAreaField('Код решения', validators=[
        DataRequired(message='Поле с кодом не может быть пустым')])