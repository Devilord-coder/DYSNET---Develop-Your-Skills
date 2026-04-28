# Подключение flask
from flask import Flask, request, g, send_from_directory
from flask import render_template, redirect
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_restful import reqparse, abort, Api, Resource

# Встроенные библиотеки
import os
import datetime

# Формы регистрации/авторизации
from backend.forms import *

# База данных
from backend.database import db_session
from backend.database.__all_models import User

# Обработчик ошибок
from backend.errors import *

# Работа с rest
from backend.api import *
from backend.utils.secure_email import secure_email

# ENV
import os
from dotenv import load_dotenv
load_dotenv()

# Путь к БД
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/server.db")

# Хост и порт
HOST = os.getenv("FLASK_HOST", "0.0.0.0")
PORT = os.getenv("FLASK_PORT", 8080)

# Приложение
app = Flask(__name__)
# Ключ доступа (нужен для login_manager)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret")
# время хранения сессий
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(
    days=int(os.getenv("PERMANENT_SESSION_LIFETIME_DAYS", "secret"))
)
# путь, куда загружать файлы
app.config['UPLOAD_FOLDER'] = 'data/uploads'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('data/uploads', filename)


@app.before_request
def create_session():
    """Создает сессию перед каждым запросом"""
    g.db_session = db_session.create_session()

@app.teardown_appcontext
def close_session(exception=None):
    """Закрывает сессию после запроса"""
    db_sess = g.pop('db_session', None)
    if db_sess is not None:
        db_sess.close()


@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя"""

    db_sess = g.db_session
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
    if form.validate_on_submit(): # форма успешно отправлена
        db_sess = g.db_session
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
        db_sess = g.db_session
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
            aboutme=form.aboutme.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register_form.html", title="Регистрация", form=form)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Профиль пользователя"""

    def get_user_avatar():
        for file in os.listdir("data/uploads"):
            if secure_email(current_user) in file:
                print(file)
                return file
        return None

    return render_template("profile.html", title="Профиль", avatar=get_user_avatar(), user=current_user)


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Изменение профиля пользователя"""

    form = EditProfileForm()
    if form.validate_on_submit() or (request.method == "POST" and
                                     request.files['file']):
        db_sess = g.db_session
        user = db_sess.get(User, current_user.id)
        if request.files['file']:
            file = request.files['file']
            print("We have a file")
            safe_email = secure_email(current_user)
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{safe_email}.{file_extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            user.set_avatar(filepath)
        if form.name.data:
            user.set_name(form.name.data)
        if form.surname.data:
            user.set_surname(form.surname.data)
        if form.aboutme.data:
            user.set_aboutme(form.aboutme.data)
        db_sess.commit()
        return redirect("/profile")

    return render_template("edit_profile.html", title="Профиль", form=form)


@app.route("/profile/<int:user_id>")
@login_required
def view_profile(user_id):
    """Просмотр профиля пользователя по ID"""

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        abort(404)
    return render_template("profile.html", title=f"Профиль {user.name}", user=user)


@app.route("/logout")
@login_required
def logout():
    """Выход из аккаунта"""

    logout_user()
    return redirect("/")


def error_init():
    """Обработка ошибок"""

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


def blueprint_init():
    """Инициализация всех веток"""

    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(cursive_printing.blueprint)
    app.register_blueprint(admin_api.blueprint)
    app.register_blueprint(english.blueprint)
    app.register_blueprint(python_api.bp)
    app.register_blueprint(clicker_api.blueprint)


def main():
    """Главная функция"""

    error_init()
    blueprint_init()
    db_session.global_init(DATABASE_PATH)
    app.run(host=HOST, port=PORT)


if __name__ == "__main__":
    main()
