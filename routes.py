from alambi import app, db, mail, bcrypt, login_manager
from alambi.forms import (GeneralSettingsForm, NewThemeForm, Login, Search,
                          NewBlogPost, AdminForm, CommentForm, RequestResetForm,
                          ResetPassword, SidebarSettingsForm, ThemeSelectForm,
                          InitializationForm)
from alambi.models import (Blog, Comment, Tag, User, GeneralSettings, SidebarSettings,
                           Theme)
from alambi.utils import img_uploader
from alambi.local_settings import tinymce_api_key, mail_address
from flask import render_template, request, flash, redirect, url_for, make_response
from flask_login import logout_user, current_user, login_required, login_user
from flask_mail import Message
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.template_filter('autoversion')
def autoversion_filter(filename):
    path = 'alambi/' + filename[1:]

    try:
        timestamp = str(os.path.getmtime(path))
    except OSError:
        return filename

    newfile = "{0}?v={1}".format(filename, timestamp)
    print(newfile)
    return newfile


@app.route("/initialize", methods=['GET', 'POST'])
def init():

    form = InitializationForm()

    if request.method == 'POST':
        if form.validate_on_submit:

            admin = User.query.first()
            admin.email = form.email.data
            admin.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            settings = GeneralSettings.query.first()
            settings.name = form.blog_name.data
            settings.author = form.author_name.data
            settings.post_count = 3
            settings.excerpt = True
            settings.comments = True

            db.session.commit()
            return redirect(url_for('index'))

    return render_template('initialize.html', title="Welcome to Alambi", form=form)



@app.route("/", methods=['GET', 'POST'])
def index():

    general_settings = GeneralSettings.query.first()
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
            return redirect(url_for('query', term=search_form.term.data))

    return render_template('index.html', title=general_settings.name + " - Home", posts=posts,
                           general_settings=general_settings, sidebar_settings=sidebar_settings,
                           theme_settings=theme_settings, search_form=search_form,
                           categories=categories, tags=tags,
                           recent_posts=recent_posts, popular_posts=popular_posts,
                           main_font=main_font, head_font=head_font)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
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

    if request.method == 'POST':

        if form.comment_submit.data:
            if form.validate_on_submit:
                if recaptcha.verify():

                    comment = Comment(name=form.name.data,
                                      email=form.email.data,
                                      text=form.text.data,
                                      post=post
                                      )

                    post.comment_count += 1

                    db.session.add(comment)
                    db.session.commit()

                    msg = Message("New comment from " + general_settings.name, sender='noreply@alambi.com', recipients=[mail_address])
                    msg.body = '''
                    From: %s <%s>
                    %s
                    %s
                    ''' % (form.name.data, form.email.data, form.text.data, url_for('post', post_id=post_id, _external=True))

                    mail.send(msg)

                    flash("Thank you for the comment! Check back soon for a reply!")

                    return redirect(url_for('post', post_id=post_id))

    comments = Comment.query.filter(Comment.post_id == post_id).order_by(Comment.date.desc()).all()

    # for the sidebar
    popular_posts = Blog.query.order_by(Blog.like.desc()).limit(sidebar_settings.max_popular).all()
    recent_posts = Blog.query.order_by(Blog.date.desc()).limit(sidebar_settings.max_recent).all()
    categories = Blog.query.group_by(Blog.category).limit(sidebar_settings.max_category).all()
    tags = Tag.query.group_by(Tag.name).limit(sidebar_settings.max_tag).all()
    search_form = Search()
    if request.method == 'POST':
        if search_form.validate_on_submit:
            return redirect(url_for('query', term=search_form.term.data))


    return render_template('post.html', post=post, prev_post=prev_post, next_post=next_post, search_form=search_form,
                           title=post.name, form=form, comments=comments, general_settings=general_settings,
                           sidebar_settings=sidebar_settings, categories=categories, tags=tags, recent_posts=recent_posts,
                           like=like, popular_posts=popular_posts, theme_settings=theme_settings,
                           main_font=main_font, head_font=head_font)


@app.route('/query/<term>', methods=['GET', 'POST'])
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
            return redirect(url_for('query', term=search_form.term.data))


    return render_template('query.html', title='Search:' + term, tag_posts=tag_posts, general_settings=general_settings,
                           sidebar_settings=sidebar_settings, search_form=search_form, categories=categories,
                           tags=tags, recent_posts=recent_posts, popular_posts=popular_posts,
                           theme_settings=theme_settings, main_font=main_font, head_font=head_font)


