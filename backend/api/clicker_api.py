from flask import Blueprint, render_template, session, jsonify, request, abort
from flask_login import current_user
from sqlalchemy import desc
from random import randint
from datetime import datetime
import time

from backend.database.models.clicker_models.statistics_model import ClickerStatistics
from backend.database import db_session

blueprint = Blueprint("clicker", __name__, template_folder="templates")


APPEARANCE_TIME = [1500, 1450, 1400, 1350, 1300, 1250, 1200, 1150]


def save_statistics(quantity_correct):
    """Сохранение статистики для авторизованных пользователей"""

    if current_user.is_authenticated:
        statistics = ClickerStatistics()
        statistics.datetime = datetime.now()
        statistics.quantity_correct_answers = quantity_correct
        statistics.user = current_user.id
        db_sess = db_session.create_session()
        db_sess.add(statistics)
        db_sess.commit()


def is_intersecting(x, y, size, circles):
    """Проверка пересечения нового круга с существующими"""

    new_rect = {"x": x, "y": y, "size": size}
    for circle in circles:
        old_rect = circle
        if (
            new_rect["x"] < old_rect["x"] + old_rect["size"]
            and new_rect["x"] + new_rect["size"] > old_rect["x"]
            and new_rect["y"] < old_rect["y"] + old_rect["size"]
            and new_rect["y"] + new_rect["size"] > old_rect["y"]
        ):
            return True
    return False


def generate_circles():
    """Генерация 8 непересекающихся кругов"""

    circles = []
    clients_circles_information = []
    for i in range(8):
        while True:
            size = randint(50, 200)
            x = randint(0, 800 - size)
            y = randint(0, 600 - size)
            if not is_intersecting(x, y, size, circles):
                break

        r = randint(100, 255)
        g = randint(100, 255)
        b = randint(100, 255)
        show_delay = randint(100, 5500)
        time_now = int(time.time() * 1000)
        show_at = time_now + show_delay
        circles.append(
            {
                "id": i,
                "x": x,
                "y": y,
                "size": size,
                "color": f"rgb({r}, {g}, {b})",
                "show_at": show_at,
                "hide_at": show_at + APPEARANCE_TIME[i],
                "clicked": False,
            }
        )
        clients_circles_information.append(
            {
                "id": i,
                "x": x,
                "y": y,
                "size": size,
                "color": f"rgb({r}, {g}, {b})",
            }
        )
    return circles, clients_circles_information


@blueprint.route("/clicker")
def clicker():
    """Возврат страницы с полем для отрисовки"""

    return render_template("clicker/clicker.html", title="Кликер")


@blueprint.route("/clicker/start", methods=["POST"])
def start():
    """Подготовка кругов"""

    circles, clients_circles_information = generate_circles()
    session["clicker_game"] = {
        "circles": circles,
        "remaining": 8,
        "correct": 0,
        "round_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "statistics_save": False,
    }
    return jsonify(
        {"success": True, "circles": clients_circles_information, "total": 8}
    )


@blueprint.route("/clicker/click", methods=["POST"])
def click():
    """Проверка клика пользователя"""

    data = request.get_json()
    click_x = data.get("x")
    click_y = data.get("y")
    game = session.get("clicker_game", "")
    if not game:
        return jsonify({"error": "Игра не начата"}), 400

    time_now = int(time.time() * 1000)
    circles = game["circles"]
    for circle in circles:
        if circle["clicked"]:
            continue
        if (
            circle["show_at"] <= time_now <= circle["hide_at"]
        ):  # проверяем активен ли круг
            circle_x = circle["x"]
            circle_y = circle["y"]
            radius = circle["size"] / 2
            center_x = circle_x + radius
            center_y = circle_y + radius
            dx = click_x - center_x
            dy = click_y - center_y
            if dx**2 + dy**2 <= radius**2:  # находится ли клик внутри круга
                circle["clicked"] = True
                game["remaining"] -= 1
                game["correct"] += 1
                session["clicker_game"] = game

                game_over = False
                if (
                    game.get("remaining", 0) == 0
                ):  # если кругов больше не осталось, заканчиваем игру
                    game_over = True
                    if not session["statistics_save"]:
                        save_statistics(
                            game["correct"]
                        )  # сохраняем статистику, если кругов больше нет
                        game["statistics_save"] = True
                        session["clicker_game"] = game
                return jsonify(
                    {
                        "hit": True,
                        "remaining": game["remaining"],
                        "correct": game["correct"],
                        "game_over": game_over,
                    }
                )
    return jsonify(
        {"hit": False, "remaining": game["remaining"], "correct": game["correct"]}
    )


@blueprint.route("/clicker/state")
def state():
    """Проверка состояния кругов (активен ли в данное время, кликнул ли пользователь)"""

    game = session.get("clicker_game", "")
    if not game:
        return jsonify({"error": "Игра не начата"}), 400

    circles = game.get("circles", [])
    current_circles = []  # активны сейчас
    clicked_circles = []  # пользователь кликнул на них
    time_now = int(time.time() * 1000)
    for circle in circles:
        id = circle["id"]
        x = circle["x"]
        y = circle["y"]
        size = circle["size"]
        color = circle["color"]
        if circle["clicked"] is False and (
            circle["show_at"] <= time_now <= circle["hide_at"]
        ):
            current_circles.append(
                {"id": id, "x": x, "y": y, "size": size, "color": color}
            )
        if circle["clicked"] is True:
            clicked_circles.append(
                {"id": id, "x": x, "y": y, "size": size, "color": color}
            )
        if time_now > circle["hide_at"] and circle["clicked"] is False:
            game["remaining"] -= 1
            circle["clicked"] = "expired"
            session["clicker_game"] = game
    if (
        game["remaining"] == 0 and not game["statistics_save"]
    ):  # если кругов не осталось, то сохраняем статистику
        save_statistics(game["correct"])
        game["statistics_save"] = True
        session["clicker_game"] = game
    return jsonify(
        {
            "active_circles": current_circles,
            "clicked_circles": clicked_circles,
            "remaining": game["remaining"],
            "correct": game["correct"],
        }
    )


@blueprint.route("/clicker/statistics")
def statistics():
    """Просмотр статистики для авторизованных пользователей"""

    if not current_user.is_authenticated:
        abort(401)

    db_sess = db_session.create_session()
    user_statistics = (
        db_sess.query(ClickerStatistics)
        .filter(ClickerStatistics.user == current_user.id)
        .order_by(desc(ClickerStatistics.datetime))
        .all()
    )
    return render_template(
        "clicker/statistics.html",
        title="Статистика кликера",
        statistic=user_statistics,
    )
