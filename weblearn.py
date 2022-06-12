from flask import Flask, render_template, url_for, redirect, request, session, jsonify, make_response
from flask_restful import Api
from flask_login import LoginManager, current_user, login_user
from werkzeug.security import check_password_hash
from forms.user import RegisterForm, EntryForm
from api.users_resource import UsersListResource, UsersResource
from forms.lesson import LessonForm
from data.users import User
from data.questions import Question
from data.tests import Test
from data.images import Image
from forms.question import QuestionForm
from api.lesson_resource import LessonResource
from api.lessons_resource import LessonsResource
from data import db_session
from data.lessons import Lesson
from os import listdir, remove, rmdir, mkdir, environ, path
from PIL import Image as Imagepil
import sqlalchemy
import datetime


class Card():
    def __init__(self, lesson, user):
        self.id = lesson.id
        try:
            self.author = user.nickname
        except sqlalchemy.orm.exc.NoResultFound:
            self.author = "???"
        self.items = lesson.items
        self.title = lesson.title
        self.top_image = lesson.top_image
        self.text = lesson.text
        self.test = lesson.test
        self.images = lesson.images


app = Flask(__name__)
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=1)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'my_secret_key'


def resize(pic, width=700, height=450):
    with open("static/img/!!0.png", "wb") as file:
        file.write(pic)
    im = Imagepil.open("static/img/!!0.png")
    im = im.resize((width, height))
    im.save("static/img/!!0.png")
    im = open("static/img/!!0.png", "rb").read()
    remove("static/img/!!0.png")
    return im


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(500)
def not_found(error):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    return render_template("500.html", id=id)


@app.errorhandler(404)
def not_found(error):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    return render_template("404.html", id=id)


@app.route('/del/<int:lesson>')
def del_lesson(lesson):  # страница для удаления урока
    start = datetime.datetime.now()
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    db_sess = db_session.create_session()
    d = db_sess.query(Lesson).filter(Lesson.author_id == id, Lesson.id == lesson).one()
    if d is None:
        return redirect('/weblearn')
    t = d.test
    db_sess.delete(d)
    db_sess.commit()
    try:
        t = int(t)
    except ValueError:
        return redirect('/weblearn')
    db_sess = db_session.create_session()
    d = db_sess.query(Test).filter(Test.id == t).one()
    if d is None:
        return redirect('/weblearn')
    s = d.questions.split(",")
    for i in s:
        db_sess = db_session.create_session()
        d = db_sess.query(Question).filter(Question.id == int(i)).one()
        if d is None:
            continue
        db_sess.delete(d)
        db_sess.commit()
    print(datetime.datetime.now() - start)
    return redirect('/weblearn')


