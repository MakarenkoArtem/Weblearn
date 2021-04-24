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

def abort_if_title_lessons_not_found(lesson_title):
    session = db_session.create_session()
    lesson = None
    for i in session.query(Lesson).all():
        print("!!!!!", i.title)
        print("-".join(i.title.split()).lower(), lesson_title)
    s = [[fuzz.ratio("-".join(i.title.split()).lower(), lesson_title), i] for i in session.query(Lesson).all()]
    s.sort(reverse=True)
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
            lesson = abort_if_title_lessons_not_found(title)
        else:
            lesson = abort_if_lessons_not_found(lesson_id)
        lessons = []
        for i in lesson:
            lesson.top_image = lesson.top_image.hex()
            lessons.append(i)
        return jsonify({'lessons': {lesson.id: lesson.to_dict(
            only=[i for i in list(vars(lesson).keys()) if i not in ['_sa_instance_state', 'id']]) for
                                    lesson in lessons}})