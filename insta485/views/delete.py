"""
Insta485 delete view.

URLs include:
/accounts/delete/
"""
from flask import request, render_template, abort
import insta485
import sys


@insta485.app.route('/accounts/delete/', methods=['GET'])
def show_delete():
    """Show delete."""
    print(request.cookies, file=sys.stderr)
    if 'username' in request.cookies:
        logname = request.cookies.get('username')

        context = {'logname': logname}
        return render_template("delete.html", **context)

    return abort(404)