@app.route('/weblearn')
@app.route('/weblearn/page=<int:page>')
@app.route('/weblearn/page=<int:page>/<int:lesson_del>')
def weblearn(page=1, lesson_del=0):  # главная страница
    start = datetime.datetime.now()
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    db_sess = db_session.create_session()
    try:
        d = db_sess.query(Test).filter(Test.author_id == id, Test.created == 1).one()
        print(d)
        if d is not None:
            d.created = 0
            db_sess.commit()
            db_sess = db_session.create_session()
    except sqlalchemy.orm.exc.NoResultFound:
        pass
    for x in db_sess.query(Test).filter(Test.author_id == id, Test.questions == "",
                                        Test.created == 0).all():
        try:
            s = str(x.id)
            db_sess.delete(x)
            for i in db_sess.query(Lesson).filter(Lesson.test == s).all():
                i.test = ""
                db_sess.commit()
                db_sess = db_session.create_session()
        except sqlalchemy.exc.InvalidRequestError as e:
            print("Не удалось удалить")
        finally:
            db_sess.commit()
            db_sess = db_session.create_session()
    if id:
        im = db_sess.query(User).filter(User.id == id).first()
        with open(f"static/img/user_images/{id}.png", "wb") as file:
            file.write(im.image)
    lessons = db_sess.query(Lesson).all()
    lessons.reverse()
    lessons = lessons[(page - 1) * 12:page * 12]
    texts = []
    [remove(f"static/img/all_images/{i}") for i in listdir("static/img/all_images") if
     i.split("_")[0] == str(id) and i.split(".")[-1] == 'png']
    img = []
    for i in lessons:
        open(f'static/img/top_images/{id}_{i.id}.png', 'wb').write(i.top_image)
        img.append(f'{id}_{i.id}.png')
        if i.items is None:
            i.items = ""
        texts.append(i.text.split("\r")[0][:31] + "...")
    c = len(db_sess.query(Lesson).all())
    max = c // 12
    if c % 12 or c == 0:
        max += 1
    pages = {1, max}
    for i in range(page - 1, page + 2):
        if 0 < i < max:
            pages.add(i)
    pages = list(pages)
    pages.sort()
    if pages[0] + 1 not in pages and len(pages) > 1:
        pages.insert(1, "...")
    if pages[-1] - 1 not in pages and len(pages) > 1:
        pages.insert(-2, "...")
    if len(pages) == 1:
        pages = []
    try:
        db_sess = db_session.create_session()
        name = db_sess.query(User).filter(User.id == id).one()
        name = name.nickname
    except sqlalchemy.orm.exc.NoResultFound:
        name = ''
    cards = [Card(lesson, db_sess.query(User).filter(User.id == lesson.author_id).one()) for lesson in lessons]
    db_sess.commit()
    print(datetime.datetime.now() - start)
    return render_template("weblearn.html", id=id, img=img, lessons=cards, texts=texts,
                           pages=pages, name=name, page=page, lesson_del=lesson_del)


@app.route('/lesson/<int:lesson>')
def lesson(lesson):  # форма урока
    start = datetime.datetime.now()
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    [remove(f"static/img/top_images/{i}") for i in listdir("static/img/top_images") if
     i.split("_")[0] == str(id) and i.split(".")[-1] == 'png']
    db_sess = db_session.create_session()
    print("LESSON", lesson)
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson).first()
    with open(f'static/img/top_images/{id}_{lesson.id}.png', 'wb') as file:
        file.write(lesson.top_image)
    images = []
    if lesson.items is None:
        lesson.items = ""
    if lesson.images:
        for i in lesson.images.split(","):
            img = db_sess.query(Image).filter(Image.id == i).first()
            open(f'static/img/all_images/{i}.png', 'wb').write(img.image)
        images = [i + ".png" for i in lesson.images.split(",")]
    try:
        db_sess = db_session.create_session()
        name = db_sess.query(User).filter(User.id == id).one()
        name = name.nickname
    except sqlalchemy.orm.exc.NoResultFound:
        name = ''
    finally:
        db_sess.commit()
    print(datetime.datetime.now() - start)
    return render_template("lesson.html", id=id, lesson=lesson, images=images, test=lesson.test,
                           name=name)


@app.route('/')
def choice():  # выбор входа или регистрации
    return render_template("choice.html")


@app.route('/entry', methods=['GET', 'POST'])
def entry():  # форма для входа
    form = EntryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        us = None
        for user in db_sess.query(User).all():
            if user.email == form.email.data and check_password_hash(user.hashed_password, form.password.data):
                us = user
                break
        if us is None:
            return render_template('entry.html', form=form, message="Такой пользователь не найден")
        login_user(us, remember=True)
        return redirect('/weblearn')
    return render_template('entry.html', form=form)


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():  # форма для добавления вопроса в тест
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    form = QuestionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        x = form.image.data
        if x is None:
            x = open("static/img/tests_images/0.png", "rb").read()
        else:
            x = x.read()
        question = Question(
            question=form.question.data,
            variants_f=form.variants_f.data,
            variants_s=form.variants_s.data,
            variants_t=form.variants_t.data, right=int(request.form['var']),
            variants_fo=form.variants_fo.data, image=resize(x))
        db_sess.add(question)
        db_sess.commit()
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.author_id == id, Test.created == 1).one()
        q = db_sess.query(Question).all()[-1]
        print("NEW_QUESTION", q.id)
        print("TEST", test.id)
        if test.questions == "":
            test.questions = str(q.id)
        else:
            test.questions += "," + str(q.id)
        db_sess.add(test)
        db_sess.commit()
    try:
        db_sess = db_session.create_session()
        name = db_sess.query(User).filter(User.id == id).one()
        name = name.nickname
    except sqlalchemy.orm.exc.NoResultFound:
        name = ''
    finally:
        db_sess.commit()
    print(datetime.datetime.now() - start)
    return render_template('add_question.html', form=form, id=id, name=name)


