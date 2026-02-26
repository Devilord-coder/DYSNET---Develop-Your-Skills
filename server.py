from flask import Flask

app = Flask(__name__)


app.route("/")
app.route("/index")
def index():
    return ""


def main():
    app.run(host="$HOST$", port="$PORT$")


if __name__ == "__main__":
    main()
