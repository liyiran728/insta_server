"""
Insta485 utility functions.

URLs include:
None
"""
import uuid
import hashlib
import sys
from flask import request, abort
import insta485
from insta485.api.invalid_usage import InvalidUsage


def follow(connection, logname, username):
    """Follow Action."""
    # Connect to database
    if_followed = connection.execute(
        "SELECT username1 FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, username)
    ).fetchall()
    if len(if_followed) > 0:
        abort(409)
    connection.execute("INSERT INTO following(username1, username2) "
                       "VALUES(?,?)",
                       (logname, username, ))


def unfollow(connection, logname, username):
    """Unfollow Action."""
    # Connect to database
    if_followed = connection.execute(
        "SELECT username1 FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, username)
    ).fetchall()
    if len(if_followed) == 0:
        abort(409)
    connection.execute("DELETE FROM following WHERE username1 = ? "
                       "AND username2 = ?",
                       (logname, username, ))


def follow_post_request(connection, logname, username):
    """Process requests of follow/unfollow."""
    if request.form.get("unfollow") == "unfollow" or \
            request.form.get("operation") == "unfollow":
        unfollow(connection, logname, username)
    elif request.form.get("follow") == "follow" or \
            request.form.get("operation") == "follow":
        follow(connection, logname, username)


def validate(username, abort_type=4):
    """Validate username."""
    connection = insta485.model.get_db()

    cur = connection.execute("SELECT * FROM users WHERE username = ?",
                             (username, ))
    user_exists = len(cur.fetchall()) == 1
    if abort_type == 9:
        if user_exists:
            abort(409)
    else:
        if not user_exists:
            abort(404)


def validate_password(username, password):
    """Validate username and password."""
    # Validate user
    (salt, password_db_string) = get_salt(username)
    # Validate password
    hash_p = hash_password(password, salt)
    if hash_p != password_db_string:
        abort(403)


def validate_password_p3ver(username, password):
    """Validate username and password. P3 ver."""
    # Validate user
    (salt, password_db_string) = get_salt(username)
    # Validate password
    hash_p = hash_password(password, salt)
    if hash_p != password_db_string:
        # abort(403) This is p2 version
        raise InvalidUsage('Forbidden', status_code=403)


def get_salt(username):
    """Return salt associated with username."""
    connection = insta485.model.get_db()
    # Get password db string
    password_db = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username, )).fetchall()
    # See if user exists
    user_exists = len(password_db) > 0
    if not user_exists:
        abort(403)
    password_str = password_db[0]["password"]
    # Get salt
    # print(password_str, file=sys.stderr)
    salt = password_str.split('$')[1]
    return (salt, password_str)


def hash_password(password, salt=uuid.uuid4().hex):
    """Hash password and return string."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def operation_unlike(form, connection, postid, logname):
    """Do unlike operation."""
    # CHECK OWNER
    #################
    if_liked = connection.execute(
        "SELECT likeid FROM likes "
        "WHERE owner = ? AND postid = ?",
        (logname, postid)
    ).fetchall()
    if len(if_liked) == 0:
        abort(409)
    connection.execute(
        "DELETE "
        "FROM likes "
        "WHERE postid = ? AND owner = ?",
        (postid, logname)
    )


def operation_like(form, connection, postid, logname):
    """Do like operation."""
    if_liked = connection.execute(
        "SELECT likeid FROM likes "
        "WHERE owner = ? AND postid = ?",
        (logname, postid)
    ).fetchall()
    if len(if_liked) > 0:
        abort(409)
    connection.execute(
        "INSERT INTO likes (owner, postid) "
        "VALUES (?, ?)",
        (logname, postid)
    )


def create_comment(form, connection, postid, logname):
    """Create comment."""
    # If a user tries to create an empty comment, then abort(400)
    if form['text'] == '':
        abort(400)
    # execute
    connection.execute(
        "INSERT INTO comments (owner, postid, text) "
        "VALUES (:logname, :postid, :text)",
        {'logname': logname,
            'postid': postid,
            'text': form['text']}
    )


def delete_comment(form, connection, logname):
    """Delete comment."""
    # If a user tries to delete a comment that they do not own,
    # then abort(403).
    commentid = form['commentid']
    owner = connection.execute(
        "SELECT owner FROM comments "
        "WHERE commentid = ?",
        (commentid,)
    ).fetchone().get('owner')
    if logname != owner:
        abort(403)
    # execute
    connection.execute(
        "DELETE "
        "FROM comments "
        "WHERE commentid = ?",
        (commentid, )
    )


def get_target():
    """Get target."""
    value = request.args.get("target")
    if value is None:
        return "/"
    return value
