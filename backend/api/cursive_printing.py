import time
from flask import Blueprint, jsonify, request, render_template, session, abort
from sqlalchemy import desc
from flask_login import current_user
from random import choices
from datetime import datetime

from backend.database import db_session
from backend.database.models.cursive_printing_models.words_model import (
    CursivePrintingWords,
)
from backend.database.models.cursive_printing_models.modes_model import (
    CursivePrintingModes,
)
from backend.database.models.cursive_printing_models.statistics_model import (
    CursivePrintingStatistics,
)

blueprint = Blueprint("cursive_printing", __name__, template_folder="templates")


@blueprint.route("/choose_mode")
def choose_mode():
    """Выбор модуля скоропечатания"""

    return render_template("cursive_printing/choose_mode.html", title="Выбор режима")


@blueprint.route("/training", methods=["POST", "GET"])
def training():
    """Тренировка навыка скоропечатания"""

    if request.method == "POST":
        mode = request.form.get("mode")  # Получение модуля
        language = request.form.get("language")  # Получение языка
        # Запоминаем все необходимые данные в сессию пользователя
        session["mode"] = mode
        session["language"] = language
        db_sess = db_session.create_session()
        mode_id = (
            db_sess.query(CursivePrintingModes)
            .filter(CursivePrintingModes.mode == f"{mode}_{language}")
            .first()
        )
        words = (
            db_sess.query(CursivePrintingWords)
            .filter(CursivePrintingWords.mode == mode_id.id)
            .all()
        )
        session["words"] = [
            word.word for word in words
        ]  # получаем слова с учётом выбора пользователя
    training_text = choices(session["words"], k=20)
    session["training_text"] = " ".join(training_text)
    language = session.get("language", "russian")
    session["current_index"] = 0
    session["correct_clicks"] = 0
    session["error_clicks"] = 0
    return render_template(
        "cursive_printing/training.html",
        title="Тренировка скоропечатания",
        texts=session["training_text"],
        language=language,
    )


@blueprint.route("/api/check_key", methods=["POST"])
def check_key():
    """Проверка правильности нажатия клавиши"""

    data = request.get_json()  # получение данных запроса
    key = data.get("key", "")

    # получение всех необходимых значений из сессии
    text = session.get("training_text", "")
    current_index = session.get("current_index", 0)
    correct_clicks = session.get("correct_clicks", 0)
    error_clicks = session.get("error_clicks", 0)

    finished = False
    if current_index == 0:
        session["start_time"] = time.time()  # время начала тренировки

    # Проверка правильности нажатия клавиши, обновление данных
    expected_key = text[current_index]
    is_correct = False
    if key == expected_key:
        is_correct = True
        correct_clicks += 1
        current_index += 1
    else:
        error_clicks += 1
    progress = int(current_index / len(text) * 100)

    session["current_index"] = current_index
    session["correct_clicks"] = correct_clicks
    session["error_clicks"] = error_clicks

    # Сохранение статистики для авторизованных пользователей, если текст закончился
    if current_index >= len(text):
        finished = True
        session["end_time"] = time.time()
        if current_user.is_authenticated:
            statistics = CursivePrintingStatistics()
            statistics.datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            training_time = round(
                session.get("end_time", 0) - session.get("start_time", 0), 3
            )
            statistics.training_time = training_time
            quantity_symbols = session.get("correct_clicks", 0) + session.get(
                "error_clicks", 0
            )
            statistics.quantity_symbols = quantity_symbols
            statistics.speed = int((quantity_symbols / training_time) * 60)
            statistics.quantity_errors = session.get("error_clicks", 0)

            language = None
            if session.get("language", "russian") == "russian":
                language = "Русский"
            else:
                language = "Английский"
            statistics.language = language

            mode = session.get("mode", "fourth")
            if mode == "first":
                statistics.mode = "Режим верхней строки"
            elif mode == "second":
                statistics.mode = "Режим нижней строки"
            elif mode == "third":
                statistics.mode = "Режим средней строки"
            elif mode == "fourth":
                statistics.mode = "Общий режим"

            statistics.user = current_user.id
            db_sess = db_session.create_session()
            db_sess.add(statistics)
            db_sess.commit()
        return jsonify(
            {
                "finished": finished,
                "correct_clicks": correct_clicks,
                "error_clicks": error_clicks,
            }
        )

    return jsonify(
        {
            "is_correct": is_correct,
            "current_index": current_index,
            "correct_clicks": correct_clicks,
            "error_clicks": error_clicks,
            "progress": progress,
            "finished": finished,
        }
    )


@blueprint.route("/api/reset_training", methods=["POST"])
def reset_training():
    """Обновление данных для тренировки"""

    words = session.get("words", [])

    words = choices(words, k=20)  # составление нового текста
    new_text = " ".join(words)

    session["training_text"] = new_text
    session["current_index"] = 0
    session["correct_clicks"] = 0
    session["error_clicks"] = 0
    return jsonify(
        {
            "status": "ok",
            "text": new_text,
        }
    )


@blueprint.route("/statistics")
def statistics():
    """Просмотр статистики для авторизованных пользователей"""

    if not current_user.is_authenticated:
        abort(401)

    db_sess = db_session.create_session()
    user_statistics = (
        db_sess.query(CursivePrintingStatistics)
        .filter(CursivePrintingStatistics.user == current_user.id)
        .order_by(desc(CursivePrintingStatistics.datetime))
        .all()
    )
    return render_template(
        "cursive_printing/statistics.html",
        title="Статистика скоропечатания",
        statistic=user_statistics,
    )
