"""
Insta485 login view.

URLs include:
/accounts/login
"""
from flask import request, redirect, url_for, make_response, render_template
import insta485
from insta485.views.util import validate_password


@insta485.app.route('/accounts/login/', methods=['GET'])
def show_login():
    """Show /accounts/login/."""
    # if logged in, redirect to index page
    if 'username' in request.cookies:
        return redirect(url_for('show_index'))
    return render_template('login.html')


@insta485.app.route('/accounts/logout/', methods=['POST'])
def show_logout():
    """Show logout."""
    response = make_response(redirect(url_for('show_login')))
    response.delete_cookie('username')
    return response