@app.route('/test/<int:lesson>', methods=['GET', 'POST'])
@app.route('/test/<int:lesson>/<int:page>', methods=['GET', 'POST'])
def test(lesson, page=1):  # Форма теста
    start = datetime.datetime.now()
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    db_sess = db_session.create_session()
    test = None
    try:
        test = db_sess.query(Lesson).filter(Lesson.id == lesson).one()
        print("Проверка", test)
        '''for i in db_sess.query(Lesson).all():
            if i.id == lesson:
                test = i.test
                break'''
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(f'/lesson/{lesson}')
    '''for i in db_sess.query(Test).all():
        print("Все тесты:", i.id, test, str(i.id) == str(test), i.questions)
        if str(i.id) == str(test):
            print("TRUE")
            test = int(i.id)
            break'''
    if test is None:
        return redirect(f'/lesson/{lesson}')
    test = db_sess.query(Test).filter(Test.id == test.test).one()
    print("TEST", test)
    question = ''
    print(request.method, page)
    try:
        db_sess = db_session.create_session()
        name = db_sess.query(User).filter(User.id == id).one()
        name = name.nickname
    except sqlalchemy.orm.exc.NoResultFound:
        name = ''
    finally:
        db_sess.commit()
    try:
        if request.method == 'POST':
            m = test.questions.split(",")[page - 1]
            print("Вопросы:", m)
            i = db_sess.query(Question).filter(Question.id == int(m)).one()
            session[f"{id}_{page}"] = i.right == int(request.form['var'])
            '''for i in db_sess.query(Question).all():
                if i.id == int(m):
                    session[f"{id}_{page}"] = i.right == int(request.form['var'])
                    break'''
            print(str(page) + ":", session.get(f"{id}_{page}", None))
            return redirect(f'/test/{lesson}/{page + 1}')
        if not page:
            raise IndexError
        m = test.questions.split(",")[page - 1]
        questions = db_sess.query(Question).filter(Question.id == int(m)).first()
        varia = [questions.variants_f, questions.variants_s, questions.variants_t,
                 questions.variants_fo]
        question = questions.question
        with open(f"static/img/tests_images/{lesson}_{page}.png", "wb") as file:
            file.write(questions.image)
    except IndexError:
        s = [0, 0, 0]
        print("Результаты:")
        print(test.questions)
        for i in range(1, 1 + len(test.questions.split(","))):
            print(session.get(f"{str(id)}_{i}", None))
            if session.get(f"{str(id)}_{i}", None) is None:
                s[2] += 1
            elif session.get(f"{str(id)}_{i}", None):
                s[0] += 1
            else:
                s[1] += 1
            session.pop(f"{str(id)}_{i}", None)
        print(s[0] / sum(s), s[1] / sum(s), s[2] / sum(s))
        [remove(f"static/img/tests_images/{i}") for i in listdir("static/img/tests_images") if
         i.split("_")[0] == str(lesson) and i.split(".")[-1] == 'png']
        print(datetime.datetime.now() - start)
        return render_template('end_test.html', id=id, t=round(s[0] / sum(s) * 100, 2), name=name,
                               f=round(s[1] / sum(s) * 100, 2), n=round(s[2] / sum(s) * 100, 2))  # результаты теста
    print(datetime.datetime.now() - start)
    return render_template('test.html', varia=varia, id=id, lesson=lesson, page=page,
                           question=question, name=name)  # новый вопрос теста


