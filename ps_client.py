"""Client executable module."""

import time
import socket

from common import request
from common import response
from common.message import MessageType
from common import transfer

HOST = '185.238.73.50'    # The server's hostname or IP address
PORT = 9999    # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    req = request.AuthRequest(user='billy', passwd='123')
    # Send it to a server as JSON
    transfer.send(s, req)
    resp = response.AuthResponse.fromJSON(transfer.recieve(s))
    if resp.type == MessageType.ERR:
        print(resp.description)
        s.close()
        exit(1)
    # Save my ID for future connections
    myID = resp.sessionID
    # Request files owned and borrowed by the user
    print(myID)
    req = request.NewFileRequest(fileName='b.txt')
    transfer.send(s, req)
    resp = response.OkResponse.fromJSON(transfer.recieve(s))
    print(resp)
    req = request.FileListRequest()
    transfer.send(s, req)
    resp = response.FileListResponse.fromJSON(transfer.recieve(s))
    if resp.type == MessageType.ERR:
        print(resp.description)
        s.close()
        exit(1)
    for fileID, data in resp.files.items():
        if data['name'] == 'b.txt':
            print(data)
            req = request.PushRequest(fileID=fileID, content='NEW BFILE 2')
            transfer.send(s, req)
            resp = response.OkResponse.fromJSON(transfer.recieve(s))
            print(resp)
            req = request.PullRequest(fileID=fileID)
            transfer.send(s, req)
            resp = response.PullResponse.fromJSON(transfer.recieve(s))
            print(resp.content)
