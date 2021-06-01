"""Database manager module.

Processes request to read/write the database and/or the user files. Raises
DatabaseException if things go wrong.
"""
import sqlite3
import time
import os
import hashlib
import sys
from logging import error, debug
from server import config

# Initial database schema
try:
    with sqlite3.connect(config.DATABASE) as con:
        con.execute(
            '''
            CREATE TABLE IF NOT EXISTS Files (
                id TEXT,
                name TEXT,
                owner TEXT,
                created TEXT,
                last_edited TEXT,
                last_edited_user TEXT
            );
            ''')
        con.execute(
            '''
            CREATE TABLE IF NOT EXISTS Users (
                username TEXT,
                password TEXT
            );
            ''')
        con.execute(
            '''
            CREATE TABLE IF NOT EXISTS Shares (
                user TEXT,
                file TEXT
            );
            ''')
        con.commit()
except (sqlite3.DatabaseError, sqlite3.OperationalError) as ex:
    error(f'Fatal error creating database at {config.DATABASE}: {ex}')
    sys.exit(1)
else:
    debug(f'Initialized database at {config.DATABASE}')


class DatabaseException(Exception):
    """Database exception class."""


class DatabaseManager:
    """Database manager class.

    Wraps an sqlite connection to provide database access to TCPHandler.
    """
    def __init__(self):
        self.dbConnection = sqlite3.connect(config.DATABASE)

    def __del__(self):
        self.dbConnection.close()

    def authenticate(self, user, passwd):
        """Authenticate the user.

        Args:
            user: username to authenticate.
            passwd: password to authenticate.

        Raises:
            DatabaseException if not authenticated.
        """
        if not self.dbConnection.execute(
                '''
            SELECT * FROM Users WHERE username=? AND password=?;
            ''',
            (user, passwd),
        ).fetchone():
            raise DatabaseException('Invalid username or password')

    def listFiles(self, username):
        """List files available for a given user.

        Args:
            username: the user for which the files should be listed.

        Returns:
            Dictionary of (file ID, (info)) pairs, where the ID is the unique
            ID assigned to every file and info is a dicitonary that contains
            information about the owner, file name, last edited date and last
            edited user.
        Raises:
            DatabaseException if the user does not exist.
        """
        fileList = dict()
        owned = self.dbConnection.execute(
            '''
            SELECT * FROM Files WHERE owner=?;
            ''',
            (username, ),
        ).fetchall()

        sharedIDs = [
            fileID[0] for fileID in self.dbConnection.execute(
                '''
            SELECT file FROM Shares WHERE user=?;
            ''',
                (username, ),
            )
        ]
        borrowed = [
            self.dbConnection.execute(
                '''
                SELECT * FROM Files WHERE id=?;
                ''',
                (fileID, ),
            ).fetchone() for fileID in sharedIDs
        ]
        for row in owned:
            fileList[row[0]] = dict()
            fileList[row[0]]['name'] = row[1]
            fileList[row[0]]['owner'] = row[2]
            fileList[row[0]]['created'] = row[3]
            fileList[row[0]]['last_edited'] = row[4]
            fileList[row[0]]['last_edited_user'] = row[5]
            fileList[row[0]]['shares'] = [
                user[0] for user in self.dbConnection.execute(
                    '''
                SELECT user FROM Shares WHERE file=?;
                ''',
                    (row[0], ),
                ).fetchall()
            ]
        for row in borrowed:
            fileList[row[0]] = dict()
            fileList[row[0]]['name'] = row[1]
            fileList[row[0]]['owner'] = row[2]
            fileList[row[0]]['created'] = row[3]
            fileList[row[0]]['last_edited'] = row[4]
            fileList[row[0]]['last_edited_user'] = row[5]
        return fileList

    def pullFile(self, username, fileID):
        """Pull file contents from the server.

        Args:
            username: the user requesting the file contents.
            fileID: ID of the file to be pulled.

        Returns:
            Contents of the specified file.

        Raises:
            DatabaseException if user has no access to specified file.
        """
        if self.dbConnection.execute(
                '''
            SELECT 1 FROM Files WHERE id=? AND owner=?;
            ''',
            (fileID, username),
        ).fetchone() or self.dbConnection.execute(
                '''
                SELECT 1 FROM Shares WHERE file=? AND user=?;
                ''',
            (fileID, username),
        ).fetchone():
            with open(config.STORAGE + os.sep + fileID) as fRequested:
                return fRequested.read()
        raise DatabaseException(
            f'User {username} has no access to file {fileID}')

    def newFile(self, username, fileName):
        """Create new file for specified user.

        Args:
            username: the user requesting new file.
            fileName: the name of the new file.

        Raises:
            DatabaseException
        """
        if self.dbConnection.execute(
                '''
            SELECT * FROM Files WHERE owner=? AND name=?;
            ''',
            (username, fileName),
        ).fetchall():
            raise DatabaseException(
                f'User {username} already has a file named {fileName}')
        fileID = str(time.time()) + username + fileName
        fileID = hashlib.sha1(fileID.encode('utf-8')).hexdigest()
        self.dbConnection.execute(
            '''
            INSERT INTO Files
            (id, name, owner, created, last_edited, last_edited_user)
            VALUES (?,?,?,?,?,?);
        ''', (
                fileID,
                fileName,
                username,
                time.strftime(config.DATETIME_FMT),
                time.strftime(config.DATETIME_FMT),
                username,
            ))
        self.dbConnection.commit()
        newFile = open(config.STORAGE + os.sep + fileID, 'w')
        newFile.close()

    def pushFile(self, username, fileID, contents):
        """Push file contents to the server.

        Args:
            username: the user requesting the modification.
            fileID: the file ID to be modified.
            contents: the file contents.

        Raises:
            DatabaseException if user has no access to specified file.
        """
        # Check if the user owns the file
        if self.dbConnection.execute(
                '''
            SELECT 1 FROM Files WHERE id=? AND owner=?;
            ''',
            (fileID, username),
        ).fetchone() or self.dbConnection.execute(
        # Or the file has been shared with him
                '''
            SELECT 1 FROM Shares WHERE file=? AND user=?;
            ''',
            (fileID, username),
        ).fetchone():
            with open(config.STORAGE + os.sep + fileID, 'w') as fRequested:
                fRequested.write(contents)
            self.dbConnection.execute(
                '''
                UPDATE Files SET last_edited=?, last_edited_user=? WHERE id=?;
                ''',
                (time.strftime(config.DATETIME_FMT), username, fileID),
            )
            self.dbConnection.commit()
        else:
            raise DatabaseException(
                f'User {username} has no access to file {fileID}')

    def deleteFile(self, username, fileID):
        """Delete the specified file.

        If the user owns the file then it is deleted permanently, if it has
        been shared then the share is deleted, but file is still available for
        the owner and other shared users.

        Args:
            username: the user requesting deletion.
            fileID: ID of file to be deleted.

        Returns:
            String "owned" if the file was owned by the user, "shared" if it
            was shared.

        Raises:
            DatabaseException if user has no acces to specified file.
        """
        # Check if the user owns the file -> delete it and all the shares
        if self.dbConnection.execute(
                '''
            SELECT 1 FROM Files WHERE id=? AND owner=?;
            ''',
            (fileID, username),
        ).fetchone():
            self.dbConnection.execute(
                '''
                DELETE FROM Files WHERE id=?;
                ''',
                (fileID, ),
            )
            self.dbConnection.execute(
                '''
                DELETE FROM Shares WHERE file=?;
                ''',
                (fileID, ),
            )
            os.remove(config.STORAGE + os.sep + fileID)
            self.dbConnection.commit()
            return "owned"
        # Check if the user has the file shared -> delete the share
        if self.dbConnection.execute(
                '''
            SELECT 1 FROM Shares WHERE file=? AND user=?;
            ''',
            (fileID, username),
        ).fetchone():
            self.dbConnection.execute(
                '''
                DELETE FROM Shares WHERE file=? AND user=?;
                ''',
                (fileID, username),
            )
            self.dbConnection.commit()
            return "shared"
        # The does not own the file and has not shared it
        raise DatabaseException(
            f'User {username} has no access to file {fileID}')

    def newShare(self, fileID, username, userToShare):
        """Creates a new share of given file to specified user.

        Args:
            fileID: ID of file to be shared.
            username: the user requesting a share.
            userToShare: user to whom the file should be shared.

        Raises:
            DatabaseException if the user to share does not exist or already
            has the file shared or is the same as reqeusting user or the
            requesting user does not own the file.
        """
        # Handle all sorts of user errors
        if userToShare == username:
            raise DatabaseException('Cannot share to yourself')
        if not self.dbConnection.execute(
                '''
            SELECT 1 FROM Files WHERE id=? AND owner=?;
            ''',
            (fileID, username),
        ).fetchone():
            raise DatabaseException(f'User {username} does not own {fileID}')
        if not self.dbConnection.execute(
                '''
            SELECT 1 FROM Users WHERE username=?;
            ''',
            (userToShare, ),
        ).fetchone():
            raise DatabaseException(f'User {userToShare} does not exist')
        if self.dbConnection.execute(
                '''
            SELECT 1 FROM Shares WHERE file=? AND user=?;
            ''',
            (fileID, userToShare),
        ).fetchone():
            raise DatabaseException(
                f'User {userToShare} already has access to file {fileID}')
        # All possible errors handled -> proceed to creating a share
        self.dbConnection.execute(
            '''
            INSERT INTO Shares (file, user) VALUES (?, ?)
            ''',
            (fileID, userToShare),
        )
        self.dbConnection.commit()

    def deleteShare(self, fileID, username, userToUnshare):
        """Deletes a share of given file to specified user.

        Args:
            fileID: ID of file to unshared.
            username: the user requesting a deletion of share.
            userToUnshare: user to whom the file should no longer be shared.

        Raises:
            DatabaseException if the share does not exist or the
            requesting user does not own the file AND wnats to unshare someone
            other than himself.
        """
        # Requesting user is the owner
        if self.dbConnection.execute(
                '''
            SELECT 1 FROM Files WHERE id=? AND owner=?;
            ''',
            (fileID, username),
        ).fetchone() or username == userToUnshare:
            # Or user is unsharing himself ^
            if self.dbConnection.execute(
                    '''
                SELECT 1 FROM Shares WHERE file=? AND user=?
                ''',
                (fileID, userToUnshare),
            ).fetchone():
                self.dbConnection.execute(
                    '''
                    DELETE FROM Shares WHERE file=? AND user=?
                    ''',
                    (fileID, userToUnshare),
                )
                self.dbConnection.commit()
            else:
                raise DatabaseException(
                    f'File {fileID} is not shared to {userToUnshare}.')
        else:
            raise DatabaseException(
                f'Can\'t unshare file {fileID} from user {userToUnshare}.')
