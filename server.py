# Подключение flask
from flask import Flask, request, g, send_from_directory, flash
from flask import render_template, redirect
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_restful import reqparse, abort, Api, Resource
from sqlalchemy import desc

# Встроенные библиотеки
import os
import datetime
import secrets

# Формы регистрации/авторизации
from backend.forms import *

# База данных
from backend.database import db_session
from backend.database.__all_models import User, News

# Обработчик ошибок
from backend.errors import *

# Работа с rest
from backend.api import *
from backend.utils.secure_email import secure_email

# ENV
import os
from dotenv import load_dotenv

# Работа с почтой
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
app.config["UPLOAD_FOLDER"] = "data/uploads"
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)

# Настройки почты из .env
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


def send_email(to_email, subject, body_html):
    """Универсальная отправка писем"""

    msg = MIMEMultipart()
    msg["From"] = MAIL_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))

    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            if MAIL_USE_TLS:
                server.starttls()

        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False


def send_confirmation_email(email, token):
    """Отправка письма для подтвержения почты"""

    link = f"http://127.0.0.1:8080/confirm/{token}"
    subject = "Подтверждение регистрации"
    body = f"""
    <html>
        <body>
            <h2>Добро пожаловать!</h2>
            <p>Для подтверждения регистрации перейдите по ссылке:</p>
            <a href="{link}">{link}</a>
            <p>Если вы не регистрировались, просто проигнорируйте это письмо.</p>
        </body>
    </html>
    """
    return send_email(email, subject, body)


def send_reset_email(email, token):
    """Отправка письма для восстановления пароля"""

    link = f"http://127.0.0.1:8080/reset_password/{token}"
    subject = "Восстановление пароля"
    body = f"""
    <html>
        <body>
            <h2>Восстановление пароля</h2>
            <p>Вы запросили сброс пароля. Для установки нового пароля перейдите по ссылке:</p>
            <a href="{link}">{link}</a>
            <p>Ссылка действительна 2 часа.</p>
            <p>Если вы не запрашивали сброс, просто проигнорируйте это письмо.</p>
        </body>
    </html>
    """
    return send_email(email, subject, body)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("data/uploads", filename)


@app.before_request
def create_session():
    """Создает сессию перед каждым запросом"""
    g.db_session = db_session.create_session()


@app.teardown_appcontext
def close_session(exception=None):
    """Закрывает сессию после запроса"""
    db_sess = g.pop("db_session", None)
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

    db_sess = g.db_session
    news = db_sess.query(News).order_by(desc(News.created_date)).all()
    return render_template("index.html", title="Главная страница", news=news)


@app.route("/contacts")
def contacts():
    """Страница с контактами"""

    return render_template("contacts.html", title="Контакты")


@app.route("/skills")
def skills():
    """Страница навыков"""

    return render_template("skills.html", title="Улучшение навыков")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Авторизация пользователя"""

    form = LoginForm()
    if form.validate_on_submit():  # форма успешно отправлена
        db_sess = g.db_session
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                # Генерируем токен для неподверждённых пользователей
                token = secrets.token_urlsafe(32)
                user.confirmation_token = token
                send_confirmation_email(user.email, token)
                db_sess.commit()
                return redirect("/confirm_page")
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
        token = secrets.token_urlsafe(32)  # генерируем токен для подтверждения
        send_confirmation_email(user.email, token)
        user.confirmation_token = token
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/confirm_page")
    return render_template("register_form.html", title="Регистрация", form=form)


@app.route("/confirm_page")
def confirm_page():
    """Страница ожидания для подтверждения"""

    return render_template("confirm_page.html", title="Ожидание подтверждения")


@app.route("/confirm/<token>")
def confirm_email(token):
    """Проверяем правильность токена, подтверждаем вход"""

    db_sess = g.db_session
    user = db_sess.query(User).filter(User.confirmation_token == token).first()
    if user:
        user.is_active = True
        user.confirmation_token = None
        db_sess.commit()
        login_user(user)
        return redirect("/")
    return render_template("error.html", message="Неверная ссылка")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Получение почты пользователя, отправка письма"""

    if request.method == "POST":
        email = request.form.get("email")
        db_sess = g.db_session
        user = db_sess.query(User).filter(User.email == email).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expires = datetime.datetime.now() + datetime.timedelta(
                hours=2
            )
            db_sess.commit()
            send_reset_email(user.email, token)
        return render_template("reset_sent.html", title="Ожидание подтверждения")
    return render_template("forgot_password.html", title="Смена пароля")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Проверяем правильность токена, меняем пароль"""

    db_sess = g.db_session
    user = db_sess.query(User).filter(User.reset_token == token).first()

    # Проверяем существование токена и срока действия
    if not user or user.reset_token_expires < datetime.datetime.now():
        flash("Ссылка устарела или неверна", "danger")
        return redirect("/forgot_password")

    if request.method == "POST":
        password = request.form.get("password")
        password_again = request.form.get("password_again")

        if password != password_again:
            flash("Пароли не совпадают", "danger")
            return render_template(
                "reset_password.html", token=token, title="Смена пароля"
            )

        user.set_password(password)
        user.reset_token = None
        user.reset_token_expires = None
        db_sess.commit()

        flash("Пароль успешно изменён! Войдите с новым паролем.", "success")
        return redirect("/login")

    return render_template("reset_password.html", token=token)


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

    return render_template(
        "profile.html", title="Профиль", avatar=get_user_avatar(), user=current_user
    )


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Изменение профиля пользователя"""

    form = EditProfileForm()
    if form.validate_on_submit() or (
        request.method == "POST" and request.files["file"]
    ):
        db_sess = g.db_session
        user = db_sess.get(User, current_user.id)
        if request.files["file"]:
            file = request.files["file"]
            print("We have a file")
            safe_email = secure_email(current_user)
            file_extension = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{safe_email}.{file_extension}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
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
    app.register_blueprint(memory_api.blueprint)
    app.register_blueprint(news_api.blueprint)


def main():
    """Главная функция"""

    error_init()
    blueprint_init()
    db_session.global_init(DATABASE_PATH)
    app.run(host=HOST, port=PORT)


if __name__ == "__main__":
    main()
