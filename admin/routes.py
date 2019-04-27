from flask import render_template, request, flash, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from alambi import db, bcrypt
from alambi.utils import img_uploader
from alambi.models import (Blog, Comment, User, GeneralSettings, SidebarSettings,
                           Theme)
from alambi.admin.forms import (GeneralSettingsForm, NewThemeForm, NewBlogPost,
                                AdminForm, SidebarSettingsForm, ThemeSelectForm)
import os


admin = Blueprint('admin', __name__)


@admin.route("/settings")
@admin.route("/settings/general/", methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_authenticated:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('users.login'))

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

            flash("Your settings have been updated!", "success")
            return redirect(url_for('admin.settings'))

    if old_rules:
        form.blog_name.data = old_rules.name
        form.author_name.data = old_rules.author
        form.post_count.data = old_rules.post_count
        form.excerpt.data = old_rules.excerpt
        form.comments.data = old_rules.comments

    return render_template('settings.html', title=old_rules.name + " - Settings", settings_title="General Settings",
                           form=form, theme_settings=theme_settings, main_font=main_font, head_font=head_font)

@admin.route("/settings/sidebar/", methods=['GET', 'POST'])
@login_required
def sidebar():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('users.ogin'))

    tinymce = os.getenv('TINYMCE_API')
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
                                       show_logo=form.show_logo.data,
                                       show_blog_name=form.show_blog_name.data,
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
                old_rules.show_logo = form.show_logo.data
                old_rules.show_blog_name = form.show_blog_name.data
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
            return redirect(url_for('admin.sidebar'))

    if old_rules:
        form.main_position.data = old_rules.main_position
        form.post_position.data = old_rules.post_position
        form.show_logo.data = old_rules.show_logo
        form.show_blog_name.data = old_rules.show_blog_name
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


@admin.route("/settings/theme/", methods=['GET', 'POST'])
@login_required
def theme():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('users.login'))

    tinymce = os.getenv('TINYMCE_API')
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

            current_theme.name = form.name.data
            current_theme.selected = True
            current_theme.bg_color = form.bg_color.data
            current_theme.text_color = form.text_color.data
            current_theme.post_container_color = form.post_container_color.data
            current_theme.blog_name_color = form.blog_name_color.data
            current_theme.header_color = form.header_color.data
            current_theme.alt_header_color = form.alt_header_color.data
            current_theme.link_color = form.link_color.data
            current_theme.like_color = form.like_color.data
            current_theme.comment_color = form.comment_color.data
            current_theme.sticky_color = form.sticky_color.data
            current_theme.main_font = form.main_font.data
            current_theme.header_font = form.header_font.data

            db.session.commit()
            flash('You successfully updated your theme!', 'success')
            return redirect(url_for('admin.theme'))


        if selectform.submit2.data and selectform.validate_on_submit:
            for theme in themes:
                theme.selected = False

            print(selectform.selection.data)

            new_theme = Theme.query.get_or_404(selectform.selection.data)
            new_theme.selected = True

            db.session.commit()
            return redirect(url_for('admin.theme'))

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


@admin.route("/settings/new_post/", methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('users.login'))

    tinymce = os.getenv('TINYMCE_API')
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

            return redirect(url_for('main.index'))


    return render_template('new_post.html', title=general_settings.name + " - New Blog Post", settings_title="New Blog Post",
                           form=form, theme_settings=theme_settings, main_font=main_font, head_font=head_font,
                           tinymce=tinymce)

@admin.route("/settings/manage_users/", methods=['GET', 'POST'])
#@login_required
def manage_users():

    tinymce = os.getenv('TINYMCE_API')
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
            return redirect(url_for('admin.manage_users'))

    users = User.query.all()

    return render_template('manage_users.html', title=general_settings.name + " - Manage Users", settings_title="Manage Users",
                           form=form, users=users, theme_settings=theme_settings, main_font=main_font,
                           head_font=head_font, tinymce=tinymce)


@admin.route("/settings/about-alambi/")
@login_required
def about_alambi():
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('users.login'))

    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    form = NewBlogPost()

    return render_template('about_alambi.html', title="About Alambi", settings_title="About Alambi",
                           form=form, theme_settings=theme_settings, main_font=main_font, head_font=head_font)


@admin.route("/settings/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update(post_id):
    if current_user.is_authenticated != True:
        flash('You must be logged in to do that!', 'warning')
        return redirect(url_for('users.login'))

    tinymce = os.getenv('TINYMCE_API')

    theme_settings = Theme.query.filter_by(selected=True).first()
    main_font = theme_settings.main_font
    main_font = main_font.replace('+',' ')
    head_font = theme_settings.header_font
    head_font = head_font.replace('+',' ')

    if not current_user.is_authenticated:
        redirect(url_for('users.login'))

    form = NewBlogPost()
    post = Blog.query.get_or_404(post_id)
    if request.method == 'POST':
        if form.validate_on_submit:
            post.name = form.post_name.data
            post.text = form.content.data
            post.category = form.category.data
            post.tags = form.tags.data
            db.session.commit()
            return redirect(url_for('main.post', post_id=post_id))

    form.post_name.data = post.name
    form.content.data = post.text
    form.category.data = post.category
    form.tags.data = post.tags

    return render_template('new_post.html', title='Update ' + post.name, form=form, settings_title="Update Blog Post", theme_settings=theme_settings,
                           main_font=main_font, head_font=head_font, tinymce=tinymce)


@admin.route("/item/<int:item_id>/<table>/<location>/delete", methods=['GET', 'POST'])
@login_required
def delete_item(item_id, table, location):

    item = None
    msg = None

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
        return redirect(url_for('main.post', post_id=location))

    if table == 'user':
        item = User.query.get_or_404(item_id)
        msg = "User successfully deleted!"


    db.session.delete(item)
    db.session.commit()
    flash(msg, 'success')
    return redirect(url_for(location))