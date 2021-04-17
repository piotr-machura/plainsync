from libcommon.request import Request, PullRequest, AuthRequest
from libcommon.response import Response, OkResponse, ErrResponse, AuthResponse
from libcommon.message import MessageType

# Server keeps the connected ID:user pairs here
SERVER_USERIDS = {}

FILES = {
    'a.txt': {
        'users': {'user', 'billy'},
        'content': 'conent of file a.txt',
    },
    'b.txt': {
        'users': {'billy'},
        'content': 'conent of file b.txt',
    },
    'c.txt': {
        'users': {'user'},
        'content': 'conent of file b.txt',
    },
}

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
                response = AuthResponse(
                    userID=ID,
                    user=rec.user,
                    filelist=[key for key in FILES if rec.user in FILES[key]['users']],
                )
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
            if rec.file in FILES.keys() and SERVER_USERIDS[rec.userID] in FILES[
                    rec.file]['users']:
                response = OkResponse(
                    action=descitption,
                    content=FILES[rec.file]['content'],
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
aur = AuthRequest(user='billy', passwd='123')
# Send it to a server as JSON
msg = aur.toJSON()
# Recieve it as a JSON and parse
re = server(msg)
resp = Response.fromJSON(re)
if resp.type == MessageType.AUTH:
    resp = AuthResponse.fromJSON(re)
    # Save my ID for future connections
    myID = resp.userID
    # Try to pull a file
    for filename in resp.filelist:
        pr = PullRequest(userID=myID, file=filename)
        msg = pr.toJSON()
        resp = Response.fromJSON(server(msg))
        if resp.type == MessageType.OK:
            print(resp.content)
        else:
            print(resp.message)
else:
    print(resp.message)
