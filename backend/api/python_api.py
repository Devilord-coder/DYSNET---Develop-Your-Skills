from flask import Blueprint, render_template, request, redirect, session
from flask_wtf.csrf import generate_csrf
# Формы
from backend.forms import AddTaskForm
# БД
from backend.database.__all_models import PythonTask, PythonTest
from backend.database import db_session

# Отдельная ветка
bp = Blueprint("python", __name__, template_folder="templates")

@bp.route("/choose_level")
def choose_level():
    """Выбор уровня сложности"""

    return render_template("python/choose_level.html", title="Выбор режима")


@bp.route("/tasks", methods=["POST", "GET"])
def tasks():
    """Просмотр заданий"""

    if request.method == "POST":
        level = request.form.get("level")
        session['level'] = level
        print(session['level'])

    ...

    return render_template(
        "python/tasks.html"
    )


@bp.route("/tasks/add", methods=['GET', 'POST'])
def add_task():
    """Добавление заданий"""

    form = AddTaskForm()
    db_sess = db_session.create_session()

    # При GET-запросе добавляем один пустой тест
    if request.method == 'GET' and len(form.tests) == 0:
        form.tests.append_entry()

    if form.validate_on_submit():
        # Сохраняем задание
        task = PythonTask(
            name=form.name.data,
            task_type=session['level'],
            text=form.text.data
        )
        db_sess.add(task)

        # Сохраняем тесты
        for test_form in form.tests.entries:
            if test_form.input_data.data and test_form.expected_output.data:
                test = PythonTest(
                    task_id=task.id,
                    args=test_form.input_data.data,
                    result=test_form.expected_output.data
                )
                db_sess.add(test)

        db_sess.commit()
        return redirect("/tasks")

    return render_template("python/add_task.html", level=session['level'], form=form)


@bp.route("/tasks/junior")
def junior():
    """Уровень сложности Junior"""

    return ""


@bp.route("/tasks/middle")
def middle():
    """Уровень сложности Middle"""

    return ""


@bp.route("/tasks/senior")
def senior():
    """Уровень сложности Senior"""

    return ""