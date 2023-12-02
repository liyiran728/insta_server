#!flask/bin/python
"""REST API Implementation."""

from flask import Flask, jsonify, abort, request
import insta485
from sys import stderr
from base64 import b64decode
from insta485.views.util import validate_password_p3ver
from insta485.views.explore import get_follow_table
from insta485.views.index import add_likes
from insta485.api.invalid_usage import InvalidUsage


@insta485.app.route('/api/v1/', methods=['GET'])
def get_api_v1():
    """Show /api/v1/."""
    task = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return jsonify(task)


@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_api_v1_posts():
    """Show /api/v1/posts/."""
    logname = check_http_and_cookies().get('logname')
    # Process the return data
    connection = insta485.model.get_db()
    # Request results no newer than postid with ?postid_lte=N
    postid_lte = request.args.get("postid_lte", type=int)
    # Request a specific page of results with ?page=N.
    page = request.args.get("page", default=0, type=int)
    # Return the 10 newest posts
    num_result = request.args.get("size", default=10, type=int)
    if page == -1 or num_result == -1:
        raise InvalidUsage('Bad Request', status_code=400)  # Bad Request
    latest_id = connection.execute(
        "SELECT MAX(postid) FROM posts"
        ).fetchone()['MAX(postid)']
    if postid_lte is None:
        postid_lte = latest_id
    # print(type(postid_lte),file=stderr)
    # delete unfollowed posts
    posts = connection.execute(
        "SELECT DISTINCT p.postid, p.owner "
        "FROM posts AS p "
        "INNER JOIN following AS f "
        "ON p.owner = ? OR "
        "(f.username2 = p.owner AND f.username1 = ?) "
        "WHERE p.postid <= ? "
        "ORDER BY p.postid DESC LIMIT ? OFFSET ?",
        (logname, logname, postid_lte, num_result, page*num_result)
    ).fetchall()
    # print(posts, file=stderr)
    result = []
    for single_post in posts:
        result.append({
            "postid": single_post['postid'],
            "url": f"/api/v1/posts/{single_post['postid']}/"})

    current_url = request.url
    current_url = current_url[current_url.find("api")-1:]
    # Check if there are more pages
    # if_more_posts = len(MORE_POSTS) > 0
    if_more_posts = len(posts) == num_result
    if if_more_posts:
        next_url = current_url[:current_url.find("?")] \
            if current_url.find("?") != -1 else current_url
        # print(next_url, file=stderr)
        next_url += f"?size={num_result}&page={page+1}&postid_lte={postid_lte}"
    else:
        next_url = ""
    task = {
        "next": next_url,
        "results": result,
        "url": current_url
    }
    return jsonify(task)


@insta485.app.route('/api/v1/posts/<int:postid>/', methods=['GET'])
def get_api_v1_detailed_posts(postid):
    """Show single post."""
    logname = check_http_and_cookies().get('logname')
    connection = insta485.model.get_db()
    posts = connection.execute(
        "SELECT p.postid, p.filename AS imgUrl, p.owner, p.created, "
        "u.filename AS ownerImgUrl "
        "FROM posts AS p, users AS u "
        "WHERE u.username = p.owner AND p.postid = ? "
        "ORDER BY p.postid DESC",
        (postid,)
    ).fetchone()
    # print("\n\n", file=stderr)
    if posts is None:
        raise InvalidUsage('Not Found', status_code=404)
    add_comments_p3ver(connection, posts, logname)
    add_likes_p3ver(connection, posts, logname)
    task = {
        "imgUrl": f"/uploads/{posts['imgUrl']}",
        "ownerImgUrl": f"/uploads/{posts['ownerImgUrl']}",
        "ownerShowUrl": f"/users/{posts['owner']}/",
        "postShowUrl": f"/posts/{posts['postid']}/",
        "url": f"/api/v1/posts/{posts['postid']}/"
    }
    posts.update(task)
    # print(posts, file=stderr)
    return jsonify(posts)


def check_http_and_cookies():
    """Check both HTTP Basic Authentication and session cookies."""
    # Check HTTP
    logname = ""
    authorized = False
    if request.headers.get('Authorization') is not None:
        auth = request.headers.get('Authorization')[6:]
        auth = b64decode(auth)
        auth = auth.decode('ascii')
        # print(auth, file=stderr)
        i_colon = auth.find(':')
        if i_colon == -1:
            authorized = False
        http_username = auth[:i_colon]
        http_password = auth[i_colon+1:]
        validate_password_p3ver(http_username, http_password)
        authorized = True
        logname = http_username
    # validate_password will abort 403 if password is wrong
    # Check cookies
    if 'username' in request.cookies:
        logname = request.cookies.get('username')
    if 'username' not in request.cookies and authorized is False:
        raise InvalidUsage('Forbidden', status_code=403)
    return {"logname": logname}


