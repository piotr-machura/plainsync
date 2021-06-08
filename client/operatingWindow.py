from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox, QWidget, QTextEdit, QPushButton, QInputDialog, QTreeWidget, QTreeWidgetItem

from common import request
from common import response
from common.message import MessageType
from common import transfer

from client.errors import FunnyClassForErrorMsg
from client.shareWindow import ShareWindow
from client.fileWindow import fileWindow


class OperatingWindow(QWidget):
    def __init__(self, user):
        super(QWidget, self).__init__()
        self.setGeometry(300, 300, 500, 350)
        self.setWindowTitle("Witam w pięknym programie")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.user = user
        self.connection = None

        self.initUserBoard()

    def initUserBoard(self):
        container = QtWidgets.QVBoxLayout()
        buttonPanel = QtWidgets.QHBoxLayout()

        self.fileTree = QTreeWidget(self)
        self.fileTree.setMaximumSize(500, 300)
        self.fileTree.setColumnCount(4)
        self.fileTree.setColumnWidth(0, 120)
        self.fileTree.setColumnWidth(1, 120)
        self.fileTree.setColumnWidth(2, 120)
        self.fileTree.setColumnWidth(3, 80)
        self.fileTree.setHeaderLabels(["Name", "Created", "Last Edit", "Last Editor"])

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

        container.addWidget(self.fileTree)

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
        seletedFile = self.fileTree.selectedItems()
        if seletedFile:
            filename = seletedFile[0].text(0)
            fileID = self.getFileID(filename)
            content = self.getFileContent(fileID)

            self.fileWindow = fileWindow(filename, fileID, content)
            self.fileWindow.set_connection(self.connection)
            self.fileWindow.show()

    def addButtonClicked(self):
        text, ok = QInputDialog.getText(self, 'Creating new file', 'Type filename')
        if ok:
            req = request.NewFileRequest(fileName=text)
            transfer.send(self.connection, req)
            resp = response.OkResponse.fromJSON(transfer.recieve(self.connection))
            FunnyClassForErrorMsg().showMsg(self, resp.description)
            self.refreshFileList()

    def deleteButtonClicked(self):
        seletedFile = self.fileTree.selectedItems()
        if seletedFile:
            filename = seletedFile[0].text(0)
            fileID = self.getFileID(filename)

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
            self.shared_files = [data["name"] for fileID, data in resp.files.items() if data['owner'] != self.user]
            self.filesID = [[data["name"], fileID] for fileID, data in resp.files.items() if data['owner'] == self.user]
            self.files = files

            files_dict = {f'Files for user {self.user}': files,
                          'Shared': self.shared_files}
            items = []
            for key, values in files_dict.items():
                item = QTreeWidgetItem([key])
                for value in values:
                    fileInfo = self.getFileInfo(value) #created, last_edit, last_edited_user
                    child = QTreeWidgetItem([value, fileInfo[0], fileInfo[1], fileInfo[2]])
                    item.addChild(child)
                items.append(item)

            self.fileTree.clear()
            self.fileTree.insertTopLevelItems(0, items)

    def getFileID(self, filename):
        req = request.FileListRequest()
        transfer.send(self.connection, req)
        resp = response.FileListResponse.fromJSON(transfer.recieve(self.connection))
        if resp.type == MessageType.ERR:
            QMessageBox.question(self, 'Error', resp.description, QMessageBox.Ok,
                                 QMessageBox.Ok)
        else:
            fileID = [fileID for fileID, data in resp.files.items() if data["name"] == filename]
            return fileID[0]

    def getFileInfo(self, filename):
        req = request.FileListRequest()
        transfer.send(self.connection, req)
        resp = response.FileListResponse.fromJSON(transfer.recieve(self.connection))
        if resp.type == MessageType.ERR:
            QMessageBox.question(self, 'Error', resp.description, QMessageBox.Ok,
                                 QMessageBox.Ok)
        else:
            fileInfo = [[data["created"], data["last_edited"], data["last_edited_user"]]
                      for fileID, data in resp.files.items() if data["name"] == filename]
            return fileInfo[0]

    def getFileContent(self, fileID):
        req = request.PullRequest(fileID)
        transfer.send(self.connection, req)
        resp = response.FileListResponse.fromJSON(transfer.recieve(self.connection))
        if resp.type == MessageType.ERR:
            QMessageBox.question(self, 'Error', resp.description, QMessageBox.Ok,
                                 QMessageBox.Ok)
        else:
            content = resp.content
            return content
