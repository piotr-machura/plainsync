"""Database manager module.

Processes request to read/write the database and/or the user files. Raises
DatabaseException if things go wrong.
"""


class DatabaseException(Exception):
    """Database exception class."""


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
        'users': {'user'},
        'content': 'file\nb.txt\n more content',
    },
    'c.txt': {
        'owner': 'billy',
        'users': {},
        'content': 'conent of\nfile c.txt\n more contentss',
    },
}


def authenticate(user, passwd):
    """Authenticate the user.

    Args:
        user: username to authenticate.
        passwd: password to authenticate.

    Raises:
        DatabaseException if not authenticated.
    """
    if user not in USERS or USERS[user] != passwd:
        raise DatabaseException('Invalid username or password')


def listFiles(username):
    """List files available for a given user.

    Args:
        username: the user for which the files should be listed.

    Returns:
        Dictionary of (file, users), where the users is a list of
        authenticated users OR a list with just the owner if it is different
        from the requesting user.

    Raises:
        DatabaseException if the user does not exist.
    """
    filelist = dict()
    if username not in USERS:
        raise DatabaseException(f'No such user: {username}')
    for file in FILES:
        if FILES[file]['owner'] == username:
            filelist[file] = [username] + list(FILES[file]['users'])
        elif username in FILES[file]['users']:
            filelist[file] = [FILES[file]['owner']]
    return filelist


def pullFile(username, file):
    """Pull file contents from the server.

    Args:
        username: the user requesting the file contents.
        file: name of the file to be pulled.

    Returns:
        Contents of the specified file.

    Raises:
        DatabaseException if user has no access to specified file.
    """
    # Database of files and users allowed to use them
    if file in FILES.keys() and (username in FILES[file]['users']
                                 or username == FILES[file]['owner']):
        return FILES[file]['content']
    raise DatabaseException(f'User {username} has no access to file {file}')


def pushFile(username, file, contents):
    """Push file contents to the server.

    Args:
        username: the user requesting the modification.
        file: the file to be modified.
        contents: the file contents.

    Raises:
        DatabaseException if user has no access to specified file.
    """
    raise DatabaseException('Pushing not implemented')
