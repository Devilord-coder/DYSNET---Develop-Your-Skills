from functools import wraps

from flask import Blueprint, render_template, request, redirect, abort
from flask_login import current_user

from backend.database import db_session
from backend.database.models.users_model import User

# Отдельная ветка
blueprint = Blueprint("admin_api", __name__, template_folder="templates")


@blueprint.route("/admin")
def admin():
    """Просмотр всех пользователей"""

    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template("admin.html", title="Просмотр пользователей", users=users)


@blueprint.route("/change_role/<user_id>", methods=["POST"])
def change_role(user_id):
    """Изменение роли пользователя"""

    new_role = request.form.get("role")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    user.role = new_role
    db_sess.commit()
    return redirect("/admin")


@blueprint.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    """Удаление пользователя"""

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    db_sess.delete(user)
    db_sess.commit()
    return redirect("/admin")


def admin_required(f):
    """Декоратор — доступ только для админов"""

    @wraps(f)  # сохраняет имя и докстринг оригинальной функции
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)  # Forbidden
        return f(*args, **kwargs)

    return decorated_function
