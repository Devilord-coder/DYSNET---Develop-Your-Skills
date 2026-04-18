from flask import Blueprint, render_template, request, redirect, session

# Формы
from backend.forms import AddTaskForm

# БД
from backend.database.__all_models import PythonTask, PythonTest
from backend.database import db_session

# Работа с admin_api
from .admin_api import admin_required

# Отдельная ветка
bp = Blueprint("python", __name__, template_folder="templates")

@bp.route("/choose_level")
def choose_level():
    """Выбор уровня сложности"""

    return render_template("python/choose_level.html", title="Выбор режима")


@bp.route("/tasks", methods=["POST", "GET"])
def tasks():
    """Просмотр заданий"""
    
    db_sess = db_session.create_session()
    tasks = db_sess.query(PythonTask).filter(PythonTask.task_type == session['level']).all()

    if request.method == "POST":
        level = request.form.get("level")
        session['level'] = level
        print(session['level'])
        redirect(f"tasks/{session['level']}")

    ...

    return render_template(
        "python/tasks.html",
        tasks=tasks,
        level=session['level']
    )


@bp.route("/tasks/add", methods=['GET', 'POST'])
@admin_required
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
        print(f"task {task} added")
        db_sess.add(task)

        # Сохраняем тесты
        for test_form in form.tests.entries:
            if test_form.args.data and test_form.result.data:
                test = PythonTest(
                    task_id=task.id,
                    args=test_form.args.data,
                    result=test_form.result.data
                )
                print(f"test {test} added")
                db_sess.add(test)

        db_sess.commit()
        db_sess.close()
        return redirect(f"/tasks/{session['level']}")

    return render_template("python/add_task.html", level=session['level'], form=form)


@bp.route("/tasks/junior")
def junior():
    """Уровень сложности Junior"""

    return render_template(
        "python/tasks.html",
        level="junior"
    )


@bp.route("/tasks/middle")
def middle():
    """Уровень сложности Middle"""

    return render_template(
        "python/tasks.html",
        level="middle"
    )


@bp.route("/tasks/senior")
def senior():
    """Уровень сложности Senior"""

    return render_template(
        "python/tasks.html",
        level="senior"
    )