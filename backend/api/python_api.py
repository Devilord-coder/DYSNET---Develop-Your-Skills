from flask import Blueprint, render_template, request, jsonify, session

# Отдельная ветка
bp = Blueprint("python", __name__, template_folder="templates")

@bp.route("/choose_level")
def choose_level():
    """Выбор уровня сложности"""

    return render_template("python/choose_level.html", title="Выбор режима")


@bp.route("/tasks", methods=["POST", "GET"])
def tasks():
    if request.method == "POST":
        level = request.form.get("level")
        session['level'] = level
        print(level)

    return render_template(
        "python/tasks.html"
    )


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