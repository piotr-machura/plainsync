"""Response module.

Contains the `Response` classes sent by client to a server.
"""
from .message import Message, MessageType


class Response(Message):
    """Base response class.

    Used by the server to request authentication from a server.

    Items:
        userID: unique userID recognized by the server.
    """
    def __init__(self, userID=None, message='', **kwargs):
        super().__init__(**kwargs)
        self.userID = userID
        self.message = message


class OkResponse(Response):
    """OK response class.

    Used by the server to communicate succesfull action.

    Args:
        action: cosmetic string describing the succesfull action.
    """
    def __init__(self, userID=None, action='', **kwargs):
        super().__init__(
            userID=userID,
            msgType=MessageType.OK,
            message=f'Action: {action}, userID: {userID} :: Success.',
            **kwargs,
        )


class ErrResponse(Response):
    """ Error response class.

    Used by the server to communicate errors.

    Args:
        action: cosmetic string descibing hte action in which the error ocured.
        err: error description with optional stack trace.
    """
    def __init__(self, userID=None, action='', err='', **kwargs):
        super().__init__(
            userID=userID,
            msgType=MessageType.ERR,
            message=f'Action: {action}, userID: {userID} :: Error {err}.',
            **kwargs,
        )
