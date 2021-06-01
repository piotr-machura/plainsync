import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QTextEdit, QPushButton, QInputDialog

import socket

from common import request
from common import response
from common.message import MessageType
from common import transfer


class FunnyClassForErrorMsg:
    def showError(self, cls, msg):
        QMessageBox.question(cls, 'Error', msg, QMessageBox.Ok,
                             QMessageBox.Ok)


class Connection:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('piotr-machura.com', 9999))

    def getSocket(self):
        return self.s


class OperatingWindow(QWidget):
    def __init__(self, user):
        super(QWidget, self).__init__()
        self.setGeometry(300, 300, 500, 350)
        self.setWindowTitle("Title")

        self.user = user
        self.connection = None

        self.initUserBoard()

    def initUserBoard(self):
        container = QtWidgets.QHBoxLayout()
        buttonPanel = QtWidgets.QVBoxLayout()

        self.fileList = QTextEdit()
        self.fileList.setReadOnly(True)
        self.fileList.setMaximumSize(300, 300)
        self.fileList.setText(f'Files for user: \n{self.user}')

        self.openButton = QPushButton("Open")
        self.openButton.clicked.connect(self.openButtonClicked)

        self.addButton = QPushButton("Add new file")
        self.addButton.clicked.connect(self.addButtonClicked)

        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(self.deleteButtonClicked)

        self.newShareButton = QPushButton("New share")
        self.newShareButton.clicked.connect(self.newSharebuttonClicked)

        self.deleteShareButton = QPushButton("Delete share")
        self.deleteShareButton.clicked.connect(self.deleteSharebuttonClicked)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self.closeButtonClicked)

        container.addWidget(self.fileList)

        buttonPanel.addWidget(self.openButton)
        buttonPanel.addWidget(self.addButton)
        buttonPanel.addWidget(self.deleteButton)
        buttonPanel.addWidget(self.newShareButton)
        buttonPanel.addWidget(self.closeButton)

        container.addLayout(buttonPanel)
        self.setLayout(container)

    def set_connection(self, connection):
        self.connection = connection

    def openButtonClicked(self):
        req = request.FileListRequest()
        transfer.send(self.connection, req)
        resp = response.FileListResponse.fromJSON(transfer.recieve(self.connection))
        if resp.type == MessageType.ERR:
            print(resp.description)
        else:
            for fileID, data in resp.files.items():
                print(data)

    def addButtonClicked(self):
        text, ok = QInputDialog.getText(self, 'Creating new file', 'Type filename')
        if ok:
            req = request.NewFileRequest(fileName=text)
            transfer.send(self.connection, req)
            resp = response.OkResponse.fromJSON(transfer.recieve(self.connection))
            FunnyClassForErrorMsg().showError(self, resp.description)
            self.refreshFileList()

    def deleteButtonClicked(self):
        file, okPressed = QInputDialog.getItem(self, "Select file to delete", "Files:", self.files, 0, False)
        if okPressed and file:
            fileID = ["{} {}".format(index1, index2) for index1, value1
                      in enumerate(self.filesID) for index2, value2 in enumerate(value1) if value2 == file]
            num = int(fileID[0][0])
            fileID = self.filesID[num][1]
            req = request.DeleteFileRequest(fileID)
            transfer.send(self.connection, req)
            resp = response.ErrResponse.fromJSON(transfer.recieve(self.connection))
            FunnyClassForErrorMsg().showError(self, resp.description)
            self.refreshFileList()

    def newSharebuttonClicked(self):
        pass

    def deleteSharebuttonClicked(self):
        pass

    def closeButtonClicked(self):
        self.close()

    def refreshFileList(self):
        req = request.FileListRequest()
        transfer.send(self.connection, req)
        resp = response.FileListResponse.fromJSON(transfer.recieve(self.connection))
        if resp.type == MessageType.ERR:
            QMessageBox.question(self, 'Error', resp.description, QMessageBox.Ok,
                                 QMessageBox.Ok)
        else:
            files = [data["name"] for fileID, data in resp.files.items() if data['owner'] == self.user]
            self.filesID = [[data["name"], fileID] for fileID, data in resp.files.items() if data['owner'] == self.user]
            self.files = files

            self.fileList.setText(''.join(self.files))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.operatingWindow = None
        self.setGeometry(300, 300, 500, 350)
        self.setWindowTitle("Title")
        self.initUI()

        # niezabespieczone dane, hakerzy mozecie tutaj patrzec
        self.passwd = None
        self.username = None

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Hello!")
        self.label.move(220, 20)

        self.loginLabel = QtWidgets.QLabel(self)
        self.loginLabel.setText("Login:")
        self.loginLabel.move(180, 100)

        self.passwordLabel = QtWidgets.QLabel(self)
        self.passwordLabel.setText("Password:")
        self.passwordLabel.move(180, 140)

        self.loginButton = QtWidgets.QPushButton(self)
        self.loginButton.setText("Login")
        self.loginButton.clicked.connect(self.loginButtonClicked)
        self.loginButton.move(250, 200)

        self.loginTextBox = QtWidgets.QLineEdit(self)
        self.loginTextBox.move(250, 100)

        self.passwordTextBox = QtWidgets.QLineEdit(self)
        self.passwordTextBox.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordTextBox.move(250, 140)

    def loginButtonClicked(self):
        loginBoxValue = self.loginTextBox.text()
        passwordBoxValue = self.passwordTextBox.text()

        if (not loginBoxValue) or (not passwordBoxValue):
            FunnyClassForErrorMsg().showError(self, "Type Login and Password")
        else:
            self.username = self.loginTextBox.text()
            self.passwd = self.passwordTextBox.text()

            s = Connection().getSocket()
            req = request.AuthRequest(user=self.username, passwd=self.passwd)
            print(1)
            transfer.send(s, req)
            print(2)
            resp = response.AuthResponse.fromJSON(transfer.recieve(s))
            print(3)
            print(resp)
            if resp.type == MessageType.ERR:
                FunnyClassForErrorMsg().showError(self, resp.description)
            else:
                if self.operatingWindow is None:
                    self.operatingWindow = OperatingWindow(self.username)
                    self.operatingWindow.set_connection(s)
                    self.operatingWindow.refreshFileList()
                    self.operatingWindow.show()
                    self.hide()
                else:
                    self.operatingWindow.close()
                    self.operatingWindow = None


def main():
    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
