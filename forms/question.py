from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, TextAreaField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    question = StringField('Вопрос', validators=[DataRequired()])
    variants_f = StringField('Вариант 1', validators=[DataRequired()])
    variants_s = StringField('Вариант 2', validators=[DataRequired()])
    variants_t = StringField('Вариант 3', validators=[DataRequired()])
    variants_fo = StringField('Вариант 4', validators=[DataRequired()])
    image = FileField('Картинка', validators=[FileAllowed(['jpg', 'png', "bmp"], 'Images only!')])
    submit = SubmitField('Добавить вопрос')
#multiple