"""Database manager module.

Processes request to read/write the database and/or the user files.
"""
from common import response

# A wannabe SQL database
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
        'content': 'file\nb.txt\n more content',
    },
    'c.txt': {
        'owner': 'user',
        'users': {},
        'content': 'conent of\nfile c.txt\n more contentss',
    },
}

def authenticate(user, passwd):
    """Authenticate the user.

    Args:
        user: username to authenticate.
        passwd: password to authenticate.

    Returns:
        `True` if authenticated and `False` if not.
    """
    return user in USERS and USERS[user] == passwd

def listFiles(username):
    """List files availible for a given user.

    Args:
        username (str): the user for which the files should be listed.

    Returns:
        FileListResponse with files availible to the user.
    """
    filelist = dict()
    for file in FILES:
        if FILES[file]['owner'] == username:
            filelist[file] = username
        elif username in FILES[file]['users']:
            filelist[file] = FILES[file]['owner']
    return response.FileListResponse(filelist)


def pullFile(username, file):
    """Pull file contents from the server.

    Args:
        username: the user requesting the file contents.
        file: name of the file to be pulled.

    Returns:
        PullResponse if the pull is succesfull or ErrResponse if it is not.
    """
    # Database of files and users allowed to use them
    if file in FILES.keys() and (
            username in FILES[file]['users']
            or username == FILES[file]['owner']):
        return response.PullResponse(
            file=file,
            content=FILES[file]['content'],
        )
    return response.ErrResponse(
        err=f'User {username} has no access to file {file}')

def pushFile(username, file, contents):
    """Push file contents to the server.

    Args:
        username: the user requesting the modification.
        file: the file to be modified.
        contents: the file contents.

    Returns:
        PushResponse if the push is succesfull or ErrResponse if it is not.
    """
    return response.ErrResponse(err='Pushing not implemented')
