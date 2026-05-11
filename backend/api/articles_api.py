from flask import (
    Blueprint, render_template,
    request, redirect,
    g, jsonify,
    abort
)
from flask_login import current_user

# Формы
from backend.forms import ArticleForm

# БД
from backend.database.__all_models import Article, Theme

from datetime import datetime
import markdown
import html

# Отдельная ветка
bp = Blueprint("articles", __name__, template_folder="templates")


def render_article_content(article):
    """Рендерит текст статьи с экранированием"""
    
    if article.type.lower() == 'md':
        # Markdown сам генерирует безопасный HTML
        return markdown.markdown(
            article.text, 
            extensions=['fenced_code', 'tables', 'nl2br']
        )
    
    elif article.type.lower() == 'html':
        from bleach import clean
        return clean(
            article.text,
            tags=['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3'],
            attributes={'*': ['class', 'id']},
            strip=True
        )
    
    else:
        # Экранируем ВСЕ специальные символы
        escaped_text = html.escape(article.text)
        # Заменяем \n на <br> только если нужно
        formatted_text = escaped_text.replace('\n', '<br>\n')
        return f'<div style="white-space: pre-wrap; font-family: inherit;">{formatted_text}</div>'


@bp.route("/articles")
def articles():
    """Страница со статьями"""

    # Получаем поисковый запрос из GET-параметров
    search_query = request.args.get('search', '').strip()

    db_sess = g.db_session
    articles = db_sess.query(Article).all()
    if search_query:
        articles = [
            a for a in articles
            if (search_query.lower() in a.title.lower() or
                search_query.lower() in a.theme.name.lower() or
                search_query.lower() in a.tags.lower() or
                search_query.lower() in a.author.name.lower() or
                search_query.lower() in a.text.lower())
        ]
    return render_template("articles/articles.html", title="Научные статьи", articles=articles,
                           search_query=search_query)


@bp.route("/articles/<int:article_id>")
def get_article(article_id):
    db_sess = g.db_session
    article = db_sess.get(Article, article_id)
    return render_template("articles/article.html", title=article.title,
                           article=article,
                           render_article_content=render_article_content)
    

@bp.route("/articles/like/<int:article_id>", methods=["POST"])
def like_article(article_id):
    return ""


@bp.route("/articles/comment/<int:article_id>", methods=["POST"])
def add_comment(article_id):
    return ""


@bp.route("/api/topics/suggestions")
def get_topic_suggestions():
    """API для получения предложений тем"""

    db_sess = g.db_session
    query = request.args.get('q', '').strip()

    # Загружаем существующие темы из базы данных
    topics = db_sess.query(Theme).all()
    suggestions = map(lambda x: x.name, topics)

    if query:
        suggestions = [s for s in suggestions if query.lower() in s.lower()]

    return jsonify({
        'suggestions': suggestions[:20]  # Ограничиваем 20 вариантами
    })


@bp.route('/articles/publish')
def publish():
    return render_template("articles/publish.html", title="Публикация статьи")


@bp.route("/articles/add", methods=["GET", "POST"])
def add_article():
    form = ArticleForm()

    if form.validate_on_submit():
        db_sess = g.db_session

        topic_name = request.form.get("topic")
        topic = db_sess.query(Theme).filter(Theme.name == topic_name).first()
        if not topic:
            topic = Theme(name=topic_name)
            db_sess.add(topic)
            db_sess.flush()

        article = Article(
            title=form.title.data,
            tags=form.tags.data,
            user_id=current_user.id,
            type=form.type.data,
            text=form.text.data,
            theme_id=topic.id
        )
        db_sess.add(article)
        db_sess.commit()
        return redirect('/articles/publish')
    return render_template("articles/add_article.html", title="Написание статьи", form=form)


@bp.route("/artices/delete/<int:article_id>", methods=["GET", "POST"])
def delete(article_id):
    db_sess = g.db_session
    article = db_sess.get(Article, article_id)
    db_sess.delete(article)
    db_sess.commit()

    return redirect("/articles")


@bp.route("/articles/edit/<int:article_id>", methods=["GET", "POST"])
def edit(article_id):
    db_sess = g.db_session
    article = db_sess.get(Article, article_id)
    if current_user.id != article.author.id:
        abort(403)
    return redirect("/articles")


@bp.route("/articles/author/<int:user_id>")
def article_author(user_id):
    articles = g.db_session.query(Article).filter(Article.user_id == current_user.id)
    return render_template(
        "articles/article_author.html", title=f"Статьи от {current_user.name}",
        articles=articles
    )