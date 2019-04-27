from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    text = TextAreaField('Comment:')
    email = StringField('Email')
    recaptcha = RecaptchaField(validators=[DataRequired()])
    comment_submit = SubmitField('Submit')


class Search(FlaskForm):
    term = StringField('Name:', validators=[DataRequired()])
    search_submit = SubmitField('Submit')