"""TCP handler module.

Contains the handler and associated functions.
"""
import time
import hashlib
from socketserver import BaseRequestHandler
from logging import info, warning, error
from json import JSONDecodeError

from common.request import Request, AuthRequest, FileListRequest, PullRequest, PushRequest
from common.response import ErrResponse, OkResponse, FileListResponse, PullResponse, AuthResponse
from common.message import MessageType
from common import transfer

from server.dbmanager import DatabaseException
from server import dbmanager


class TCPHandler(BaseRequestHandler):
    """
    The TCP request handler class.

    This is instantiated once per connection to the server and handles the
    communication with the client.
    """
    def __init__(self, *args, **kwargs):
        self.sessionID = None
        self.username = None
        super().__init__(*args, **kwargs)

    def setup(self):
        # Try to authenticate
        try:
            data = transfer.recieve(self.request)
            req = AuthRequest.fromJSON(data)
            if req.type != MessageType.AUTH:
                raise DatabaseException('Authenticate first')
            # Authenticate
            user = req.user
            passwd = req.passwd
            dbmanager.authenticate(user, passwd)
            # Save the username and the session ID hash
            sessionID = str(time.time()) + user + self.client_address[0]
            sessionID = hashlib.sha1(sessionID.encode('utf-8'))
            self.sessionID = sessionID.hexdigest()[:12]
            self.username = user
            resp = AuthResponse(
                sessionID=self.sessionID,
                user=user,
            )
            info('New session %s of user %s', self.sessionID, self.username)
        except (JSONDecodeError, TypeError, AttributeError) as ex:
            resp = ErrResponse(err=f'Could not parse request: {ex}')
            warning(
                'Unable to authenticate %s: %s',
                self.client_address[0],
                resp.description,
            )
        except DatabaseException as ex:
            resp = ErrResponse(err=ex)
            warning(
                'Unable to authenticate %s: %s',
                self.client_address[0],
                resp.description,
            )
        except ConnectionAbortedError:
            return
        transfer.send(self.request, resp)

    def handle(self):
        if self.sessionID is None:
            return
        while True:
            # Handle incoming requests
            try:
                data = transfer.recieve(self.request)
                request = Request.fromJSON(data)
                if request.type == MessageType.LIST_FILES:
                    request = FileListRequest.fromJSON(data)
                    response = FileListResponse(
                        files=dbmanager.listFiles(self.username),
                        user=self.username,
                    )
                elif request.type == MessageType.PULL:
                    request = PullRequest.fromJSON(data)
                    response = PullResponse(
                        file=request.file,
                        content=dbmanager.pullFile(
                            self.username,
                            request.file,
                        ),
                    )
                elif request.type == MessageType.PUSH:
                    # Same here but I'm lazy
                    request = PushRequest.fromJSON(data)
                    dbmanager.pushFile(
                        self.username,
                        request.file,
                        request.content,
                    )
                    response = OkResponse(action=f'Push file {request.file}')
                else:
                    raise DatabaseException(f'Unknown action: {request.type}')
            except DatabaseException as ex:
                response = ErrResponse(err=f'{ex}')
                error(
                    'Session %s of user %s: Request:%s Response:%s',
                    self.sessionID,
                    self.username,
                    request,
                    response,
                )
            except (JSONDecodeError, TypeError, AttributeError) as ex:
                response = ErrResponse(err=f'Malformed request: {ex}')
                error(
                    'Session %s of user %s: %s',
                    self.sessionID,
                    self.username,
                    response.description,
                )
                break
            except ConnectionAbortedError:
                break
            else:
                info(
                    'Session %s of user %s: Request:%s Response:%s',
                    self.sessionID,
                    self.username,
                    request,
                    response,
                )
            print(response)
            transfer.send(self.request, response)
        info('Closed session %s of user %s', self.sessionID, self.username)
