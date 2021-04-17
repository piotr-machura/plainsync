from libcommon.request import Request, PullRequest, AuthRequest
from libcommon.response import Response, OkResponse, ErrResponse
from libcommon.message import MessageType

# Server keeps the connected ID:user pairs here
SERVER_USERIDS = {}


# This emulates the server
def server(msgSent):
    rec = Request.fromJSON(msgSent)
    response = ErrResponse(
        action='Connection',
        err=f'Unknown action: {rec.type}',
    )
    if rec.userID is None:
        # By default the response of no userID is err
        response = ErrResponse(action='Connection', err='authenticate first')
        if rec.type == MessageType.AUTH:
            rec = AuthRequest.fromJSON(msgSent)
            # Server has this database
            SQL = {'user': '456', 'billy': '123'}
            description = f'Authenticate {rec.user}'
            if rec.user in SQL.keys() and SQL[rec.user] == rec.passwd:
                # Hash of username, time and IP address
                ID = '0987'
                # Add our suer to the active sessions database
                SERVER_USERIDS.update({ID: rec.user})
                response = OkResponse(userID=ID, action=description)
            else:
                response = ErrResponse(
                    action=description,
                    err='Wrong username or password',
                )
    else:
        if rec.userID not in SERVER_USERIDS:
            response = ErrResponse(
                userID=rec.userID,
                action='Connection',
                err=f'Unknown userID: {rec.userID}')
        elif rec.type == MessageType.PULL:
            rec = PullRequest.fromJSON(msgSent)
            descitption = f'Pull file {rec.file}'
            # Database of files and users allowed to use them
            SQL = {'a.txt': {'billy', 'user'}}
            if rec.file in SQL.keys() and SERVER_USERIDS[rec.userID] in SQL[
                    rec.file]:
                response = OkResponse(
                    userID=rec.userID,
                    action=descitption,
                    content='(file contents). Hello world!',
                )
            else:
                response = ErrResponse(
                    userID=rec.userID,
                    action=descitption,
                    err=
                    f'User {SERVER_USERIDS[rec.userID]} has no file {rec.file}.'
                )
        elif rec.type == MessageType.PUSH:
            # Same here but I'm lazy
            pass
    return response.toJSON()


# CLIENT
# ------
# Try to authenticate
aur = AuthRequest(user='billy', passwd='1234')
# Send it to a server as JSON
msg = aur.toJSON()
# Recieve it as a JSON and parse
resp = Response.fromJSON(server(msg))
if resp.type == MessageType.OK:
    # Save my ID for future connections
    myID = resp.userID
    # Try to pull a file
    pr = PullRequest(userID=myID, file='a.txt')
    msg = pr.toJSON()
    resp = Response.fromJSON(server(msg))
    if resp.type == MessageType.OK:
        print(resp.content)
    else:
        print(resp.message)
else:
    print(resp.message)
