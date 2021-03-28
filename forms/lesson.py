from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class LessonForm(FlaskForm):
    title = StringField('Название урока', validators=[DataRequired()])
    text = TextAreaField("Текст урока", validators=[DataRequired()])
    image = FileField('Картинка',
                       validators=[FileRequired(), FileAllowed(['jpg', 'png', "bmp"], 'Images only!')])
    submit = SubmitField('Сохранить')
