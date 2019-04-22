from alambi.models import User, Tag, Theme
from alambi.utils import ThemeName
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileAllowed
from wtforms import (StringField, BooleanField, TextAreaField, SubmitField, SelectField,
                     RadioField, FileField, PasswordField, IntegerField)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class AdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create New User')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class TagField(StringField):

    def _value(self):
        if self.data:
            # Display tags as a comma separated list
            return ', '.join([tag.name for tag in self.data])
        return ''

    def get_tags_from_string(self, tag_string):
        raw_tags = tag_string.split(',')

        # filter empty tag names
        tag_names = [name.strip() for name in raw_tags if name.strip()]

        # query for already existing tags
        existing_tags = Tag.query.filter(Tag.name.in_(tag_names))

        # separate out the new names
        new_names = set(tag_names) - set([tag.name for tag in existing_tags])

        # create a list of unsaved tags
        new_tags = [Tag(name=name) for name in new_names]

        # return all the existing tags and all unsaved tags
        return list(existing_tags) + new_tags

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.get_tags_from_string(valuelist[0])
        else:
            self.data = []


class GeneralSettingsForm(FlaskForm):
    blog_name = StringField('Blog Name:', validators=[DataRequired()])
    author_name = StringField('Author Name:', validators=[DataRequired()])
    post_count = IntegerField('Post Count:', validators=[DataRequired()])
    excerpt = BooleanField('Excerpt:')
    comments = BooleanField('Show Comments:')
    submit = SubmitField('Apply')


class SidebarSettingsForm(FlaskForm):
    main_position = RadioField('Position on Main Page:', coerce=int,
                               choices=[(1 ,'Left'),(2,'Right'),(3,'None')])
    post_position = RadioField('Position on Post Page:', coerce=int,
                               choices=[(1,'Left'),(2,'Right'),(3,'None')])
    img = FileField('Main Image:', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    text = TextAreaField('Text:')
    search = BooleanField('Show Search Bar:')
    recent_posts = BooleanField('Show Links to Recent Posts:')
    max_recent = IntegerField('Max Recent Posts Shown:', validators=[DataRequired()])
    popular_posts = BooleanField('Show Links to Popular Posts:')
    max_popular = IntegerField('Max Popular Posts Shown:', validators=[DataRequired()])
    category = BooleanField('Show Categories:')
    max_category = IntegerField('Max Categories Shown:', validators=[DataRequired()])
    tag = BooleanField('Show Tags:')
    max_tag = IntegerField('Max Tags Shown:', validators=[DataRequired()])
    submit = SubmitField('Apply', validators=[DataRequired()])


class NewThemeForm(FlaskForm):
    name = StringField('Theme Name:', validators=[DataRequired()])
    bg_color = StringField('Background Color:', validators=[DataRequired()])
    text_color = StringField('Text Color:', validators=[DataRequired()])
    post_container_color = StringField('Post Container Color:', validators=[DataRequired()])
    blog_name_color = StringField('Blog Name Color:', validators=[DataRequired()])
    header_color = StringField('Header Color:', validators=[DataRequired()])
    alt_header_color = StringField('Alt-Header Color:', validators=[DataRequired()])
    link_color = StringField('Link Color:', validators=[DataRequired()])
    like_color = StringField('Like Color:', validators=[DataRequired()])
    comment_color = StringField('Comment Submit Color:', validators=[DataRequired()])
    sticky_color = StringField('Pin Button Color:', validators=[DataRequired()])
    main_font = StringField('Main Font:', validators=[DataRequired()])
    header_font = StringField('Header Font:', validators=[DataRequired()])
    submit1 = SubmitField('Apply')


class ThemeSelectForm(FlaskForm):

    theme = ThemeName()

    selection = SelectField('Choose a theme:', coerce=int,
                               choices=[(1, theme.one.name),(2, theme.two.name),(3, theme.three.name),(4, theme.four.name),
                                        (5, theme.five.name),(6, theme.six.name),(7, theme.seven.name),(8, theme.eight.name)])
    submit2 = SubmitField('Apply')


class Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('That email address does not exist. Register for a new account.')


class ResetPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class NewBlogPost(FlaskForm):
    post_name = StringField('Name:', validators=[DataRequired()])
    content = TextAreaField('Blog Content:')
    category = StringField('Category:', validators=[DataRequired()])
    tags = TagField('Tags:', description='Separate tags with commas')
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired()])
    text = TextAreaField('Comment:')
    email = StringField('Email')
    recaptcha = RecaptchaField(validators=[DataRequired()])
    comment_submit = SubmitField('Submit')


class Search(FlaskForm):
    term = StringField('Name:', validators=[DataRequired()])
    search_submit = SubmitField('Submit')


class InitializationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    blog_name = StringField('Blog Name:', validators=[DataRequired()])
    author_name = StringField('Your Name:', validators=[DataRequired()])
    submit = SubmitField('Submit')
