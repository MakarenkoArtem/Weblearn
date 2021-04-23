from flask_restful import Resource, abort
from flask import jsonify

from data import db_session
from data.lessons import Lesson



def abort_if_lessons_not_found(lesson_id):
    session = db_session.create_session()
    lesson = session.query(Lesson).get(lesson_id)
    if not lesson:
        abort(404, message=f"Lesson {lesson_id} not found")
    return lesson


class LessonResource(Resource):
    def get(self, lesson_id):
        print("API", lesson_id)
        lesson = abort_if_lessons_not_found(lesson_id)
        lesson.top_image = str(lesson.top_image)
        return jsonify({'lesson': lesson.to_dict(only=list(vars(lesson).keys())[1:])})