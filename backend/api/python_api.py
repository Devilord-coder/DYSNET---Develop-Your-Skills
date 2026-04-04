from flask import Blueprint, render_template, request, jsonify, session

# Отдельная ветка
bp = Blueprint("python", __name__, template_folder="templates")

@bp.route("/choose_level")
def choose_level():
    """Выбор уровня сложности"""

    return render_template("python/choose_level.html", title="Выбор режима")


@bp.route("/task/junior")
def task_easy():
    """уровень сложности Junior"""

    return ""


@bp.route("/task/middle")
def task_medium():
    """уровень сложности Middle"""

    return ""


@bp.route("/task/senior")
def task_hard():
    """уровень сложности Senior"""

    return ""