def add_comments_p3ver(connection, post, logname):
    """Add List 'comment' into the dictionary 'post'. P3 Version."""
    comments = connection.execute(
        "SELECT commentid, owner, text "
        "FROM comments WHERE postid = ?",
        (post['postid'],)
    ).fetchall()
    # print(comments, file=stderr)
    post['comments'] = []
    for comment in comments:
        comment['lognameOwnsThis'] = logname == comment['owner']
        comment['ownerShowUrl'] = f"/users/%s/" % comment['owner']
        comment['url'] = f"/api/v1/comments/%d/" % comment['commentid']
        post['comments'].append(comment)


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_new_comment():
    """Post a new comment."""
    postid = request.args.get('postid', type=int)
    logname = check_http_and_cookies().get('logname')
    connection = insta485.model.get_db()
    # Insert new comment into database
    connection.execute(
        "INSERT INTO comments (owner, postid, text) "
        "VALUES (:logname, :postid, :text)",
        {'logname': logname,
            'postid': postid,
            'text': request.json.get('text')}
    )
    comment = connection.execute(
        "SELECT commentid, owner, text "
        "FROM comments "
        "WHERE commentid = last_insert_rowid()",
        ()
    ).fetchone()
    if_owns_this = comment['owner'] == logname
    task = {
        "commentid": comment['commentid'],
        "lognameOwnsThis": if_owns_this,
        "owner": comment['owner'],
        "ownerShowUrl": f"/users/{comment['owner']}/",
        "text": comment['text'],
        "url": f"/api/v1/comments/{comment['commentid']}/"
    }
    return jsonify(task), 201


def add_likes_p3ver(connection, post, logname):
    """Add item 'likes' into the dictionary 'post'. P3 Version."""
    num_likes = connection.execute(
        "SELECT COUNT(likeid) "
        "FROM likes WHERE postid = ?",
        (post['postid'],)
    ).fetchone()
    lognamelike = connection.execute(
        "SELECT likeid "
        "FROM likes WHERE postid = ? "
        "AND owner = ? ",
        (post['postid'], logname, )
    ).fetchone()
    likes = {}
    likes['numLikes'] = num_likes["COUNT(likeid)"]
    if lognamelike is None:
        likes['lognameLikesThis'] = False
        likes['url'] = None
    else:
        likes['lognameLikesThis'] = True
        likes['url'] = f"/api/v1/likes/%d/" % lognamelike['likeid']
    post['likes'] = likes


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def post_new_like():
    """Create a new like."""
    postid = request.args.get('postid', type=int)
    logname = check_http_and_cookies().get('logname')
    connection = insta485.model.get_db()
    like = connection.execute(
        "SELECT * "
        "FROM likes "
        "WHERE postid = ? AND owner = ? ",
        (postid, logname, )
    ).fetchone()
    if like is not None:
        task = {
            "likeid": like['likeid'],
            "url": f"/api/v1/likes/%d/" % like['likeid']
        }
        return jsonify(task), 200
    else:
        connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES (:logname, :postid)",
            {'logname': logname, 'postid': postid}
        )
        like = connection.execute(
            "SELECT * "
            "FROM likes "
            "WHERE likeid = last_insert_rowid()",
            ()
        ).fetchone()
        task = {
            "likeid": like['likeid'],
            "url": f"/api/v1/likes/%d/" % like['likeid']
        }
        return jsonify(task), 201


@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Delete a like."""
    logname = check_http_and_cookies().get('logname')
    connection = insta485.model.get_db()
    like = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE likeid = ? ",
        (likeid,)
    ).fetchone()
    if like is None:
        raise InvalidUsage('Not Found', status_code=404)
    elif like['owner'] != logname:
        raise InvalidUsage('Forbidden', status_code=403)
    else:
        connection.execute(
            "DELETE FROM likes "
            "WHERE likeid = ? ",
            (likeid,)
        )
        return jsonify({}), 204


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete a comment."""
    logname = check_http_and_cookies().get('logname')
    connection = insta485.model.get_db()
    comment = connection.execute(
        "SELECT owner "
        "FROM comments "
        "WHERE commentid = ? ",
        (commentid,)
    ).fetchone()
    if comment is None:
        raise InvalidUsage('Not Found', status_code=404)
    elif comment['owner'] == logname:
        connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ? ",
            (commentid,)
        )
        return jsonify({}), 204
    else:
        raise InvalidUsage('Forbidden', status_code=403)