@app.route('/sticky/<post_id>')
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
    return redirect(url_for('post', post_id=post_id))


@app.route('/like/<post_id>')
def like(post_id):

    resp = make_response(redirect(url_for('post', post_id=post_id)))
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

@app.route('/settings')
def settings_reroute():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('login'))

    return redirect(url_for('settings'))

@app.route("/settings/general/", methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('login'))

    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    form = GeneralSettingsForm()
    old_rules = GeneralSettings.query.first()

    if request.method == 'POST':
        if form.validate_on_submit:

            if not old_rules:

                new_rules = GeneralSettings(name=form.blog_name.data,
                                            author=form.author_name.data,
                                            post_count=form.post_count.data,
                                            excerpt=form.excerpt.data,
                                            comments=form.comments.data)

                db.session.add(new_rules)

            elif old_rules:
                old_rules.name = form.blog_name.data
                old_rules.author = form.author_name.data
                old_rules.post_count = form.post_count.data
                old_rules.excerpt = form.excerpt.data
                old_rules.comments = form.comments.data

            db.session.commit()

            flash("Your settings have been updated!", "dark")
            return redirect(url_for('settings'))

    if old_rules:
        form.blog_name.data = old_rules.name
        form.author_name.data = old_rules.author
        form.post_count.data = old_rules.post_count
        form.excerpt.data = old_rules.excerpt
        form.comments.data = old_rules.comments

    return render_template('settings.html', title=old_rules.name + " - Settings", settings_title="General Settings",
                           form=form, theme_settings=theme_settings, main_font=main_font, head_font=head_font)

@app.route("/settings/sidebar/", methods=['GET', 'POST'])
@login_required
def sidebar():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('login'))

    tinymce = tinymce_api_key
    general_settings = GeneralSettings.query.first()
    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    form = SidebarSettingsForm()

    old_rules = SidebarSettings.query.first()

    if request.method == 'POST':
        if form.validate_on_submit:

            if not old_rules:
                item = SidebarSettings(main_position=form.main_position.data,
                                       post_position=form.post_position.data,
                                       text=form.text.data,
                                       search=form.search.data,
                                       recent_posts=form.recent_posts.data,
                                       max_recent=form.max_recent.data,
                                       popular_posts=form.popular_posts.data,
                                       max_popular=form.max_popular.data,
                                       category=form.category.data,
                                       max_category=form.max_category.data,
                                       tag=form.tag.data,
                                       max_tag=form.max_tag.data)

                db.session.add(item)

            elif old_rules:
                old_rules.main_position = form.main_position.data
                old_rules.post_position = form.post_position.data
                old_rules.text = form.text.data
                old_rules.search = form.search.data
                old_rules.recent_posts = form.recent_posts.data
                old_rules.max_recent = form.max_recent.data
                old_rules.popular_posts = form.popular_posts.data
                old_rules.max_popular = form.max_popular.data
                old_rules.category = form.category.data
                old_rules.max_category = form.max_category.data
                old_rules.tag = form.tag.data
                old_rules.max_tag = form.max_tag.data

            if form.img.data:
                img_uploader(form.img.data)

            db.session.commit()
            flash('Successfully updated sidebar settings!', 'success')
            return redirect(url_for('sidebar'))

    if old_rules:
        form.main_position.data = old_rules.main_position
        form.post_position.data = old_rules.post_position
        form.text.data = old_rules.text
        form.search.data = old_rules.search
        form.recent_posts.data = old_rules.recent_posts
        form.max_recent.data = old_rules.max_recent
        form.popular_posts.data = old_rules.popular_posts
        form.max_popular.data = old_rules.max_popular
        form.category.data = old_rules.category
        form.max_category.data = old_rules.max_category
        form.tag.data = old_rules.tag
        form.max_tag.data = old_rules.max_tag


    return render_template('sidebar_settings.html', title=general_settings.name + " - Settings", settings_title="Sidebar Settings",
                           form=form, theme_settings=theme_settings, main_font=main_font, head_font=head_font,
                           tinymce=tinymce)


