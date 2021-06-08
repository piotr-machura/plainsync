from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton

from common import request
from common import response
from common import transfer

from client.errors import FunnyClassForErrorMsg

class ShareWindow(QWidget):
    def __init__(self, files_data):
        super(QWidget, self).__init__()
        self.setGeometry(300, 300, 350, 200)
        self.setWindowTitle("Title")

        self.files_data = files_data
        self.connection = None

        self.initUI()

    def initUI(self):
        self.userLabel = QtWidgets.QLabel(self)
        self.userLabel.setText("User: ")
        self.userLabel.move(70, 50)

        self.userTextBox = QtWidgets.QLineEdit(self)
        self.userTextBox.move(150, 50)

        self.file = QtWidgets.QLabel(self)
        self.file.setText("Select file")
        self.file.move(70, 80)

        self.cb = QtWidgets.QComboBox(self)
        files = [file for file, fileID in self.files_data]
        self.cb.addItems(files)
        self.cb.move(120, 80)

        self.shareButton = QPushButton(self)
        self.shareButton.setText("Share")
        self.shareButton.move(100, 150)
        self.shareButton.clicked.connect(self.shareButtonPressed)

        self.deleteShareButton = QPushButton(self)
        self.deleteShareButton.setText("Delete share")
        self.deleteShareButton.move(200, 150)
        self.deleteShareButton.clicked.connect(self.deleteShareButtonPressed)

    def shareButtonPressed(self):
        user = self.userTextBox.text()
        fileID = [fileID for file, fileID in self.files_data if file == self.cb.currentText()][0]
        req = request.NewShareRequest(fileID, user)
        transfer.send(self.connection, req)
        resp = response.FileListResponse.fromJSON(transfer.recieve(self.connection))
        FunnyClassForErrorMsg().showMsg(self, resp.description)
        self.close()

    def deleteShareButtonPressed(self):
        user = self.userTextBox.text()
        fileID = [fileID for file, fileID in self.files_data if file == self.cb.currentText()][0]
        req = request.DeleteShareRequest(fileID, user)
        transfer.send(self.connection, req)
        resp = response.FileListResponse.fromJSON(transfer.recieve(self.connection))
        FunnyClassForErrorMsg().showMsg(self, resp.description)
        self.close()


    def set_connection(self, connection):
        self.connection = connection