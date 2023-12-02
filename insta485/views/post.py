"""
Insta485 index (main) view.

URLs include:
/
"""
import pathlib
import uuid
import arrow
from flask import request, redirect, render_template, url_for, abort
import insta485
from insta485.views.index import add_comments, add_likes
from insta485.views.util import delete_comment, \
    create_comment, operation_unlike, \
    operation_like


@insta485.app.route('/posts/<postid>/', methods=['GET'])
def show_post(postid):
    """Display / route."""
    # Connect to database
    if 'username' not in request.cookies:
        return redirect(url_for('show_login'))
    connection = insta485.model.get_db()
    # Query database
    logname = request.cookies['username']
    posts = connection.execute(
        "SELECT p.postid, p.filename, p.owner, "
        "p.created AS timestamp, "
        "u.filename AS owner_img_url "
        "FROM posts AS p, users AS u "
        "WHERE postid = ? AND p.owner = u.username",
        (postid, )
    ).fetchone()
    # Make timestamp humanize
    posts['timestamp'] = (arrow.get(posts['timestamp']).humanize())
    add_comments(connection, [posts])
    add_likes(connection, [posts], logname)
    # Add database info to context
    posts['logname'] = logname
    # context = {"posts": posts}
    context = posts
    return render_template("post.html", **context)


@insta485.app.route('/posts/', methods=['POST'])
def update_posts():
    """Update posts."""
    connection = insta485.model.get_db()
    logname = request.cookies.get('username')
    if request.form['operation'] == 'create':
        # Unpack flask object
        fileobj = request.files["file"]
        filename = fileobj.filename
        if filename == "":
            abort(400)
        # Compute base name (filename without directory).
        # We use a UUID to avoid
        # clashes with existing files,
        # and ensure that the name is compatible with the
        # filesystem.
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix
        uuid_basename = f"{stem}{suffix}"
        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        connection.execute(
            "INSERT INTO posts(filename, owner) "
            "VALUES(?, ?)",
            (uuid_basename, logname)
        )

    if request.form['operation'] == 'delete':
        # If a user tries to delete a post that they
        # do not own, then abort(403).
        postid = request.form['postid']
        owner = connection.execute(
            "SELECT owner FROM posts "
            "WHERE postid = ?",
            (postid, )
        ).fetchone().get('owner')
        if logname != owner:
            abort(403)
        # Delete the image file for postid from the filesystem.
        cur = connection.execute(
            "SELECT filename FROM posts WHERE postid = ?",
            (postid, ))
        posts = cur.fetchone()
        cur = connection.execute(
            "DELETE FROM posts WHERE postid = ?",
            (postid,))
        filename = posts["filename"]
        path = insta485.app.config['UPLOAD_FOLDER']/filename
        path.unlink()

        # Delete everything in the database related
        # to this post. Redirect to URL.
    value = request.args.get("target")
    if value is None or value == "":
        return redirect(url_for('show_user',
                                username=logname))
    return redirect(value)

    """
    elif request.form['delete'] == 'delete this post':
        connection.execute(
            "DELETE "
            "FROM comments "
            "WHERE commentid = ?",
            (request.form['commentid'], )
        )
    """


@insta485.app.route('/likes/', methods=['POST'])
def update_likes():
    """Update likes."""
    logname = request.cookies.get('username')
    form = request.form
    connection = insta485.model.get_db()
    postid = form['postid']
    # print(form, file=sys.stderr)
    if form['operation'] == 'like':
        operation_like(form, connection, postid, logname)
    elif form['operation'] == 'unlike':
        operation_unlike(form, connection, postid, logname)
    return redirect(request.args.get('target'))


@insta485.app.route('/comments/', methods=['POST'])
def update_comments():
    """Update comments."""
    logname = request.cookies.get('username')
    form = request.form
    connection = insta485.model.get_db()
    postid = form.get('postid')

    if form['operation'] == 'create':
        create_comment(form, connection, postid, logname)
    elif form['operation'] == 'delete':
        delete_comment(form, connection, logname)
    # If the value of ?target is not set, redirect to /
    target = request.args.get('target')
    # print(type(target), file=sys.stderr)
    if target is None or target == '':
        return redirect(url_for('show_index'))
    return redirect(request.args.get('target'))
