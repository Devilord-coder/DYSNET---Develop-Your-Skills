from flask import Flask
from flask import render_template

# Быза данных
from backend import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dysnet_secret_key'


app.route("/")
app.route("/index")
def index():
    return render_template("index.html")

    
def main():
    """ Главная функция """

    db_session.global_init("data/server.db")
    app.run(host='127.0.0.1', port=80)


if __name__ == "__main__":
    main()
