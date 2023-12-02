"""
Insta485 /explore/ view.

URLs include:
/accounts/create/
"""
import pathlib
import uuid
from flask import request, redirect, url_for, \
                make_response, render_template
import insta485
from insta485.views.util import get_target, hash_password


@insta485.app.route('/accounts/create/', methods=['GET'])
def show_create():
    """Display /accounts/create/."""
    if 'username' in request.cookies:
        return redirect(url_for('show_edit'))

    return render_template('create.html')


def add_user():
    """Add user."""
    username = request.form['username']
    email = request.form['email']
    fullname = request.form['fullname']
    password = request.form['password']

    # Unpack flask object
    fileobj = request.files["file"]
    filename = fileobj.filename
    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that the name
    # is compatible with the
    # filesystem.
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"
    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)

    password_db_string = hash_password(password)

    # Connect to database
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO users(username, fullname, email, filename, password) "
        "VALUES(?,?,?,?,?)",
        (username, fullname, email, uuid_basename, password_db_string,))

    response = make_response(redirect(get_target()))
    response.set_cookie('username', username)
    return response
