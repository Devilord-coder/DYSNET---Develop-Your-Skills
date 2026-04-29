from flask import Blueprint, render_template, request, jsonify, session, abort
from flask_login import current_user
from random import sample, shuffle, choice
from sqlalchemy import desc

from backend.database import db_session
from backend.database.models.english_models.topics_model import EnglishTopics
from backend.database.models.english_models.words_model import EnglishWords
from backend.database.models.english_models.texts_model import EnglishTexts
from backend.database.models.english_models.statistic_model import EnglishStatistics
from datetime import datetime

#  Отдельная ветка
blueprint = Blueprint("english", __name__, template_folder="templates")


def save_statistics(
    skill,
    category=None,
    quantity_correct_answers=None,
    english_word=None,
    russian_word=None,
    language=None,
    status=None,
):
    """Сохранение статистики для всех навыков"""

    if not current_user.is_authenticated:
        return
    user_id = current_user.id
    db_sess = db_session.create_session()
    statistic = EnglishStatistics()
    statistic.skill = skill
    statistic.user = user_id
    statistic.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Сохранение передаваемой информации
    if category:
        statistic.category = category
    if quantity_correct_answers is not None:
        statistic.quantity_correct_answers = quantity_correct_answers
    if english_word:
        statistic.english_word = english_word
    if russian_word:
        statistic.russian_word = russian_word
    if language:
        statistic.language = language
    if status:
        statistic.status = status

    db_sess.add(statistic)
    db_sess.commit()


def get_words_by_topic(topic):
    """Получение слов по выбранной теме из бд"""

    db_sess = db_session.create_session()
    topic_id = (
        db_sess.query(EnglishTopics).filter(EnglishTopics.title == topic).first()
    )  # Получение id темы
    if topic_id:
        topic_id = topic_id.id
        words = (
            db_sess.query(EnglishWords).filter(EnglishWords.topic == topic_id).all()
        )  # Получение слов по теме
    else:
        words = db_sess.query(EnglishWords).all()  # Если темы нет в бд, берём все слова

    # Получение подоходящих слов, запоминаем их в сессии
    all_words = [(word.russian_word, word.english_word) for word in words]
    current_words = sample(all_words, 8)
    russian_words = []
    english_words = []
    correct_answers = {}
    for words in current_words:
        russian_words.append(words[0])
        english_words.append(words[1])
        correct_answers[words[0]] = words[1]
    shuffle(russian_words)
    shuffle(english_words)
    session["current_words"] = correct_answers
    return russian_words, english_words


def get_next_word():
    """Фунция смены слова на следующее из загруженных"""

    cards_data = session.get("cards_data", [])  # получение загруженных слов
    direction = session.get("direction", "russian")  # получение языка перевода

    if not cards_data:
        return None

    next_word = choice(cards_data)
    session["current_card"] = next_word
    cards_data.remove(next_word)  # удаление использованного слова из загруженных
    session["cards_data"] = cards_data

    # Определение слова и ответа в зависимости от языка
    if direction == "russian":
        word = next_word["russian"]
        answer = next_word["english"]
    else:
        word = next_word["english"]
        answer = next_word["russian"]

    session["current_correct_answer"] = answer
    return word


def prepare_cards_data(topic, direction):
    """Подготовка данных для карточек"""

    get_words_by_topic(topic)  # получение слов по теме
    correct_answers = session["current_words"]
    all_cards = [
        {"russian": rus, "english": eng} for rus, eng in correct_answers.items()
    ]

    session["cards_data"] = all_cards
    session["direction"] = direction
    session["current_topic"] = topic

    if all_cards:
        current_word = get_next_word()  # получение первого слова
        return {"success": True, "current_word": current_word}

    return {"success": False, "error": "Нет слов"}


@blueprint.route("/choose_english_mode")
def choose_english_mode():
    """Выбор режима изучения"""

    return render_template("english/choose_mode.html", title="Выбор режима")


