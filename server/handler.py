"""TCP handler module.

Contains the handler and associated functions.
"""
import time
import hashlib
from socketserver import BaseRequestHandler
from logging import info, warning

from common.request import *
from common.response import AuthResponse, ErrResponse
from common.message import MessageType
from common import transfer

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
        # Try and authenticate
        try:
            data = transfer.recieve(self.request)
        except ConnectionAbortedError:
            return
        authRequest = AuthRequest.fromJSON(data)
        if authRequest.type == MessageType.AUTH:
            # Atuhenticate
            user = authRequest.user
            passwd = authRequest.passwd
            if dbmanager.authenticate(user, passwd):
                        # Save the username and the session ID hash
                toHash = str(time.time()) + user + self.client_address[0]
                self.sessionID = hashlib.sha1(
                    toHash.encode('utf-8')).hexdigest()
                self.username = user
                response = AuthResponse(
                    sessionID=self.sessionID,
                    user=user,
                )
            else:
                response = ErrResponse(err='Invalid username or password')
            transfer.send(self.request, response)
        else:
            transfer.send(
                self.request,
                ErrResponse(err='Unauthenticated'),
            )

    def handle(self):
        if self.sessionID is None:
            warning('Unable to authenticate %s', self.client_address[0])
            return

        info('New session %s of user %s', self.sessionID, self.username)
        # Handle incoming requests

        while True:
            try:
                data = transfer.recieve(self.request)
            except ConnectionAbortedError:
                # The connection has been closed
                break
            request = Request.fromJSON(data)
            if request.type == MessageType.LIST_FILES:
                request = FileListRequest.fromJSON(data)
                response = dbmanager.listFiles(self.username)
            elif request.type == MessageType.PULL:
                request = PullRequest.fromJSON(data)
                response = dbmanager.pullFile(self.username, request.file)
            elif request.type == MessageType.PUSH:
                # Same here but I'm lazy
                request = PushRequest.fromJSON(data)
                request = dbmanager.pushFile(
                    self.username,
                    request.file,
                    request.content,
                )
            else:
                response = ErrResponse(err=f'Unknown action: {request.type}')
            info(
                'Session %s of user %s: Request:%s Response:%s',
                self.sessionID,
                self.username,
                request,
                response,
            )
            transfer.send(self.request, response)
        info('Closed session %s of user %s', self.sessionID, self.username)
