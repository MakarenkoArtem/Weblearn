from flask_restful import Resource, abort, url_for, reqparse
from flask import jsonify

from data import db_session
from data.users import User


def abort_if_users_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"Lesson {user_id} not found")
    return user




class UsersResource(Resource):
    def get(self, user_id):
        user = [abort_if_users_not_found(user_id)]
        users = []
        for i in user:
            i.image = i.image.hex()
            users.append(i)
        return jsonify({'user': {user.id: user.to_dict(
            only=[i for i in list(vars(user).keys()) if i not in ['_sa_instance_state', 'id']]) for
            user in users}})

    def delete(self, user_id):
        news = abort_if_users_not_found(user_id)
        session = db_session.create_session()
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})

parser = reqparse.RequestParser()
parser.add_argument('nickname', required=True)
parser.add_argument('password', required=True)
parser.add_argument('password_again', required=True)
parser.add_argument('city_from', required=True)
parser.add_argument('image', required=True)
parser.add_argument('email', required=True)
parser.add_argument('about', required=True)

class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        users = []
        for i in user:
            i.image = i.image.hex()
            users.append(i)
        return jsonify({'users': {user.id: user.to_dict(
            only=[i for i in list(vars(user).keys()) if i not in ['_sa_instance_state', 'id']]) for
            user in users}})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        if args['password'] != args['password_again']:
            return jsonify({'password': 'Password mismatch'})
        user = User(
            nickname=args['nickname'],
            city_from=args['city_from'],
            image=args['image'],
            email=args['email'],
            about=args['about'])
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
