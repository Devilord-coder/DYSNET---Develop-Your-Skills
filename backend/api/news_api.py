from flask import Blueprint, render_template, redirect, abort, request
from flask_login import current_user, login_required

import uuid
import os
from werkzeug.utils import secure_filename

from backend.database import db_session
from backend.database.models.news_model import News
from backend.forms.news_form import NewsForm

blueprint = Blueprint("news", __name__, template_folder="templates")


@blueprint.route("/news/create", methods=["GET", "POST"])
@login_required
def create():
    """Создание новости"""

    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.user_id = current_user.id
        file = form.image.data
        # Проверяем загрузку картинки, сохраняем
        if file and file.filename:
            original_filename = file.filename
            safe_name = secure_filename(original_filename)
            extension = safe_name.rsplit(".", 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{extension}"
            news.image = f"{unique_name}"
            full_path = os.path.join("data", "uploads", unique_name)
            file.save(full_path)
        else:
            news.image = None
        db_sess.add(news)
        db_sess.commit()
        return redirect("/")
    return render_template("news_editing.html", title="Добавление новости", form=form)


@blueprint.route("/news/edit/<news_id>", methods=["GET", "POST"])
@login_required
def edit(news_id):
    """Редактирование новости по id"""

    if not (current_user.role == "admin"):
        return redirect("/")

    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id).first()
    if not news:
        return abort(404)

    form = NewsForm()
    if form.validate_on_submit():
        news.title = form.title.data
        news.content = form.content.data
        file = form.image.data
        # Проверяем загрузку картинки. Если загружена, меняем и удаляем старую
        if file and file.filename:
            if news.image:
                file_path = os.path.join("data", "uploads", news.image)
                if os.path.exists(file_path):
                    os.remove(file_path)
            original_filename = file.filename
            safe_name = secure_filename(original_filename)
            extension = safe_name.rsplit(".", 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{extension}"
            news.image = f"{unique_name}"
            full_path = os.path.join("data", "uploads", unique_name)
            file.save(full_path)
        db_sess.commit()
        return redirect("/")
    elif request.method == "GET":
        form.title.data = news.title
        form.content.data = news.content
        return render_template(
            "news_editing.html", title="Редактирование новости", form=form
        )


@blueprint.route("/news/delete/<news_id>", methods=["POST"])
@login_required
def delete(news_id):
    """Удаление новости по id"""

    if not (current_user.role == "admin"):
        return redirect("/")

    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id).first()
    if not news:
        return abort(404)
    # Если была картинка, удаляем из памяти
    if news.image:
        file_path = os.path.join("data", "uploads", news.image)
        if os.path.exists(file_path):
            os.remove(file_path)
    db_sess.delete(news)
    db_sess.commit()
    return redirect("/")
