from flask import Flask, render_template, url_for, redirect, request, session
from data import db_session
from werkzeug.security import generate_password_hash
from forms.user import RegisterForm, EntryForm
from forms.lesson import LessonForm
from data.users import User
from data.lessons import Lesson
from os import listdir, remove, rmdir, mkdir, environ


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    print(session)
    return f"Вы пришли на эту страницу {visits_count + 1} раз"

@app.route('/weblearn/<int:id>')
def weblearn(id):
    db_sess = db_session.create_session()
    lessons = db_sess.query(Lesson).all()[:9]
    texts = []
    k = 1
    for i in lessons:
        image = open(f'static/img/top_images/{id}_{k}.png', 'wb')
        image.write(i.top_image)
        texts.append(i.text.split("\r")[0][:21] + "...")
        k += 1
    return render_template("weblearn.html", id=id, lessons=lessons, texts=texts)

@app.route('/lesson/<int:lesson>/<int:id>')
def lesson(lesson, id):
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson).first()
    open(f'static/img/top_images/{lesson.author_id}_{lesson.id}.png', 'wb').write(lesson.top_image)
    images = lesson.images.split(", ")
    return render_template("lesson.html", id=id, lesson=lesson, images=images)

@app.route('/')
def choice():
    return render_template("choice.html")


@app.route('/entry', methods=['GET', 'POST'])
def entry():
    form = EntryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.nickname == form.nickname.data, User.hashed_password == generate_password_hash(
                form.password.data)).first()
        if user is None:
            return render_template('entry.html',
                                   form=form,
                                   message="Такой пользователь не найден")
        redirect(f'/weblearn/{user.id}')
    return render_template('entry.html', form=form)


@app.route('/add/<int:id>', methods=['GET', 'POST'])
def add(id):
    print("?", id)
    form = LessonForm()
    if form.validate_on_submit():
        k = 1
        dirs = [int(i.split("_")[-1].split(".")[0]) for i in listdir("static/img/all_images") if
                i.split("_")[0] == str(id) and i.split(".")[-1] == 'jpg']
        print(dirs)
        dirs.sort()
        if len(dirs):
            k = dirs[-1] + 1
        img = []
        for i in form.images.data:
            i.save(f"static/img/all_images/{id}_{k}.jpg")
            img.append(str(f'{id}_{k}.jpg'))
            k += 1
        form.top_image.data.save('static/img/test.png')
        im = open("static/img/test.png", 'rb')
        lesson = Lesson(
            author_id=id,
            title=form.title.data,
            top_image=im.read(),
            text=form.text.data,
            images=", ".join(img))
        remove("static/img/test.png")
        db_sess = db_session.create_session()
        db_sess.add(lesson)
        db_sess.commit()
        return redirect(url_for('.weblearn', id=id))
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
        user = User(
            nickname=form.nickname.data,
            email=form.email.data,
            city_from=form.city_from.data,
            about=form.about.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        print(user.id)
        print(f'/weblearn/{user.id}')
        return redirect(url_for('.weblearn', id=user.id))
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    try:
        mkdir("static/img/top_images")
    except FileExistsError:
        pass
    db_session.global_init("db/base_date.db")
    if 'HEROKU' in environ:
        port = int(environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(port=8080, host='127.0.0.1', debug=True)
    rmdir("static/img/top_images")
