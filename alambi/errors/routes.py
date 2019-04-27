from flask import Blueprint, render_template, redirect, flash, url_for
from alambi.models import Theme


errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
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


@errors.app_errorhandler(401)
def page_not_found(e):
    flash('You must be logged in to do that', 'warning')
    return redirect(url_for('login'))


@errors.app_errorhandler(403)
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


@errors.app_errorhandler(500)
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
