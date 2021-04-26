from flask_restful import Resource, abort, url_for
from flask import jsonify

from data import db_session
from data.users import User
from fuzzywuzzy import fuzz


def abort_if_lessons_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"Lesson {user_id} not found")
    return user




class UsersResource(Resource):
    def get(self, user_id):
        user = [abort_if_lessons_not_found(user_id)]
        users = []
        for i in user:
            i.image = i.image.hex()
            users.append(i)
        return jsonify({'user': {user.id: user.to_dict(
            only=[i for i in list(vars(user).keys()) if i not in ['_sa_instance_state', 'id']]) for
                                    user in users}})

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