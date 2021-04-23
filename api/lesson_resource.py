from flask_restful import Resource, abort
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

def abort_if_title_lessons_not_found(lesson_title):
    session = db_session.create_session()
    lesson = None
    s = [[fuzz.ratio(i.title.lower(), lesson_title), i] for i in session.query(Lesson).all()]
    s.sort()
    print(s)
    if s[0][0] > 90:
        lesson = s[0][1]
    if not lesson:
        abort(404, message=f"Lesson {lesson_title} not found")
    return lesson


class LessonResource(Resource):
    def get(self, lesson_id, title=""):
        print(lesson_id, title)
        if not lesson_id:
            lesson_id = abort_if_title_lessons_not_found(title).id
        lesson = abort_if_lessons_not_found(lesson_id)
        lesson.top_image = str(lesson.top_image)
        return jsonify({'lesson': lesson.to_dict(only=list(vars(lesson).keys())[1:])})