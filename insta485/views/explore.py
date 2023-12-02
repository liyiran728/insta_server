"""
Insta485 /explore/ view.

URLs include:
/explore/
"""
import flask
import insta485


@insta485.app.route('/explore/', methods=['GET'])
def show_explore():
    """Display /explore/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.request.cookies:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.request.cookies.get('username')
    follow_table = get_follow_table(connection)
    following = follow_table[logname]['following']
    # Put user info into following list
    users_info = connection.execute("SELECT filename AS user_img_url, "
                                    "username "
                                    "FROM users "
                                    ).fetchall()
    following.append(logname)
    users_info = [user for user in users_info
                  if user['username'] not in following]

    ##############################

    # print(users_info, file=sys.stderr)
    # Add database info to context
    context = {"not_following": users_info, "logname": logname}
    return flask.render_template("explore.html", **context)


def get_follow_table(connection):
    """Get the follow table."""
    following = connection.execute(
        "SELECT * FROM following ",
    ).fetchall()
    users = []
    for ele in connection.execute("SELECT username FROM users ",).fetchall():
        users.append(ele['username'])
    follow_table = {}
    for i in users:
        i_follow = {'following': [], 'not_following': users.copy()}
        i_follow['not_following'].remove(i)
        follow_table[i] = i_follow
    for j in following:
        follow_table[j['username1']]['not_following'].remove(j['username2'])
        follow_table[j['username1']]['following'].append(j['username2'])

    return follow_table
