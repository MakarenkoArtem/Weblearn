from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, TextAreaField, SubmitField, BooleanField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired


class LessonForm(FlaskForm):
    title = StringField('Название урока', validators=[DataRequired()])
    top_image = FileField('Главная картинка',
                       validators=[FileAllowed(['jpg', 'png', "bmp"], 'Images only!')])
    text = TextAreaField("Текст урока", validators=[DataRequired()])
    images = MultipleFileField('Картинки',
                       validators=[FileAllowed(['jpg', 'png', "bmp"], 'Images only!')])
    test = BooleanField('Создать тест')
    submit = SubmitField('Сохранить')
#multiple