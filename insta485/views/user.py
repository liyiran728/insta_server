"""
Insta485 user view.

URLs include:
/users/<user_url_slug>/
"""
import sys
import flask
import insta485
from insta485.views.util import follow_post_request
from insta485.views.explore import get_follow_table


@insta485.app.route('/users/<username>/', methods=['GET', 'POST'])
def show_user(username):
    """Display / route."""
    # Connect to database
    if 'username' not in flask.request.cookies:
        return flask.redirect(flask.url_for('show_login'))
    connection = insta485.model.get_db()

    # Query database
    logname = flask.request.cookies['username']
    if flask.request.method == 'POST':
        follow_post_request(connection, logname)
        print(flask.request.form, file=sys.stderr)
        return flask.redirect(flask.request.args.get('target'))
    user = get_user_info(logname, username, connection)

    context = {"user": user, "logname": logname}
    return flask.render_template("user.html", **context)


def get_user_info(logname, username, connection):
    """Get user info."""
    user = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (username, )
    ).fetchone()

    if user is None:
        flask.abort(404)
    all_users = connection.execute(
        "SELECT * "
        "FROM users",
    ).fetchall()

    # set user["logname"] to logname
    user["logname"] = logname

    # see if logname follows current user
    follow_table = get_follow_table(connection)
    not_following = follow_table[logname]['not_following']
    if username in not_following:
        user["logname_follows_username"] = False
    elif username != logname:
        user["logname_follows_username"] = True

    # set logname_follows_username for all users
    for person in all_users:
        person["logname"] = logname
        if person["username"] in not_following:
            person["logname_follows_username"] = False
        elif person["username"] != logname:
            person["logname_follows_username"] = True

    # get following
    following = follow_table[username]['following']
    user["following"] = len(following)
    user["following_list"] = []
    for person in following:
        for i in all_users:
            if i["username"] == person:
                user["following_list"].append(i)

    # get follower
    user["followers"] = 0
    user["followers_list"] = []
    for person in follow_table:
        if username in follow_table[person]["following"]:
            user["followers"] += 1
            for i in all_users:
                if i["username"] == person:
                    user["followers_list"].append(i)

    # get posts
    user["posts"] = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE owner = ?",
        (username, )
    ).fetchall()
    user["total_posts"] = len(user["posts"])

    return user
