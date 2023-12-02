"""
Insta485 following view.

URLs include:
/users/<user_url_slug>/following/
"""
from flask import request, redirect, url_for, render_template
import insta485
from insta485.views.user import get_user_info
from insta485.views.util import follow_post_request


@insta485.app.route('/users/<username>/following/', methods=['GET'])
def show_following(username):
    """Display / route."""
    # if not logged in, redirect to login page
    if 'username' not in request.cookies:
        return redirect(url_for('show_login'))
    # Connect to database
    connection = insta485.model.get_db()
    logname = request.cookies.get("username")
    # Query database
    user = get_user_info(logname, username, connection)

    context = {"user": user, "logname": logname}
    return render_template("following.html", **context)


@insta485.app.route('/following/', methods=['POST'])
def post_following():
    """Post following."""
    connection = insta485.model.get_db()
    logname = request.cookies.get("username")
    # validate(username)
    target = request.args.get('target')
    follow_post_request(connection, logname, request.form['username'])
    target = request.args.get('target')
    if target is None or target == '':
        return redirect(url_for('show_index'))
    return redirect(target)
