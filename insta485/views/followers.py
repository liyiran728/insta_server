"""
Insta485 followers view.

URLs include:
/users/<user_url_slug>/followers/
"""
import flask
import insta485
from insta485.views.user import get_user_info


@insta485.app.route('/users/<username>/followers/')
def show_followers(username):
    """Display / route."""
    if 'username' not in flask.request.cookies:
        return flask.redirect(flask.url_for('show_login'))
    connection = insta485.model.get_db()
    # Query database
    logname = flask.request.cookies['username']
    # Connect to database
    connection = insta485.model.get_db()

    # Query database

    user = get_user_info(logname, username, connection)

    context = {"user": user, "logname": logname}
    return flask.render_template("followers.html", **context)
