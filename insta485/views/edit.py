"""
Insta485 login view.

URLs include:
/accounts/edit
"""
import pathlib
import uuid
from flask import request, redirect, url_for, render_template, abort, \
    make_response
import insta485
from insta485.views.util import get_target, validate_password, hash_password


@insta485.app.route('/accounts/edit/', methods=["GET"])
def show_edit():
    """Display edit."""
    if 'username' in request.cookies:
        logname = request.cookies.get('username')

        connection = insta485.model.get_db()
        cur = connection.execute("SELECT * FROM users WHERE username = ?",
                                 (logname,))
        user = cur.fetchone()
        # user_img_url = "/uploads/" + user['filename']
        user_img_url = user['filename']
        context = {
            "logname": logname,
            "user_img_url": user_img_url,
            "fullname": user['fullname'],
            "email": user["email"]
        }
        return render_template('edit.html', **context)

    return redirect(url_for('show_login'))


def update_user(logname):
    """Update user info."""
    fullname = request.form['fullname']
    email = request.form['email']

    connection = insta485.model.get_db()

    if request.files['file']:
        fileobj = request.files['file']
        filename = fileobj.filename

        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        cur = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (logname,)
        )
        user = cur.fetchone()
        cur = connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ?, filename = ? "
            "WHERE username = ?", (fullname, email, uuid_basename, logname,)
        )
        old_filename = user["filename"]
        path = insta485.app.config["UPLOAD_FOLDER"]/old_filename
        path.unlink()
    else:
        cur = connection.execute(
            "UPDATE users SET fullname = ?, email = ? "
            "WHERE username = ?",
            (fullname, email, logname,)
        )
    return make_response(redirect(get_target()))


@insta485.app.route('/accounts/password/', methods=['GET', 'POST'])
def show_password():
    """Display password page."""
    if 'username' in request.cookies:
        logname = request.cookies.get('username')

    if request.method == 'POST':
        if request.form.get('update_password') == 'submit':
            return update_user_password(logname)

    context = {"logname": logname, }
    return render_template("password.html", **context)


def update_user_password(logname):
    """Update password."""
    password = request.form["password"]
    new_password1 = request.form["new_password1"]
    new_password2 = request.form["new_password2"]
    if password == "" or new_password1 == "" or new_password2 == "":
        abort(400)

    validate_password(logname, password)
    if not new_password1 == new_password2:
        abort(401)

    connection = insta485.model.get_db()
    password_db_string = hash_password(new_password1)
    connection.execute("UPDATE users SET password = ?",
                       (password_db_string,))

    return make_response(redirect(get_target()))
