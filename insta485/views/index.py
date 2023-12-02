"""
Insta485 index (main) view.

URLs include:
/
"""
import sys
import flask
import arrow
import insta485
from insta485.views.util import create_comment
from insta485.views.explore import get_follow_table


@insta485.app.route('/', methods=['GET', 'POST'])
def show_index():
    """Display / route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    # if not logged in, redirect to login page
    if 'username' not in flask.request.cookies:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.request.cookies['username']
    if flask.request.method == 'POST':
        form = flask.request.form
        create_comment(form, connection, form.get('postid'), logname)
        print(flask.request.args.get('target'))
        return flask.redirect(flask.request.args.get('target'))

    posts = connection.execute(
        "SELECT p.postid, p.filename, p.owner, p.created AS timestamp, "
        "u.filename AS owner_img_url "
        "FROM posts AS p, users AS u "
        "WHERE p.postid != ? AND u.username = p.owner "
        "ORDER BY p.postid DESC",
        (logname, )
    ).fetchall()
    # Make timestamp humanize
    for post in posts:
        post['timestamp'] = (arrow.get(post['timestamp']).humanize())
    ##############################
    add_comments(connection, posts)
    add_likes(connection, posts, logname)

    # work on buttons
    # delete unfollowed posts
    follow_table = get_follow_table(connection)
    not_following = follow_table[logname]['not_following']
    posts = [p for p in posts if p['owner'] not in not_following]
    print(flask.request.method, file=sys.stderr)
    # Add database info to context
    # print(posts, file=sys.stderr)
    context = {"posts": posts, "logname": logname}
    # print(posts, file=sys.stderr)
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<filename>', methods=['GET'])
def uploads(filename):
    """Display images."""
    if 'username' in flask.request.cookies:
        return flask.send_from_directory(
            insta485.app.config["UPLOAD_FOLDER"], filename)
    return flask.abort(403)


def add_comments(connection, posts):
    """Add comments."""
    comments = connection.execute(
        "SELECT * "
        "FROM comments ",
    ).fetchall()
    for comment in comments:
        for post in posts:
            if post['postid'] == comment['postid']:
                if 'comments' not in post:
                    post['comments'] = [comment]
                else:
                    post['comments'].append(comment)
                break
    ###########################


def add_likes(connection, posts, logname):
    """Add likes."""
    likes = connection.execute(
        "SELECT * "
        "FROM likes ",
    ).fetchall()

    for like in likes:
        for post in posts:
            if 'likes' not in post:
                post['likes'] = 0
            if 'loginlike' not in post:
                post['loginlike'] = False
            if post['postid'] == like['postid']:
                post['likes'] += 1
                if like['owner'] == logname:
                    post['loginlike'] = True
                break
