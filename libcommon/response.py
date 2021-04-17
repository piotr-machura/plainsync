"""Response module.

Contains the `Response` classes sent by client to a server.
"""
from .message import Message, MessageType


class Response(Message):
    """Base response class.

    Used by the server to request authentication from a server.

    Items:
        userID: unique userID recognized by the server.
        message: a descriptive message from the server.
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
    def __init__(self, action='', **kwargs):
        super().__init__(
            msgType=MessageType.OK,
            message=f'Action: {action} :: Success.',
            **kwargs,
        )


class AuthResponse(Response):
    """Authentication response class. Issued after succesfull authentication.

    Items:
        files: list of files the just-authenticated user has access to.
    """
    def __init__(self, userID=None, filelist=None, user='', **kwargs):
        super().__init__(
            userID=userID,
            msgType=MessageType.AUTH,
            message=f'Authenticated {user}',
            **kwargs,
        )
        if filelist is None:
            self.filelist = list()
        else:
            self.filelist = filelist


class ErrResponse(Response):
    """ Error response class.

    Used by the server to communicate errors.

    Args:
        action: cosmetic string descibing hte action in which the error ocured.
        err: error description with optional stack trace.
    """
    def __init__(self, action='', err='', **kwargs):
        super().__init__(
            msgType=MessageType.ERR,
            message=f'Action: {action} :: Error {err}.',
            **kwargs,
        )
