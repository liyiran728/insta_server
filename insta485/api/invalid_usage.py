"""Handle Invalid Usage."""

from flask import jsonify
import insta485


class InvalidUsage(Exception):
    """Catch invalid usage exception."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Initialize."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        # print("init",file=sys.stderr)

    def to_dict(self):
        """Turn to dict."""
        # print("todict",file=sys.stderr)
        i = dict(self.payload or ())
        i['message'] = self.message
        i['status_code'] = self.status_code
        return i


@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handle reroute for API."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    # print(response,file=sys.stderr)
    return response
