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
from data import db_session
from data.lessons import Lesson
from os import listdir, remove, rmdir, mkdir, environ, path
from PIL import Image as Imagepil
import sqlalchemy

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'my_secret_key'


def resize(pic, width=700, height=450):
    with open("static/img/0.png", "wb") as file:
        file.write(pic)
    im = Imagepil.open("static/img/0.png")
    im = im.resize((width, height))
    im.save("static/img/0.png")
    im = open("static/img/0.png", "rb").read()
    remove("static/img/0.png")
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


@app.route('/weblearn')
@app.route('/weblearn/page=<int:page>')
def weblearn(page=1):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    # print(vars(current_user))
    # print(session.items())
    db_sess = db_session.create_session()
    x = db_sess.query(Test).filter(Test.author_id == str(id), Test.questions == f"user_{id}").all()
    while len(x):
        try:
            for i in db_sess.query(Lesson).filter(Lesson.test == str(x[0].id)).all():
                i.test = ""
                db_sess.commit()
            db_sess.delete(x[0])
            db_sess.commit()
        except sqlalchemy.exc.InvalidRequestError:
            pass
        finally:
            db_sess = db_session.create_session()
            x = db_sess.query(Test).filter(Test.author_id == str(id),
                                           Test.questions == f"user_{id}").all()
    if id:
        im = db_sess.query(User).filter(User.id == id).first()
        with open(f"static/img/user_images/{id}.png", "wb") as file:
            file.write(im.image)
    lessons = db_sess.query(Lesson).all()[(page - 1) * 12:page * 12]
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
    print(pages)
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
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson).first()
    open(f'static/img/top_images/{lesson.id}.png', 'wb').write(lesson.top_image)
    print(lesson.images)
    for i in lesson.images.split(","):
        img = db_sess.query(Image).filter(Image.id == i).first()
        print(i, img)
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
            if user.nickname == form.nickname.data and check_password_hash(user.hashed_password,
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
    print("!!!!", vars(current_user))
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    form = QuestionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        print()
        x = form.image.data
        if x is None:
            x = open("static/img/user_images/0.png", "rb").read()
        else:
            x = x.read()
        question = Question(
            question=form.question.data,
            variants_f=form.variants_f.data,
            variants_s=form.variants_s.data,
            variants_t=form.variants_t.data, right=int(request.form['var']),
            variants_fo=form.variants_fo.data, image=resize(x))
        # print(question.image)
        db_sess.add(question)
        db_sess.commit()
        print("-" * 100)
        print(question.id)
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.author_id == f"{id}").first()
        print(test.questions)
        print(vars(question))
        if test.questions == f"user_{id}":
            test.questions = str(question.id)
        else:
            test.questions += "," + str(question.id)
        db_sess.add(test)
        db_sess.commit()
    return render_template('add_question.html', form=form, id=id)


@app.route('/test/<int:lesson>', methods=['GET', 'POST'])
@app.route('/test/<int:lesson>/<int:page>', methods=['GET', 'POST'])
def test(lesson, page=0):
    db_sess = db_session.create_session()
    test = db_sess.query(Lesson).filter(Lesson.id == lesson).first()
    print(test)
    test = db_sess.query(Test).filter(Test.id == int(test.test)).first()
    print(test)
    try:
        m = test.questions.split(",")[page]
        test = db_sess.query(Question).filter(Question.id == int(m)).first()
        varia = [test.variants_f, test.variants_s, test.variants_t, test.variants_fo]
    except IndexError:
        return "тест окончен"
    return render_template('test.html', varia=varia, id=id, lesson=lesson, page=page)


@app.route('/add', methods=['GET', 'POST'])
def add():
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    db_sess = db_session.create_session()
    if db_sess.query(Test).filter(Test.author_id == str(id),
                                  Test.questions == f"user_{id}").first() is not None:
        return "Нельзя создавать несколько тестов одновременно"
    if not id:
        [remove(f"static/img/top_images/{i}") for i in listdir("static/img/top_images") if
         i.split("_")[0] == str(id) and i.split(".")[-1] == 'png']
        [remove(f"static/img/all_images/{i}") for i in listdir("static/img/all_images") if
         i.split("_")[0] == str(id) and i.split(".")[-1] == 'png']
        return render_template('none.html', id=id)
    print("?", id)
    form = LessonForm()
    if form.validate_on_submit():
        [remove(f"static/img/top_images/{i}") for i in listdir("static/img/top_images") if
         i.split("_")[0] == str(id) and i.split(".")[-1] == 'png']
        [remove(f"static/img/all_images/{i}") for i in listdir("static/img/all_images") if
         i.split("_")[0] == str(id) and i.split(".")[-1] == 'png']
        img = []
        for i in form.images.data:
            image = i.read()
            im = db_sess.query(Image).filter(Image.image == image).all()
            if len(im):
                print(im[0])
                img.append(im[0].id)
            else:
                imag = Image(image=image)
                db_sess.add(imag)
                d = db_sess.query(Image).filter(Image.image == image).first()
                img.append(d.id)
        test_id = ""
        if form.test.data:
            print(1)
            test = Test(author_id=id, questions=f'user_{id}')
            print(2)
            db_sess.add(test)
            print(3)
            db_sess.commit()
            print(4)
            db_sess = db_session.create_session()
            test_id = str(test.id)
        lesson = Lesson(
            author_id=id,
            title=form.title.data,
            top_image=resize(form.top_image.data.read()),
            text=form.text.data,
            images=",".join([str(i) for i in img]), test=test_id)
        db_sess.add(lesson)
        db_sess.commit()
        if form.test.data:
            return redirect(f'/add_question')
        else:
            return redirect('/weblearn')
    return render_template('add.html', form=form, id=id)


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
        print(user.id)
        print(f'/weblearn/{user.id}')
        session.get('form.email.data', True)
        return redirect('/weblearn')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init()
    # app.register_blueprint(news)
    try:
        mkdir("static/img/top_images")
    except FileExistsError:
        pass
    if 'HEROKU' in environ:
        port = int(environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(port=8080, host='127.0.0.1', debug=True)
    rmdir("static/img/top_images")


if __name__ == "__main__":
    main()
