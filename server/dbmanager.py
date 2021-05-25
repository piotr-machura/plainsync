"""Database manager module.

Processes request to read/write the database and/or the user files. Raises
DatabaseException if things go wrong.
"""
import sqlite3
import time
import os
import hashlib
from server import config

# Initial database setup
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
            id TEXT,
            user TEXT,
            file TEXT
        );
        ''')
    con.commit()


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
            SELECT * FROM "Users" WHERE "username"=? AND "password"=?;
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
            fileList[row[0]]['shares'] = self.dbConnection.execute(
                '''
                SELECT id, user FROM Shares WHERE file=?
                ''',
                (row[0], ),
            ).fetchall()
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
            SELECT 1 FROM Files WHERE id=? AND owner=?
            ''',
            (fileID, username),
        ).fetchone() or self.dbConnection.execute(
                '''
                SELECT 1 FROM Shares WHERE file=? AND user=?
                ''',
            (fileID, username),
        ).fetchone():
            with open(config.STORAGE + os.sep + fileID) as fRequested:
                return fRequested.read()
        raise DatabaseException(
            f'User {username} has no access to file {fileID}')

    def newFile(self, username, fileName):
        """Create new file for specified user.
        """
        if self.dbConnection.execute(
                '''
            SELECT * FROM Files WHERE owner=? AND name=?
            ''',
            (username, fileName),
        ).fetchall():
            raise DatabaseException(
                f'User {username} already has a file named {fileName}')
        fileID = str(time.time()) + username + fileName
        fileID = hashlib.sha1(fileID.encode('utf-8')).hexdigest()
        self.dbConnection.execute(
            '''
            INSERT INTO Files VALUES (?,?,?,?,?,?)
        ''', (
                fileID,
                fileName,
                username,
                time.strftime(config.DATETIME_FMT),
                time.strftime(config.DATETIME_FMT),
                username,
            ))
        self.dbConnection.commit()

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
            SELECT 1 FROM Files WHERE id=? AND owner=?
            ''',
            (fileID, username),
        ).fetchone() or self.dbConnection.execute(
        # Or the file has been shared with him
                '''
            SELECT 1 FROM Shares WHERE file=? AND user=?
            ''',
            (fileID, username),
        ).fetchone():
            with open(config.STORAGE + os.sep + fileID, "w") as fRequested:
                fRequested.write(contents)
            self.dbConnection.execute(
                '''
                UPDATE Files SET last_edited=?, last_edited_user=? WHERE id=?
                ''',
                (time.strftime(config.DATETIME_FMT), username, fileID),
            )
            self.dbConnection.commit()
        else:
            raise DatabaseException(
                f'User {username} has no access to file {fileID}')