@app.route("/settings/theme/", methods=['GET', 'POST'])
@login_required
def theme():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('login'))

    tinymce = tinymce_api_key
    general_settings = GeneralSettings.query.first()
    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    selectform = ThemeSelectForm()
    form = NewThemeForm()
    themes = Theme.query.all()


    if request.method == 'POST':
        if form.submit1.data and form.validate_on_submit:

            current_theme = Theme.query.filter_by(selected=True).first()

            current_theme.name=form.name.data
            current_theme.selected=True
            current_theme.bg_color=form.bg_color.data
            current_theme.text_color=form.text_color.data
            current_theme.post_container_color=form.post_container_color.data
            current_theme.blog_name_color=form.blog_name_color.data
            current_theme.header_color = form.header_color.data
            current_theme.alt_header_color=form.alt_header_color.data
            current_theme.link_color=form.link_color.data
            current_theme.like_color=form.like_color.data
            current_theme.comment_color=form.comment_color.data
            current_theme.sticky_color=form.sticky_color.data
            current_theme.main_font=form.main_font.data
            current_theme.header_font=form.header_font.data

            db.session.commit()
            return redirect(url_for('theme'))


        if selectform.submit2.data and selectform.validate_on_submit:
            for theme in themes:
                theme.selected = False

            print(selectform.selection.data)

            new_theme = Theme.query.get_or_404(selectform.selection.data)
            new_theme.selected = True

            db.session.commit()
            return redirect(url_for('theme'))

    current_theme = Theme.query.filter_by(selected=True).first()

    if current_theme:
        form.name.data = current_theme.name
        form.bg_color.data = current_theme.bg_color
        form.text_color.data = current_theme.text_color
        form.post_container_color.data = current_theme.post_container_color
        form.blog_name_color.data = current_theme.blog_name_color
        form.header_color.data = current_theme.header_color
        form.alt_header_color.data = current_theme.alt_header_color
        form.link_color.data = current_theme.link_color
        form.like_color.data = current_theme.like_color
        form.comment_color.data = current_theme.comment_color
        form.sticky_color.data = current_theme.sticky_color
        form.main_font.data = current_theme.main_font
        form.header_font.data = current_theme.header_font

    return render_template('theme.html', title=general_settings.name + " - Settings", settings_title="Theme Settings",
                           form=form, selectform=selectform, themes=themes, theme_settings=theme_settings,
                           main_font=main_font, head_font=head_font, tinymce=tinymce)


@app.route("/settings/new_post/", methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('login'))

    tinymce = tinymce_api_key
    general_settings = GeneralSettings.query.first()
    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    form = NewBlogPost()

    if request.method == 'POST':

        if form.validate_on_submit:
            blog_post = Blog(name=form.post_name.data,
                             text=form.content.data,
                             tags=form.tags.data,
                             category=form.category.data
                             )

            db.session.add(blog_post)
            db.session.commit()

            return redirect(url_for('index'))


    return render_template('new_post.html', title=general_settings.name + " - New Blog Post", settings_title="New Blog Post",
                           form=form, theme_settings=theme_settings, main_font=main_font, head_font=head_font,
                           tinymce=tinymce)

@app.route("/settings/manage_users/", methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('login'))

    tinymce = tinymce_api_key
    general_settings = GeneralSettings.query.first()
    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+', ' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+', ' ')

    form = AdminForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            email = form.email.data
            user = User(email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('New administrative account created', 'success')
            return redirect(url_for('manage_users'))

    users = User.query.all()

    return render_template('manage_users.html', title=general_settings.name + " - Manage Users", settings_title="Manage Users",
                           form=form, users=users, theme_settings=theme_settings, main_font=main_font,
                           head_font=head_font, tinymce=tinymce)


@app.route("/settings/about-alambi/")
@login_required
def about_alambi():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('login'))

    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    form = NewBlogPost()

    return render_template('about-alambi.html', title="About Alambi", settings_title="About Alambi",
                           form=form, theme_settings=theme_settings, main_font=main_font, head_font=head_font)


@app.route("/settings/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update(post_id):
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('login'))

    tinymce = tinymce_api_key

    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    if not current_user.is_authenticated:
        redirect(url_for('login'))

    form = NewBlogPost()
    post = Blog.query.get_or_404(post_id)
    if request.method == 'POST':
        if form.validate_on_submit:
            post.name = form.post_name.data
            post.text = form.content.data
            post.category = form.category.data
            post.tags = form.tags.data
            db.session.commit()
            return redirect(url_for('post', post_id=post_id))

    form.post_name.data = post.name
    form.content.data = post.text
    form.category.data = post.category
    form.tags.data = post.tags

    return render_template('new_post.html', title='Update ' + post.name, form=form, settings_title="Update Blog Post", theme_settings=theme_settings,
                           main_font=main_font, head_font=head_font, tinymce=tinymce)


