from flask import (render_template, request, flash,
                   redirect, url_for, make_response, Blueprint)
from flask_mail import Message
from alambi import db, mail, recaptcha
from alambi.models import Blog, Comment, Tag, GeneralSettings, SidebarSettings, Theme
from alambi.main.forms import Search, CommentForm
import os


main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
def index():

    general_settings = GeneralSettings.query.first()

    if not general_settings.init:
        return redirect(url_for('users.init'))


    sidebar_settings = SidebarSettings.query.first()
    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    page = request.args.get('page', 1, type=int)
    post_count = general_settings.post_count
    posts = Blog.query.order_by(Blog.sticky.desc(), Blog.date.desc()).paginate(page=page, per_page=post_count)


    popular_posts = Blog.query.order_by(Blog.like.desc(), Blog.comment_count.desc()).limit(sidebar_settings.max_popular).all()
    recent_posts = Blog.query.order_by(Blog.date.desc()).limit(sidebar_settings.max_recent).all()
    categories = Blog.query.group_by(Blog.category).limit(sidebar_settings.max_category).all()
    tags = Tag.query.group_by(Tag.name).limit(sidebar_settings.max_tag).all()
    search_form = Search()
    if request.method == 'POST':
        if search_form.validate_on_submit:
            return redirect(url_for('main.query', term=search_form.term.data))

    return render_template('index.html', title=general_settings.name + " - Home", posts=posts,
                           general_settings=general_settings, sidebar_settings=sidebar_settings,
                           theme_settings=theme_settings, search_form=search_form,
                           categories=categories, tags=tags,
                           recent_posts=recent_posts, popular_posts=popular_posts,
                           main_font=main_font, head_font=head_font)


@main.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):

    general_settings = GeneralSettings.query.first()
    sidebar_settings = SidebarSettings.query.first()
    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    post = Blog.query.get_or_404(post_id)
    name = 'post' + str(post_id) + 'like'
    state = request.cookies.get(name)
    like = False
    if state == 'true':
        like = True

    prev = post_id - 1
    next = post_id + 1

    prev_post = False
    next_post = False

    if Blog.query.get(prev):
        prev_post = Blog.query.get_or_404(prev)

    if Blog.query.get(next):
        next_post = Blog.query.get_or_404(next)

    form = CommentForm()
    search_form = Search()

    if request.method == 'POST':

        if form.comment_submit.data:
            if form.validate_on_submit:
                # if recaptcha.verify():

                comment = Comment(name=form.name.data,
                                  email=form.email.data,
                                  text=form.text.data,
                                  post=post
                                  )

                post.comment_count += 1

                db.session.add(comment)
                db.session.commit()
                recip = os.getenv("MAIL_USER")
                msg = Message("New comment from " + general_settings.name, sender='noreply@alambi-blog.com', recipients=[recip])
                msg.body = '''
                From: %s <%s>
                %s
                %s
                ''' % (form.name.data, form.email.data, form.text.data, url_for('main.post', post_id=post_id, _external=True))

                mail.send(msg)

                flash("Thank you for the comment! Check back soon for a reply!")

                return redirect(url_for('main.post', post_id=post_id))

        elif search_form.validate_on_submit:
            return redirect(url_for('main.query', term=search_form.term.data))

    comments = Comment.query.filter(Comment.post_id == post_id).order_by(Comment.date.desc()).all()

    # for the sidebar
    popular_posts = Blog.query.order_by(Blog.like.desc()).limit(sidebar_settings.max_popular).all()
    recent_posts = Blog.query.order_by(Blog.date.desc()).limit(sidebar_settings.max_recent).all()
    categories = Blog.query.group_by(Blog.category).limit(sidebar_settings.max_category).all()
    tags = Tag.query.group_by(Tag.name).limit(sidebar_settings.max_tag).all()



    return render_template('post.html', post=post, prev_post=prev_post, next_post=next_post, search_form=search_form,
                           title=post.name, form=form, comments=comments, general_settings=general_settings,
                           sidebar_settings=sidebar_settings, categories=categories, tags=tags, recent_posts=recent_posts,
                           like=like, popular_posts=popular_posts, theme_settings=theme_settings,
                           main_font=main_font, head_font=head_font)


@main.route('/query/<term>', methods=['GET', 'POST'])
def query(term):

    general_settings = GeneralSettings.query.first()
    sidebar_settings = SidebarSettings.query.first()
    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    tag_query = Tag.query.filter_by(name=term).all()
    text_query = Blog.query.filter((Blog.text.contains(term)) | (Blog.name.contains(term)) | Blog.category.contains(term)).all()

    id_list = []
    tag_posts = []


    if tag_query:
        got_tags = tag_query[0].post_tags.all()
        for tags in got_tags:
            if tags.blog_id in id_list:
                pass
            else:
                id_list.append(tags.blog_id)

    if text_query:
        for post in text_query:
            if post.blog_id in id_list:
                pass
            else:
                id_list.append(post.blog_id)

    id_list.sort(reverse=True)


    for id in id_list:
        tag_posts.append(Blog.query.filter_by(blog_id=id).all())

    # for the sidebar
    popular_posts = Blog.query.order_by(Blog.like.desc()).limit(sidebar_settings.max_popular).all()
    recent_posts = Blog.query.order_by(Blog.date.desc()).limit(sidebar_settings.max_recent).all()
    categories = Blog.query.group_by(Blog.category).limit(sidebar_settings.max_category).all()
    tags = Tag.query.group_by(Tag.name).limit(sidebar_settings.max_tag).all()
    search_form = Search()
    if request.method == 'POST':
        if search_form.validate_on_submit:
            return redirect(url_for('main.query', term=search_form.term.data))


    return render_template('query.html', title='Search:' + term, tag_posts=tag_posts, general_settings=general_settings,
                           sidebar_settings=sidebar_settings, search_form=search_form, categories=categories,
                           tags=tags, recent_posts=recent_posts, popular_posts=popular_posts,
                           theme_settings=theme_settings, main_font=main_font, head_font=head_font)


@main.route('/sticky/<post_id>')
def sticky(post_id):
    post = Blog.query.get_or_404(post_id)

    if post.sticky:
        post.sticky = False
        msg = 'This post is not pinned anymore!'
    elif post.sticky == False:
        post.sticky = True
        msg = 'You pinned this post!'

    db.session.commit()

    flash(msg, 'success')
    return redirect(url_for('main.post', post_id=post_id))


@main.route('/like/<post_id>')
def like(post_id):

    resp = make_response(redirect(url_for('main.post', post_id=post_id)))
    name = 'post' + post_id + 'like'
    post = Blog.query.get_or_404(post_id)

    state = request.cookies.get(name)
    if state == 'true':
        resp.set_cookie(name, 'false')
        if post.like > 0:
            post.like -= 1
    else:
        resp.set_cookie(name, 'true')
        post.like += 1

    db.session.commit()

    return resp