"""TCP handler module.

Contains the handler and associated functions.
"""
import time
import hashlib
import logging as log
from socketserver import BaseRequestHandler
from json import JSONDecodeError

from common import request
from common import response
from common import transfer
from common.message import MessageType

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
        self.dataBase = dbmanager.DatabaseManager()
        super().__init__(*args, **kwargs)

    def setup(self):
        # Try to authenticate
        try:
            data = transfer.recieve(self.request)
            req = request.AuthRequest.fromJSON(data)
            if req.type != MessageType.AUTH:
                raise DatabaseException('Authenticate first')
            # Authenticate
            user = req.user
            passwd = req.passwd
            self.dataBase.authenticate(user, passwd)
            # Save the username and the session ID hash
            sessionID = str(time.time()) + user + self.client_address[0]
            sessionID = hashlib.sha1(sessionID.encode('utf-8'))
            self.sessionID = sessionID.hexdigest()[:12]
            self.username = user
            resp = response.AuthResponse(
                sessionID=self.sessionID,
                user=user,
            )
            log.info(
                'New session %s of user %s', self.sessionID, self.username)
        except (JSONDecodeError, TypeError, AttributeError) as ex:
            resp = response.ErrResponse(err=f'Could not parse request: {ex}')
            log.warning(
                'Unable to authenticate %s: %s',
                self.client_address[0],
                resp.description,
            )
        except DatabaseException as ex:
            resp = response.ErrResponse(err=ex)
            log.warning(
                'Unable to authenticate %s: %s',
                self.client_address[0],
                resp.description,
            )
        except (ConnectionAbortedError, MemoryError, ConnectionResetError):
            return
        transfer.send(self.request, resp)

    def handle(self):
        if self.sessionID is None:
            return
        while True:
            # Handle incoming requests
            try:
                data = transfer.recieve(self.request)
                req = request.Request.fromJSON(data)
                if req.type == MessageType.LIST_FILES:
                    req = request.FileListRequest.fromJSON(data)
                    resp = response.FileListResponse(
                        files=self.dataBase.listFiles(self.username),
                        user=self.username,
                    )
                elif req.type == MessageType.PULL:
                    req = request.PullRequest.fromJSON(data)
                    resp = response.PullResponse(
                        fileID=req.fileID,
                        content=self.dataBase.pullFile(
                            self.username,
                            req.fileID,
                        ),
                    )
                elif req.type == MessageType.PUSH:
                    req = request.PushRequest.fromJSON(data)
                    self.dataBase.pushFile(
                        self.username,
                        req.fileID,
                        req.content,
                    )
                    resp = response.OkResponse(
                        action=f'Push file {req.fileID}')
                elif req.type == MessageType.NEW_FILE:
                    req = request.NewFileRequest.fromJSON(data)
                    self.dataBase.newFile(
                        self.username,
                        req.fileName,
                    )
                    resp = response.OkResponse(
                        action=f'Create new file {req.fileName}')
                elif req.type == MessageType.DELETE_FILE:
                    req = request.DeleteFileRequest.fromJSON(data)
                    ownedOrShared = self.dataBase.deleteFile(
                        self.username,
                        req.fileID,
                    )
                    resp = response.OkResponse(
                        action=f'Delete {ownedOrShared} file { req.fileID }')
                elif req.type == MessageType.NEW_SHARE:
                    req = request.NewShareRequest.fromJSON(data)
                    self.dataBase.newShare(
                        req.fileID,
                        self.username,
                        req.user,
                    )
                    resp = response.OkResponse(
                        action=f'Share file {req.fileID} to {req.user}')
                elif req.type == MessageType.DELETE_SHARE:
                    req = request.DeleteShareRequest.fromJSON(data)
                    self.dataBase.deleteShare(
                        req.fileID,
                        self.username,
                        req.user,
                    )
                    resp = response.OkResponse(
                        action=f'Unshare file {req.fileID} from {req.user}')
                else:
                    raise DatabaseException(f'Unknown action: {req.type}')
            except DatabaseException as ex:
                resp = response.ErrResponse(err=f'{ex}')
                log.error(
                    'Session %s of user %s: Request:%s Response:%s',
                    self.sessionID,
                    self.username,
                    req,
                    resp,
                )
            except (JSONDecodeError, TypeError, AttributeError) as ex:
                resp = response.ErrResponse(err=f'Malformed request: {ex}')
                log.error(
                    'Session %s of user %s: %s',
                    self.sessionID,
                    self.username,
                    resp.description,
                )
                break
            except ConnectionAbortedError:
                break
            else:
                log.info(
                    'Session %s of user %s: Request:%s Response:%s',
                    self.sessionID,
                    self.username,
                    req,
                    resp,
                )
            transfer.send(self.request, resp)
        log.info('Closed session %s of user %s', self.sessionID, self.username)
