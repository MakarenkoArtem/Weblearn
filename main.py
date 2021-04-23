from flask import Flask, render_template, url_for, redirect, request, session, jsonify, make_response
from flask_restful import Api
from flask_login import LoginManager, current_user, login_user
from werkzeug.security import check_password_hash
from forms.user import RegisterForm, EntryForm
from forms.lesson import LessonForm
from data.users import User
from data.questions import Question
from data.tests import Test
from data.images import Image
from forms.question import QuestionForm
from api import lesson_resource
from data import db_session
from data.lessons import Lesson
from os import listdir, remove, rmdir, mkdir, environ, path
from PIL import Image as Imagepil
import sqlalchemy
import datetime

app = Flask(__name__)
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=1)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'my_secret_key'


def resize(pic, width=700, height=450):
    return pic
    with open("static/img/!!!!!!!!0.png", "wb") as file:
        file.write(pic)
    im = Imagepil.open("static/img/!!!!!!!!0.png")
    im = im.resize((width, height))
    im.save("static/img/!!!!!!!!0.png")
    im = open("static/img/!!!!!!!!0.png", "rb").read()
    remove("static/img/!!!!!!!!0.png")
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
    return render_template("404.html", id=id)


@app.errorhandler(404)
def not_found(error):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    return render_template("404.html", id=id)


@app.route('/del/<int:lesson>')
def del_lesson(lesson):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    db_sess = db_session.create_session()
    d = db_sess.query(Lesson).filter(Lesson.author_id == id, Lesson.id == lesson).first()
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
    d = db_sess.query(Test).filter(Test.id == t).first()
    if d is None:
        return redirect('/weblearn')
    s = d.questions.split(",")
    for i in s:
        db_sess = db_session.create_session()
        d = db_sess.query(Question).filter(Question.id == int(i)).first()
        if d is None:
            continue
        db_sess.delete(d)
        db_sess.commit()
    return redirect('/weblearn')


@app.route('/weblearn')
@app.route('/weblearn/page=<int:page>')
def weblearn(page=1):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    db_sess = db_session.create_session()
    d = db_sess.query(Test).filter(Test.author_id == id, Test.created == 1).first()
    if d is not None:
        d.created = 0
        db_sess.commit()
        db_sess = db_session.create_session()
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
    return render_template("weblearn.html", id=id, img=img, lessons=lessons, texts=texts,
                           pages=pages)


@app.route('/lesson/<int:lesson>')
def lesson(lesson):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    [remove(f"static/img/top_images/{i}") for i in listdir("static/img/top_images") if
     i.split("_")[0] == str(id) and i.split(".")[-1] == 'png']
    db_sess = db_session.create_session()
    print("LESSON", lesson)
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson).first()
    print(lesson.id)
    with open(f'static/img/top_images/{id}_{lesson.id}.png', 'wb') as file:
        file.write(lesson.top_image)
    images = []
    if lesson.images:
        for i in lesson.images.split(","):
            img = db_sess.query(Image).filter(Image.id == i).first()
            open(f'static/img/all_images/{i}.png', 'wb').write(img.image)
        images = [i + ".png" for i in lesson.images.split(",")]

    return render_template("lesson.html", id=id, lesson=lesson, images=images, test=lesson.test)


@app.route('/')
def choice():
    return render_template("choice.html")


@app.route('/entry', methods=['GET', 'POST'])
def entry():
    form = EntryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        us = None
        for user in db_sess.query(User).all():
            if user.email == form.email.data and check_password_hash(user.hashed_password,
                                                                     form.password.data):
                us = user
                break
        if us is None:
            return render_template('entry.html',
                                   form=form,
                                   message="Такой пользователь не найден")
        login_user(us, remember=True)
        return redirect('/weblearn')
    return render_template('entry.html', form=form)


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
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
        q = str(question.id)
        db_sess.add(question)
        db_sess.commit()
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.author_id == id, Test.created == 1).first()
        print("TEST", test.id)
        if test.questions == "":
            test.questions = q
        else:
            test.questions += "," + q
        db_sess.add(test)
        db_sess.commit()
    return render_template('add_question.html', form=form, id=id)


@app.route('/test/<int:lesson>', methods=['GET', 'POST'])
@app.route('/test/<int:lesson>/<int:page>', methods=['GET', 'POST'])
def test(lesson, page=1):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    db_sess = db_session.create_session()
    print("TEST_LESSON", lesson)
    test = None
    for i in db_sess.query(Lesson).all():
        if i.id == lesson:
            test = i.test
            break
    if test is None:
        return redirect(f'/lesson/{lesson}')
    print(test is None)
    for i in db_sess.query(Test).all():
        print(i.id, test, i.questions)
        if i.id == test:
            test = i
            break
    test = db_sess.query(Test).filter(Test.id == test).first()
    print("TEST", test)
    question = ''
    print(request.method, page)
    if request.method == 'POST':
        m = test.questions.split(",")[page - 1]
        questions = db_sess.query(Question).filter(Question.id == int(m)).first()
        session[f"{id}_{page}"] = questions.right == int(request.form['var'])
        return redirect(f'/test/{lesson}/{page + 1}')
    try:
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
        for i in test.questions.split(","):
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
        return render_template('end_test.html', id=id, t=round(s[0] / sum(s) * 100, 2),
                               f=round(s[1] / sum(s) * 100, 2), n=round(s[2] / sum(s) * 100, 2))
    return render_template('test.html', varia=varia, id=id, lesson=lesson, page=page,
                           question=question)


@app.route('/add', methods=['GET', 'POST'])
def add():
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
            test_id = str(test.id)
            db_sess.add(test)
            db_sess.commit()
            db_sess = db_session.create_session()
        x = form.top_image.data
        if x is None:
            x = open("static/img/top_images/0.png", "rb")
        lesson = Lesson(author_id=id, title=form.title.data, top_image=resize(x.read()),
                        text=form.text.data, images=",".join([str(i) for i in img]),
                        test=test_id)
        db_sess.add(lesson)
        db_sess.commit()
        if test_id != "":
            return redirect(f'/add_question')
        else:
            return redirect('/weblearn')
    return render_template('add.html', form=form, id=id, err=ERROR)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="Такой пользователь уже есть")
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
        return redirect('/weblearn')
    return render_template('register.html', title='Регистрация', form=form)


api.add_resource(lesson_resource.LessonResource, '/api/v1/lesson/<int:lesson_id>')


def main():
    db_session.global_init()
    try:
        mkdir("static/img/top_images")
    except FileExistsError:
        pass
    if 'HEROKU' in environ:
        port = int(environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(port=8080, host='127.0.0.1', debug=False)
    rmdir("static/img/top_images")


if __name__ == "__main__":
    main()
