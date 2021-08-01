from flask_restful import Resource, abort, url_for
from flask import jsonify

from data import db_session
from data.lessons import Lesson
from fuzzywuzzy import fuzz


def abort_if_lessons_not_found(lesson_id):
    session = db_session.create_session()
    lesson = session.query(Lesson).get(lesson_id)
    if not lesson:
        abort(404, message=f"Lesson {lesson_id} not found")
    return lesson


class LessonsResource(Resource):
    def get(self):
        session = db_session.create_session()
        lessons_l = session.query(Lesson)
        lessons = []
        for lesson in lessons_l:
            lesson.top_image = lesson.top_image.hex()
            lessons.append(lesson)
        return jsonify({'lessons': {lesson.id: lesson.to_dict(
            only=[i for i in list(vars(lesson).keys()) if i not in ['_sa_instance_state', 'id']]) for
                                    lesson in lessons}})
