from flask import Flask
from flask import render_template, redirect
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
import datetime

# Формы регистрации/авторизации
from backend.forms.register_form import RegisterForm
from backend.forms.login_form import LoginForm

# База данных
from backend import db_session
from backend.database.models.users_model import User

# Обработчик ошибок
from backend.errors import *

# Работа с rest
from backend.api import user_api
from backend.api import cursive_printing
from backend.api import admin_api
from backend.api import english

app = Flask(__name__)
app.config["SECRET_KEY"] = "dysnet_secret_key"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=30)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
@app.route("/index")
def index():
    """Главная страница"""
    return render_template("index.html", title="Главная страница")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Авторизация пользователя"""

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(
            "login_form.html",
            message="Неправильный логин или пароль",
            form=form,
            title="Авторизация",
        )
    return render_template("login_form.html", title="Авторизация", form=form)


@app.route("/register", methods=["GET", "POST"])
def reqister():
    """Регистрация пользователей"""

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "register_form.html",
                title="Регистрация",
                form=form,
                message="Пароли не совпадают",
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register_form.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register_form.html", title="Регистрация", form=form)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html", title="Профиль")


@app.route("/logout")
@login_required
def logout():
    """Выход из аккаунта"""
    logout_user()
    return redirect("/")


def error_init():
    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(406, not_acceptable)
    app.register_error_handler(408, request_timeout)
    app.register_error_handler(409, conflict)
    app.register_error_handler(410, gone)
    app.register_error_handler(411, length_required)
    app.register_error_handler(412, precondition_failed)
    app.register_error_handler(413, payload_too_large)
    app.register_error_handler(414, uri_too_long)
    app.register_error_handler(415, unsupported_media_type)
    app.register_error_handler(416, range_not_satisfiable)
    app.register_error_handler(417, expectation_failed)
    app.register_error_handler(418, im_a_teapot)
    app.register_error_handler(421, misdirected_request)
    app.register_error_handler(422, unprocessable_entity)
    app.register_error_handler(423, locked)
    app.register_error_handler(424, failed_dependency)
    app.register_error_handler(428, precondition_required)
    app.register_error_handler(429, too_many_requests)
    app.register_error_handler(431, headers_too_large)
    app.register_error_handler(451, legal_unavailable)
    app.register_error_handler(500, internal_error)
    app.register_error_handler(501, not_implemented)
    app.register_error_handler(502, bad_gateway)
    app.register_error_handler(503, service_unavailable)
    app.register_error_handler(504, gateway_timeout)
    app.register_error_handler(505, http_version_not_supported)


def main():
    """Главная функция"""

    error_init()
    db_session.global_init("data/server.db")
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(cursive_printing.blueprint)
    app.register_blueprint(admin_api.blueprint)
    app.register_blueprint(english.blueprint)
    app.run(host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()