@blueprint.route("/english_statistics")
def english_statistics():
    """Просмотр статистики по всем навыкам"""

    if not current_user.is_authenticated:
        abort(401)

    db_sess = db_session.create_session()
    fill_gaps_statistics = (
        db_sess.query(EnglishStatistics)
        .filter(
            (EnglishStatistics.user == current_user.id) & (EnglishStatistics.skill == 1)
        )
        .order_by(desc(EnglishStatistics.datetime))
        .all()
    )
    words_matching_statistics = (
        db_sess.query(EnglishStatistics)
        .filter(
            (EnglishStatistics.user == current_user.id) & (EnglishStatistics.skill == 2)
        )
        .order_by(desc(EnglishStatistics.datetime))
        .all()
    )
    cards_statistics = (
        db_sess.query(EnglishStatistics)
        .filter(
            (EnglishStatistics.user == current_user.id) & (EnglishStatistics.skill == 3)
        )
        .order_by(desc(EnglishStatistics.datetime))
        .all()
    )
    return render_template(
        "english/statistics.html",
        title="Статистика английских навыков",
        skill1_data=fill_gaps_statistics,
        skill2_data=words_matching_statistics,
        skill3_data=cards_statistics,
    )


@blueprint.route("/words_matching")
def words_matching():
    """Сопоставление русских слов с английскими, начальное заполнение шаблона со всеми словами"""

    russian_words, english_words = get_words_by_topic(
        "Случайные слова из разных категорий"
    )
    return render_template(
        "english/words_matching.html",
        title="Сопоставление слов",
        russian_words=russian_words,
        english_words=english_words,
    )


@blueprint.route("/words_matching/results")
def words_matching_results():
    """Просмотр результата после окончания навыка"""

    all_results = session.get("results", {})
    results = all_results.get("results", [])
    total = all_results.get("total", 0)
    correct_count = all_results.get("correct_count", 0)
    topic = session.get("topic", "Случайные слова из разных категорий")
    percent = round(correct_count / total * 100)
    save_statistics(
        skill=2,
        category=topic,
        quantity_correct_answers=correct_count,
    )
    return render_template(
        "english/words_matching_result.html",
        results=results,
        total=total,
        correct_count=correct_count,
        percent=percent,
        title="Результат",
    )


@blueprint.route("/check_words", methods=["POST"])
def check_words():
    """Проверка корректности сопоставления слов пользователями"""

    data = request.get_json()  # Получение его ответа
    user_pairs = data.get("pairs", [])
    correct_pairs = session.get("current_words", {})

    results = []
    correct_count = 0
    for pair in user_pairs:
        # Проверяем совпадение слов пользователя и правильного ответа
        is_correct = False
        russian_word = pair.get("russian", "")
        english_word = pair.get("english", "")
        if correct_pairs[russian_word] == english_word:
            correct_count += 1
            is_correct = True

        results.append(
            {
                "russian": russian_word,
                "english": english_word,
                "is_correct": is_correct,
                "correct_english": correct_pairs.get(russian_word, ""),
            }
        )  # Формирование результата по каждой паре

    total_result = {
        "correct_count": correct_count,
        "total": len(user_pairs),
        "results": results,
    }  # Получение результата по всей тренировке
    session["results"] = total_result
    return jsonify(total_result)


@blueprint.route("/get_words", methods=["GET"])
def get_words():
    """Получение слов по теме, если пользователь её поменял"""

    topic = request.args.get("topic", "Случайные слова из разных категорий")
    session["topic"] = topic
    russian_words, english_words = get_words_by_topic(topic)
    return jsonify({"russian_words": russian_words, "english_words": english_words})


@blueprint.route("/fill_gaps")
def fill_gaps():
    """Вставка слов в текст, заполнение шаблона данными"""

    db_sess = db_session.create_session()
    texts = db_sess.query(EnglishTexts).all()
    current_text = choice(texts)
    text = current_text.text
    text = [
        part.strip() for part in text.split("<пропуск>")
    ]  # Разделение текста по частя (по пропускам)
    answers = current_text.answers.split("; ")
    session["answers"] = answers
    shuffled_answers = answers.copy()
    shuffle(shuffled_answers)
    title = current_text.title
    session["title"] = title
    return render_template(
        "english/fill_gaps.html",
        title="Вставка слов в текст",
        title_text=title,
        text_parts=text,
        answers_list=shuffled_answers,
        gaps_count=6,
    )


