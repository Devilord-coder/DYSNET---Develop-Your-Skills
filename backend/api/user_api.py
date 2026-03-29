import flask
from flask import Blueprint, make_response, jsonify, request

from backend.database import db_session
from backend.database.models.users_model import User

blueprint = Blueprint("users_api", __name__, template_folder="templates")


@blueprint.route("/api/users")
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    if not users:
        return make_response(jsonify({"error": "Not found"}), 404)
    return flask.jsonify(
        {
            "users": [
                {
                    "id": item.id,
                    "surname": item.surname,
                    "name": item.name,
                    "email": item.email,
                    "hashed_password": item.hashed_password,
                    "created_date": item.created_date,
                }
                for item in users
            ]
        }
    )


@blueprint.route("/api/users/<int:user_id>", methods=["GET"])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    users = db_sess.get(User, user_id)
    if not users:
        return make_response(jsonify({"error": "Not found"}), 404)
    return flask.jsonify(
        {
            "users": {
                "id": users.id,
                "surname": users.surname,
                "name": users.name,
                "email": users.email,
                "hashed_password": users.hashed_password,
                "created_date": users.created_date,
            }
        }
    )


@blueprint.route("/api/users", methods=["POST"])
def create_job():
    if not request.json:
        return make_response(jsonify({"error": "Empty request"}), 400)
    elif not all(
        key in request.json
        for key in [
            "surname",
            "name",
            "email",
            "hashed_password",
        ]
    ):
        return make_response(jsonify({"error": "Bad request"}), 400)

    db_sess = db_session.create_session()
    user = User(
        surname=request.json["surname"],
        name=request.json["name"],
        email=request.json["email"],
        hashed_password=request.json["hashed_password"],
    )
    user.set_password(user.hashed_password)
    db_sess.add(user)
    db_sess.commit()
    return jsonify({"id": user.id})


@blueprint.route("/api/users/<int:user_id>", methods=["POST"])
def editing_user(user_id):

    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)

    if "name" in request.json:
        user.name = request.json["name"]
    if "surname" in request.json:
        user.surname = request.json["surname"]
    if "email" in request.json:
        user.email = request.json["email"]
    if "hashed_password" in request.json:
        user.hashed_password = user.set_password(request.json["hashed_password"])
    db_sess.commit()
    return jsonify({"id": user.id})


@blueprint.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    if not user:
        return make_response(jsonify({"error": "Bad request"}), 404)
    db_sess.delete(user)
    db_sess.commit()
    return make_response(jsonify({"success": f"User {user_id} deleted"}), 200)
