from flask import Blueprint, render_template, redirect, abort, request
from flask_login import current_user, login_required

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
    db_sess.delete(news)
    db_sess.commit()
    return redirect("/")
