from flask_restful import reqparse, abort, Api, Resource
from flask import g, jsonify
from backend.database.__all_models import News
from backend.utils.to_dict import to_dict

# Парсер аргументов POST запроса для новостей
parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)


def abort_if_news_not_found(news_id):
    """Проверка наличия новости"""

    session = g.db_session
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"News {news_id} not found")


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = g.db_session
        news = session.get(News, news_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = g.db_session
        news = session.get(News, news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    def get(self):
        session = g.db_session
        news = session.query(News).all()
        return jsonify({'news': [to_dict(item,
                                         only=('title', 'content', 'user_id')) for item in news]})

    def post(self):
        args = parser.parse_args()
        session = g.db_session
        news = News(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id']
        )
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK', 'id': news.id})
