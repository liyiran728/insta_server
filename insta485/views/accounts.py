"""
Insta485 account view.

URLs include:
/accounts/
"""
from flask import request, redirect, url_for, make_response, abort
import insta485
from insta485.views.util import get_target, validate_password, validate
from insta485.views.create import add_user
from insta485.views.edit import update_user, update_user_password


@insta485.app.route('/accounts/', methods=['POST'])
def show_account():
    """Show /accounts/."""
    if request.form['operation'] == "login":
        return handle_login()
    if request.form['operation'] == "create":
        return handle_create()
    if request.form['operation'] == "delete":
        return handle_delete()
    if request.form['operation'] == "edit_account":
        return handle_edit()
    if request.form['operation'] == "update_password":
        return handle_update_password()


def handle_login():
    """Show /accounts/login/."""
    # if logged in, redirect to index page
    if 'username' in request.cookies:
        return redirect(url_for('show_index'))

    # if not, log in user using information
    if request.form['password'] == "" or request.form['username'] == "":
        abort(400)
    username = request.form['username']
    password = request.form['password']
    validate_password(username, password)
    response = make_response(redirect(get_target()))
    response.set_cookie('username', username)
    return response


def handle_create():
    """Handle create."""
    if request.form['password'] == "" or request.form['username'] == "":
        abort(400)
    if request.form['fullname'] == "" or request.form['email'] == "":
        abort(400)
    file = request.files['file']
    if file.filename == '':
        abort(400)
    validate(request.form['username'], 9)
    return add_user()


def handle_delete():
    """Handle delete."""
    # if logged in, redirect to index page
    if 'username' not in request.cookies:
        abort(403)
    logname = request.cookies.get("username")
    if request.form.get('delete') == 'confirm delete account':
        connection = insta485.model.get_db()

        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (logname, ))
        user_img = cur.fetchall()[0]
        cur = connection.execute(
            "SELECT filename FROM posts WHERE owner = ?",
            (logname,))
        posts = cur.fetchall()
        cur = connection.execute(
            "DELETE FROM users WHERE username = ?",
            (logname,))
        filename = user_img["filename"]
        path = insta485.app.config['UPLOAD_FOLDER']/filename
        path.unlink()
        for post in posts:
            filename = post["filename"]
            path = insta485.app.config['UPLOAD_FOLDER']/filename
            path.unlink()

        response = make_response(redirect(get_target()))
        response.delete_cookie('username')
        return response


def handle_edit():
    """Handle edit."""
    if 'username' in request.cookies:
        logname = request.cookies.get('username')
        if request.form['fullname'] == "" or request.form['email'] == "":
            abort(400)
        if request.form.get('update') == 'submit':
            return update_user(logname)

    abort(403)


def handle_update_password():
    """Handle update password."""
    if 'username' not in request.cookies:
        abort(403)
    logname = request.cookies.get('username')
    return update_user_password(logname)
