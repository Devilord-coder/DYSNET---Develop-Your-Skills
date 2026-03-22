from flask import Flask
from flask import render_template, redirect
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

# Формы регистрации/авторизации
from backend.forms.register_form import RegisterForm
from backend.forms.login_form import LoginForm

# База данных
from backend import db_session
from backend.database.models.users_model import User

app = Flask(__name__)
app.config["SECRET_KEY"] = "dysnet_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
@app.route("/index")
def index():
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
                "register.html",
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


@app.route("/logout")
@login_required
def logout():
    """Выход из аккаунта"""
    logout_user()
    return redirect("/")


@app.errorhandler(Exception)
def handle_exception(exсeption):
    """Обработчик ошибок"""

    error_message = (
        str(exсeption) if str(exсeption) else "Произошла непредвиденная ошибка"
    )
    if hasattr(exсeption, "code"):
        status_code = exсeption.code
        error_title = f"Ошибка {status_code}"
    else:
        status_code = 500
        error_title = "Внутренняя ошибка сервера"
        error_message = "request failed"

    return (
        render_template(
            "error.html",
            title=error_title,
            message=error_message,
            status_code=status_code,
        ),
        status_code,
    )


def main():
    """Главная функция"""

    db_session.global_init("backend/database/db/server.db")
    app.run(host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()