@blueprint.route("/check_fill_gaps", methods=["POST"])
def check_fill_gaps():
    """Проверка еорректности заполнения слов пользователем"""

    # Получение ответов пользователя
    user_answers = []
    for key, value in request.form.items():
        if key.startswith("gap_"):
            user_answers.append(value)

    correct_answers = session.get("answers", [])  # Получение правильных ответов
    results = []
    correct_count = 0
    for i, answer in enumerate(user_answers):
        is_correct = False
        if answer == correct_answers[i]:
            is_correct = True
            correct_count += 1
        results.append(
            {
                "index": i,
                "user_answer": answer,
                "correct_answer": correct_answers[i],
                "is_correct": is_correct,
            }
        )

    title = session.get("title", "")
    save_statistics(
        skill=1,
        category=title,
        quantity_correct_answers=correct_count,
    )
    # Возрат результата проверки
    total = len(correct_answers)
    percent = round(correct_count / total * 100)
    return jsonify(
        {
            "results": results,
            "correct_count": correct_count,
            "total": total,
            "percent": percent,
        }
    )


@blueprint.route("/cards")
def cards():
    """Создание шаблона для навыка"""

    return render_template("english/cards.html", title="Интерактивные карточки")


@blueprint.route("/cards/next", methods=["POST"])
def next_card():
    """Получение новой порции слов"""

    data = request.get_json()
    topic = data.get(
        "topic", "Случайные слова из разных категорий"
    )  # получение темы от пользователя
    direction = data.get("direction", "russian")  # получение языка
    session["direction"] = direction
    result = prepare_cards_data(topic, direction)
    return jsonify(result)


@blueprint.route("/cards/current", methods=["GET", "POST"])
def get_current_card():
    """Получение слова при изменении языка"""

    if request.method == "POST":
        data = request.get_json()
        new_direction = data.get("direction", "russian")  # получение нового языка
        if new_direction:
            session["direction"] = new_direction

        next_word = get_next_word()  # получение следующего слова
        if not next_word:  # если слова кончились, добавляем новые
            topic = session.get("current_topic", "Случайные слова из разных категорий")
            result = prepare_cards_data(topic, new_direction)
            if result["success"]:
                next_word = result["current_word"]

    # иземенение ответа в зависимости от языка
    current_card = session.get("current_card", "")
    direction = session.get("direction", "")
    correct_answer = session.get("current_correct_answer", "")

    if not current_card:
        return jsonify({"success": False, "empty": True})

    if direction == "russian":
        current_word = current_card["russian"]
    else:
        current_word = current_card["english"]

    return jsonify(
        {
            "success": True,
            "current_word": current_word,
            "correct_answer": correct_answer,
        }
    )


@blueprint.route("/cards/check", methods=["POST"])
def check_card():
    """Проверка ответа"""

    data = request.get_json()
    user_answer = data.get("answer", "").strip().lower()  # получаем ответ пользавателя
    direction = session.get("direction", "russian")
    correct_answer = session.get(
        "current_correct_answer", ""
    ).lower()  # получаем правильный ответ из сессии
    is_correct = False
    if user_answer == correct_answer:
        is_correct = True

    topic = session.get("current_topic", "Случайные слова из разных категорий")
    direction = session.get("direction", "russian")

    answer_status = "Неправильно"
    if is_correct:
        answer_status = "Правильно"

    current_card = session.get("current_card", {})
    russian_word = current_card.get("russian", "")
    english_word = current_card.get("english", "")
    save_statistics(
        skill=3,
        category=topic,
        english_word=english_word,
        russian_word=russian_word,
        language=direction,
        status=answer_status,
    )
    next_word = get_next_word()  # меняем слово, загружаем новую порцию при нехватке
    if not next_word:
        result = prepare_cards_data(topic, direction)
        next_word = result["current_word"]
    return jsonify(
        {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "finished": False,
            "next_word": next_word,
        }
    )


@blueprint.route("/cards/next_word", methods=["GET"])
def next_word():
    """Смена слова на следующее, если пользователь посмотрел ответ"""

    current_card = session.get("current_card", {})
    russian_word = current_card.get("russian", "")
    english_word = current_card.get("english", "")
    topic = session.get("topic", "Случайные слова из разных категорий")
    direction = session.get("direction", "russian")
    next_word = get_next_word()
    save_statistics(
        skill=3,
        category=topic,
        english_word=english_word,
        russian_word=russian_word,
        language=direction,
        status="Не отвечено",
    )
    return jsonify({"finished": False, "next_word": next_word})
