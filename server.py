from libcommon.request import *
from libcommon.response import *
from libcommon.message import MessageType

# A wannabe SQL database
SERVER_USERIDS = {}
USERS = {'user': '456', 'billy': '123'}
FILES = {
    'a.txt': {
        'owner': 'user',
        'users': {'billy'},
        'content': 'conent of file a.txt',
    },
    'b.txt': {
        'owner': 'billy',
        'users': {},
        'content': 'conent of file b.txt',
    },
    'c.txt': {
        'owner': 'user',
        'users': {},
        'content': 'conent of file b.txt',
    },
}


def authenticate(rec):
    current_action = f'Authenticate {rec.user}'
    if rec.user in USERS and USERS[rec.user] == rec.passwd:
        # Hash of username, time and IP address
        ID = '0987'
        # Add our suer to the active sessions database
        SERVER_USERIDS.update({ID: rec.user})
        return AuthResponse(
            userID=ID,
            user=rec.user,
        )
    return ErrResponse(
        action=current_action,
        err='Wrong username or password',
    )


# This emulates the server AND IS VERY UGLY
def server(msgSent):
    rec = Request.fromJSON(msgSent)
    response = ErrResponse(
        action='Connection',
        err=f'Unknown action: {rec.type}',
    )
    if rec.userID is None:
        response = ErrResponse(action='Connection', err='authenticate first')
        if rec.type == MessageType.AUTH:
            # Try to atuhenticate
            rec = AuthRequest.fromJSON(msgSent)
            return authenticate(rec).toJSON()
    else:
        # userID not empty
        if rec.userID not in SERVER_USERIDS:
            # Not empty but invalid - respond with error
            response = ErrResponse(
                action='Connection', err=f'Unknown userID: {rec.userID}')
        elif rec.type == MessageType.LIST_FILES:
            username = SERVER_USERIDS[rec.userID]
            filelist = dict()
            for f in FILES:
                if FILES[f]['owner'] == username:
                    filelist[f] = username
                elif username in FILES[f]['users']:
                    filelist[f] = FILES[f]['owner']
            return FileListResponse(filelist).toJSON()
        elif rec.type == MessageType.PULL:
            # Not empty and valid - pull the file contents
            rec = PullRequest.fromJSON(msgSent)
            current_action = f'Pull file {rec.file}'
            # Database of files and users allowed to use them
            if rec.file in FILES.keys() and (
                    SERVER_USERIDS[rec.userID] in FILES[rec.file]['users']
                    or SERVER_USERIDS[rec.userID] == FILES[rec.file]['owner']):
                response = PullResponse(
                    file=rec.file,
                    content=FILES[rec.file]['content'],
                )
            else:
                response = ErrResponse(
                    action=current_action,
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
req = AuthRequest(user='billy', passwd='123')
# Send it to a server as JSON
msg = req.toJSON()
# Recieve it as a JSON and parse
resp = AuthResponse.fromJSON(server(msg))
if resp.type == MessageType.ERR:
    print(resp.description)
    exit(1)
# Save my ID for future connections
myID = resp.userID
# Request files owned and borrowed by the user
req = FileListRequest(myID)
re = server(req.toJSON())
resp = FileListResponse.fromJSON(re)
if resp.type == MessageType.ERR:
    print(resp.description)
    exit(1)
files = resp.files
# Pull the files owned/borrowed by the user
for f in files:
    ownership = files[f]
    pr = PullRequest(userID=myID, file=f)
    msg = pr.toJSON()
    re = server(msg)
    resp = PullResponse.fromJSON(re)
    if resp.type == MessageType.ERR:
        print(resp.description)
        exit(1)
    print(f'{f} (owner: {ownership})')
    print(resp.content)
