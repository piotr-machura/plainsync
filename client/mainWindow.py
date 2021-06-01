from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow

from common import request
from common import response
from common.message import MessageType
from common import transfer

from client.operatingWindow import OperatingWindow
from client.connection import Connection
from client.errors import FunnyClassForErrorMsg


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
            FunnyClassForErrorMsg().showMsg(self, "Type Login and Password")
        else:
            self.username = self.loginTextBox.text()
            self.passwd = self.passwordTextBox.text()

            s = Connection().getSocket()
            req = request.AuthRequest(user=self.username, passwd=self.passwd)
            transfer.send(s, req)
            resp = response.AuthResponse.fromJSON(transfer.recieve(s))
            if resp.type == MessageType.ERR:
                FunnyClassForErrorMsg().showMsg(self, resp.description)
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
