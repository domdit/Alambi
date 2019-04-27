from alambi import db, app
from flask_login import UserMixin
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import datetime


migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return "User('{self.email}')"


tags = db.Table('tags',
                db.Column('blog_id', db.Integer, db.ForeignKey('blog.blog_id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id'))
                )


class Blog(db.Model):
    blog_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    text = db.Column(db.Text)
    like = db.Column(db.Integer, default=0)
    sticky = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(200), default='No Category')
    tags = db.relationship('Tag', secondary=tags,
                           backref=db.backref('post_tags', lazy='dynamic'))
    comments = db.relationship("Comment", backref='post', cascade="all, delete-orphan")
    comment_count = db.Column(db.Integer, default=0)

class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog.blog_id'))
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    text = db.Column(db.Text)


class GeneralSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    init = db.Column(db.Boolean, unique=False, default=False, nullable=True)
    name = db.Column(db.String(500), unique=False, nullable=False)
    author = db.Column(db.String(500), unique=False, nullable=False)
    post_count = db.Column(db.Integer)
    excerpt = db.Column(db.Boolean, unique=False, default=False, nullable=True)
    comments = db.Column(db.Boolean, unique=False, default=False, nullable=True)


class SidebarSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    main_position = db.Column(db.Integer, default=2, nullable=False)
    post_position = db.Column(db.Integer, default=2, nullable=False)
    show_blog_name = db.Column(db.Boolean, nullable=True)
    show_logo = db.Column(db.Boolean, nullable=True)
    text = db.Column(db.Text)
    search = db.Column(db.Boolean, default=True, nullable=True)
    recent_posts = db.Column(db.Boolean, default=True, nullable=True)
    max_recent = db.Column(db.Integer, default=3, nullable=True)
    popular_posts = db.Column(db.Boolean, default=True, nullable=True)
    max_popular = db.Column(db.Integer, default=3, nullable=True)
    category = db.Column(db.Boolean, default=True, nullable=True)
    max_category = db.Column(db.Integer, default=5, nullable=True)
    tag = db.Column(db.Boolean, default=True, nullable=True)
    max_tag = db.Column(db.Integer, default=5, nullable=True)


class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    selected = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(500), unique=False, nullable=False)
    bg_color = db.Column(db.String(10), unique=False, nullable=False)
    text_color = db.Column(db.String(10), unique=False, nullable=False)
    post_container_color = db.Column(db.String(10), unique=False, nullable=False)
    blog_name_color = db.Column(db.String(10), unique=False, nullable=False)
    header_color = db.Column(db.String(10), unique=False, nullable=False)
    alt_header_color = db.Column(db.String(10), unique=False, nullable=False)
    link_color = db.Column(db.String(10), unique=False, nullable=False)
    like_color = db.Column(db.String(10), unique=False, nullable=False)
    comment_color = db.Column(db.String(10), unique=False, nullable=False)
    sticky_color = db.Column(db.String(10), unique=False, nullable=False)
    main_font = db.Column(db.String(200), unique=False, nullable=False)
    header_font = db.Column(db.String(200), unique=False, nullable=False)


if __name__ == '__main__':
    manager.run()