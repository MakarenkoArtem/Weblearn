from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, TextAreaField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    title = StringField('Название урока', validators=[DataRequired()])
    top_image = FileField('Главная картинка',
                       validators=[FileRequired(), FileAllowed(['jpg', 'png', "bmp"], 'Images only!')])
#multiple