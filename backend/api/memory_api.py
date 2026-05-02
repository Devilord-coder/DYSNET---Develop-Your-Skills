from flask import Blueprint, render_template, request, session, jsonify, abort
from flask_login import current_user
from datetime import datetime
from sqlalchemy import desc
from backend.database.models.memory_models.statistics_model import MemoryStatistics
from random import sample, shuffle

from backend.database import db_session
from backend.database.models.memory_models.animals_model import Animals

blueprint = Blueprint("memory", __name__, template_folder="templates")


def save_statistics(grid_size=0, moves=0, found_pairs=0):
    """Сохранение статистики для авторизованных пользователей"""

    if current_user.is_authenticated:
        statistics = MemoryStatistics()
        statistics.datetime = datetime.now()
        statistics.grid_size = grid_size
        statistics.moves = moves
        statistics.found_pairs = found_pairs
        statistics.user = current_user.id
        db_sess = db_session.create_session()
        db_sess.add(statistics)
        db_sess.commit()


def clients_info(cards):
    """Преобразует карточки для отправки клиенту"""

    return [
        {
            "card_id": c["card_id"],
            "animal_id": c["animal_id"],
            "emoji": c["emoji"],
            "image": c["image"],
            "flipped": c["flipped"],
            "matched": c["matched"],
        }
        for c in cards
    ]


@blueprint.route("/memory")
def memory():
    """Начальная отрисовка поля"""

    return render_template("memory/memory.html", title="Память")


@blueprint.route("/memory/start", methods=["POST"])
def start():
    """Подготовка карточек для игры"""

    data = request.get_json()
    size = data.get("size")  # Получение размера сетки для пользователя
    quantity_animals = size**2 // 2
    db_sess = db_session.create_session()
    animals = db_sess.query(Animals).all()
    animals = sample(animals, quantity_animals)

    cards = []
    card_id = 0
    # Выбор карточек для пользователя в нужном количестве
    for animal in animals:
        for _ in range(2):
            cards.append(
                {
                    "card_id": card_id,
                    "animal_id": animal.id,
                    "emoji": animal.emoji,
                    "image": animal.image,
                    "flipped": False,
                    "matched": False,
                }
            )
            card_id += 1

    shuffle(cards)
    # Запомнить данные в сессию
    session["memory_game"] = {
        "cards": cards,
        "size": size,
        "moves": 0,
        "found_pairs": 0,
        "first_opened": None,
        "waiting": False,
    }

    return jsonify(
        {
            "success": True,
            "cards": clients_info(cards),
            "moves": 0,
            "found_pairs": 0,
        }
    )


@blueprint.route("/memory/flip", methods=["POST"])
def flip():
    """Проверка нажатия на карточки, проверка пар, обработка конца игры"""

    game = session.get("memory_game", {})
    if not game:
        return jsonify({"error": "Игра не начата"}), 400
    cards = game.get("cards", [])

    if game.get("waiting", False):
        # Если ждём закрытия прошлых карточек, не засчитываем
        return jsonify(
            {
                "cards": clients_info(cards),
                "moves": game["moves"],
                "found_pairs": game["found_pairs"],
                "waiting": True,
            }
        )

    data = request.get_json()
    card_id = data.get("card_id")
    current_card = None
    # Ищем ссылку на карточку по id, запоминаем
    for card in cards:
        if card["card_id"] == card_id:
            current_card = card
            break
    if current_card is None:
        return jsonify({"error": "Карточка не найдена"}), 404

    if current_card["flipped"] or current_card["matched"]:
        # Если карточка уже открыта, то ничего не делаем
        return jsonify(
            {
                "cards": clients_info(cards),
                "moves": game["moves"],
                "found_pairs": game["found_pairs"],
                "waiting": True,
            }
        )

    if (
        game["first_opened"] is None
    ):  # Если первая карточка из пары, запоминаем и переворачиваем
        game["first_opened"] = current_card
        current_card["flipped"] = True
        session["memory_game"] = game
        return jsonify(
            {
                "cards": clients_info(cards),
                "moves": game["moves"],
                "found_pairs": game["found_pairs"],
                "waiting": False,
            }
        )

    # Если это вторая карточка
    current_card["flipped"] = True  # Переворачиваем карточку
    first_card = game["first_opened"]  # Достаём первую карточку
    for card in cards:
        # Ищем ссылку на карточку из сессии
        if card["card_id"] == first_card["card_id"]:
            first_card = card
            break

    if (
        first_card["animal_id"] == current_card["animal_id"]
    ):  # Если карточки совпали, открываем их навсегда
        first_card["matched"] = True
        current_card["matched"] = True
        game["found_pairs"] += 1
        game["waiting"] = False
    else:  # Иначе оставляем время для закрытия пары
        game["waiting"] = True

    game["first_opened"] = None
    game["moves"] += 1
    session["memory_game"] = game
    
    # Проверка конца игры
    if game["found_pairs"] == len(game["cards"]) // 2:
        if current_user.is_authenticated:
            grid_size = game["size"]
            moves = game["moves"]
            found_pairs = game["found_pairs"]
            save_statistics(grid_size, moves, found_pairs)

    return jsonify(
        {
            "cards": clients_info(cards),
            "moves": game["moves"],
            "found_pairs": game["found_pairs"],
            "waiting": game.get("waiting", False),
        }
    )


@blueprint.route("/memory/state", methods=["GET"])
def state():
    """Закрытие карточек спустя время, если пара не совпала"""

    game = session.get("memory_game")
    if not game:
        return jsonify({"error": "Игра не начата"}), 400

    if game.get("waiting", False):  # Закрываем карточки, если они открыты, но не пара
        for card in game["cards"]:
            if card["flipped"] and not card["matched"]:
                card["flipped"] = False
        game["waiting"] = False
        session["memory_game"] = game

    return jsonify(
        {
            "cards": clients_info(game["cards"]),
            "moves": game["moves"],
            "found_pairs": game["found_pairs"],
        }
    )


@blueprint.route("/memory/statistics")
def statistics():
    """Просмотр статистики для авторизованных пользователей"""

    if not current_user.is_authenticated:
        abort(401)

    db_sess = db_session.create_session()
    user_statistics = (
        db_sess.query(MemoryStatistics)
        .filter(MemoryStatistics.user == current_user.id)
        .order_by(desc(MemoryStatistics.datetime))
        .all()
    )
    return render_template(
        "memory/statistics.html",
        title="Статистика памяти",
        statistics=user_statistics,
    )
