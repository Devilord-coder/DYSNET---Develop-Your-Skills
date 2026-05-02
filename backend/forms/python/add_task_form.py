from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Optional


class TestForm(FlaskForm):
    """Форма для одного теста"""

    input_data = TextAreaField(
        "Ввод", validators=[DataRequired(message="Поле 'Ввод' обязательно")]
    )
    expected_output = TextAreaField(
        "Ожидаемый результат",
        validators=[DataRequired(message="Поле 'Ожидаемый результат' обязательно")],
    )


class AddTaskForm(FlaskForm):
    """Форма для добавления заданий с тестами"""

    name = StringField("Название задания", validators=[DataRequired()])
    text = TextAreaField("Введите суть задания", validators=[DataRequired()])

    # Динамические тесты (максимум 20)
    tests = FieldList(FormField(TestForm), min_entries=1, max_entries=20)

    submit = SubmitField("Добавить задание")

    def validate_tests(self, field):
        """Валидация: хотя бы один тест должен быть заполнен"""
        if not field.entries:
            raise ValidationError("Добавьте хотя бы один тест")

        # Проверяем, что хотя бы один тест полностью заполнен
        has_valid_test = False
        for test_form in field.entries:
            if test_form.input_data.data and test_form.expected_output.data:
                has_valid_test = True
                break

        if not has_valid_test:
            raise ValidationError(
                "Необходимо добавить хотя бы один полностью заполненный тест"
            )
