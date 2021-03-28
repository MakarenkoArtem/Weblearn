from flask import Flask, render_template, url_for, redirect, request
from data import db_session
from forms.user import RegisterForm
from forms.lesson import LessonForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/weblearn')
def index():
    return render_template("weblearn.html")


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = LessonForm()
    print(form)
    if form.validate_on_submit():
        form.image.data.save("1.png")
        return redirect('/weblearn')
    return render_template('add.html', form=form)

@app.route('/', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
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
        return redirect('/weblearn')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/base_date.db")
    app.run(port=8080, host='127.0.0.1', debug=True)
