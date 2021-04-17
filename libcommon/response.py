"""Response module.


Contains the `Response` classes sent by client to a server.
"""
from .message import Message, MessageType


class Response(Message):
    """Base response class.

    Extended by other classes to include additional data.

    Args:
        description: string describing the response contents.
    """
    def __init__(self, description='', **kwargs):
        super().__init__(**kwargs)
        self.description=description

class OkResponse(Response):
    """OK response class.

    Used by the server to communicate a succesfull outcome of an action which
    does not require any data to be sent from the server.

    Args:
        action: string describing the succesfull action.
    """
    def __init__(self, action=''):
        super().__init__(
            msgType=MessageType.OK,
            description=f'Action: {action} :: Success.',
        )

class PullResponse(Response):
    """Pull response class.

    Used by the server to send file contents to the client after a pull
    request.

    Args:
        content: contents of the specified file.
    """
    def __init__(self, file='', content=''):
        super().__init__(
            msgType=MessageType.PULL,
            description=f'Sending file contents :: {file}',
        )
        self.content = content


class AuthResponse(Response):
    """Authentication response class.

    Issued after succesfull authentication.

    Items:
        userID: a generated ID of the user authenticating him in this session.
        user: username of the just-authenticated user.
    """
    def __init__(self, userID=None, user=''):
        super().__init__(
            msgType=MessageType.AUTH,
            description=f'Authenticated {user}',
        )
        self.userID=userID

class FileListResponse(Response):
    """Response with file names owned by the user.

    Items:
        filelist: a list of files accessible to the user as a dictionary of
                  filename : owned/borrowed pairs.
        user: user for which the lsit was requested.
    """
    def __init__(self, filelist=None, user=''):
        super().__init__(
            msgType=MessageType.LIST_FILES,
            description=f'Sent file list for user {user}',
        )
        self.filelist = filelist
        if self.filelist is None:
            self.filelist = list()

class ErrResponse(Response):
    """ Error response class.

    Used by the server to communicate errors.

    Args:
        action: string descibing the action in which the error ocured.
        err: error description with optional stack trace.
    """
    def __init__(self, action='', err=''):
        super().__init__(
            msgType=MessageType.ERR,
            description=f'Action: {action} :: Error {err}.',
        )
