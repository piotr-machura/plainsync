from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QWidget, QTextEdit, QPushButton, QInputDialog

from common import request
from common import response
from common.message import MessageType
from common import transfer

from client.errors import FunnyClassForErrorMsg
from client.shareWindow import ShareWindow


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

        self.newShareButton = QPushButton("Share options")
        self.newShareButton.clicked.connect(self.newSharebuttonClicked)

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
            FunnyClassForErrorMsg().showMsg(self, resp.description)
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
            FunnyClassForErrorMsg().showMsg(self, resp.description)

            self.refreshFileList()

    def newSharebuttonClicked(self):
        self.newShareWindow = ShareWindow(self.filesID)
        self.newShareWindow.set_connection(self.connection)
        self.newShareWindow.show()

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