@app.route('/add', methods=['GET', 'POST'])
def add():  # форма для добавления теста
    start = datetime.datetime.now()
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    db_sess = db_session.create_session()
    if not id:
        [remove(f"static/img/top_images/{i}") for i in listdir("static/img/top_images") if
         i.split("_")[0] == str(id) and i != "0.png" and i.split(".")[-1] == 'png']
        [remove(f"static/img/all_images/{i}") for i in listdir("static/img/all_images") if
         i.split("_")[0] == str(id) and i != "0.png" and i.split(".")[-1] == 'png']
        return render_template('none.html', id=id)
    ERROR = ""
    form = LessonForm()
    if form.validate_on_submit():
        [remove(f"static/img/top_images/{i}") for i in listdir("static/img/top_images") if
         i.split("_")[0] == str(id) and i != "0.png" and i.split(".")[-1] == 'png']
        [remove(f"static/img/all_images/{i}") for i in listdir("static/img/all_images") if
         i.split("_")[0] == str(id) and i != "0.png" and i.split(".")[-1] == 'png']
        img = []
        if len(db_sess.query(Test).filter(Test.author_id == id, Test.questions == "",
                                          Test.created == 1).all()):
            ERROR = "Нельзя создавать несколько тестов одновременно"
            return render_template('add.html', form=form, id=id, err=ERROR)
        for i in form.images.data:
            image = i.read()
            if image == b'':
                continue
            im = db_sess.query(Image).filter(Image.image == image).first()
            if im is not None:
                img.append(im.id)
            else:
                imag = Image(image=image)
                db_sess.add(imag)
                db_sess.commit()
                db_sess = db_session.create_session()
                d = db_sess.query(Image).filter(Image.image == image).first()
                img.append(d.id)
        test_id = ""
        if form.test.data:
            test = Test(author_id=id, questions='')
            db_sess.add(test)
            db_sess.commit()
            db_sess = db_session.create_session()
            i = db_sess.query(Test).filter(Test.author_id == id, Test.created == 1).one()
            test_id = str(i.id)
        print("Создан тест номер:", test_id)
        x = form.top_image.data
        if x is None:
            print(1)
            x = open("static/img/top_images/0.png", "rb")
        lesson = Lesson(author_id=id, title=form.title.data, top_image=resize(x.read()),
                        text=form.text.data, images=",".join([str(i) for i in img]),
                        test=test_id, items=form.items.data.strip("#"))
        db_sess.add(lesson)
        db_sess.commit()
        if test_id != "":
            return redirect(f'/add_question')
        else:
            return redirect('/weblearn')
    try:
        db_sess = db_session.create_session()
        name = db_sess.query(User).filter(User.id == id).one()
        name = name.nickname
    except sqlalchemy.orm.exc.NoResultFound:
        name = ''
    finally:
        db_sess.commit()
    print(datetime.datetime.now() - start)
    return render_template('add.html', form=form, id=id, err=ERROR, name=name)


@app.route('/register', methods=['GET', 'POST'])
def register():  # форма для регистрации
    start = datetime.datetime.now()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message="Такой пользователь уже есть")
        x = form.image.data
        if x is None:
            x = open("static/img/user_images/0.png", "rb")
        user = User(
            nickname=form.nickname.data,
            email=form.email.data,
            city_from=form.city_from.data,
            image=resize(x.read(), width=450, height=400),
            about=form.about.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        print(datetime.datetime.now() - start)
        return redirect('/weblearn')
    print(datetime.datetime.now() - start)
    return render_template('register.html', title='Регистрация', form=form)


"""*********************Подключение API*******************************"""
api.add_resource(LessonResource, '/api/v1/lesson/<int:lesson_id>/<title>')
api.add_resource(LessonsResource, '/api/v1/lessons')
api.add_resource(UsersResource, '/api/v2/users/<int:user_id>')
api.add_resource(UsersListResource, '/api/v2/users')
"""*******************************************************************"""


def main():
    db_session.global_init()
    try:
        mkdir("static/img/top_images")
    except FileExistsError:
        pass
    if 'HEROKU' in environ:
        port = int(environ.get("PORT", 5000))
        print(port)
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(port=8080, host='127.0.0.1', debug=False)
    rmdir("static/img/top_images")


if __name__ == "__main__":
    main()