@app.route("/item/<int:item_id>/<table>/<location>/delete", methods=['GET', 'POST'])
@login_required
def delete_item(item_id, table, location):

    if table == 'blog':
        item = Blog.query.get_or_404(item_id)

        tags = item.tags
        for tag in tags:
            if tag.post_tags.count() <= 1:
                db.session.delete(tag)


        msg = "Blog post successfully deleted!"

    if table == 'comment':
        item = Comment.query.get_or_404(item_id)
        msg = "Comment successfully deleted!"

        post = Blog.query.get_or_404(location)
        post.comment_count -= 1

        db.session.delete(item)
        db.session.commit()
        flash(msg, 'success')
        return redirect(url_for('post', post_id=location))

    if table == 'user':
        item = User.query.get_or_404(item_id)
        msg = "User successfully deleted!"


    db.session.delete(item)
    db.session.commit()
    flash(msg, 'success')
    return redirect(url_for(location))


@app.route('/login', methods=['GET', 'POST'])
def login():
    theme_settings = Theme.query.filter_by(selected=True).first()

    form = Login()
    if current_user.is_authenticated:
        return redirect(url_for('settings'))
    if request.method == 'POST':
        if form.validate_on_submit:
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('settings'))
            else:
                flash('Login Unsuccessful. Please check your email and password', 'danger')
                return redirect(url_for('login'))

    return render_template('login.html', form=form, title='Alambi - Admin Login', theme_settings=theme_settings)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    theme_settings = Theme.query.filter_by(selected=True).first()

    form = RequestResetForm()
    if current_user.is_authenticated:
        return redirect(url_for('settings'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))

    return render_template('reset_request.html', title="Alambi - Reset Password", form=form, theme_settings=theme_settings)


def reset_email(user):
    blog = GeneralSettings.query.first()
    token = user.get_reset_token()
    msg = Message('Reset Password - ' + blog.name, sender='noreply@alambi.com', recipients=[user.email])
    token_link = url_for('reset_password', token=token, _external=True)
    msg.body = "To reset your password, click the following link: " + token_link
    mail.send(msg)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    theme_settings = Theme.query.filter_by(selected=True).first()

    form = ResetPassword()
    if current_user.is_authenticated:
        return redirect(url_for('admin'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('Your verification token has expired or is invalid, Try again.', 'danger')
        return redirect(url_for('reset_request'))

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('You have successfully updated your password!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html', title="Alambi - Reset Password", form=form, theme_settings=theme_settings)


@app.errorhandler(404)
def page_not_found(e):
    theme_settings = Theme.query.filter_by(selected=True).first()
    error = 404
    error_text = 'Turn Back!'
    bg_color = '#00878c'
    link_color = '#f3c877'
    login = False

    return render_template('error.html', title='Alambi - 404', theme_settings=theme_settings, error=error,
                           bg_color=bg_color, link_color=link_color, error_text=error_text,
                           login=login), 404

@app.errorhandler(401)
def page_not_found(e):
    flash('You must be logged in to do that', 'warning')
    return redirect(url_for('login'))

@app.errorhandler(403)
def page_not_found(e):
    theme_settings = Theme.query.filter_by(selected=True).first()
    error = 403
    error_text = 'Forbidden!'
    bg_color = '#F2684A'
    link_color = '#FCC499'
    login = True

    return render_template('error.html', title='Alambi - 403', theme_settings=theme_settings, error=error,
                           bg_color=bg_color, link_color=link_color, error_text=error_text,
                           login=login), 403

@app.errorhandler(500)
def page_not_found(e):
    theme_settings = Theme.query.filter_by(selected=True).first()
    error = 500
    error_text = "That's our fault!"
    bg_color = '#3F9490'
    link_color = '#E86E7F'
    login = False

    return render_template('error.html', title='Alambi - 500', theme_settings=theme_settings, error=error,
                           bg_color=bg_color, link_color=link_color, error_text=error_text,
                           login=login), 500

