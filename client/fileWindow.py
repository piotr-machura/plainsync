from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit

from common import request
from common import response
from common import transfer

from client.errors import FunnyClassForErrorMsg

class fileWindow(QWidget):
    def __init__(self, filename, fileID, content):
        super(QWidget, self).__init__()
        self.setGeometry(300, 300, 350, 350)
        self.setWindowTitle(filename)
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.connection = None
        self.filename = filename
        self.fileID = fileID
        self.content = content

        self.initUI()

    def initUI(self):
        container = QtWidgets.QVBoxLayout()
        buttonPanel = QtWidgets.QHBoxLayout()

        self.textEdit = QTextEdit(self)
        self.textEdit.setMaximumSize(300, 320)
        self.textEdit.setText(self.content)

        self.saveButton = QPushButton(self)
        self.saveButton.setText("Save")
        self.saveButton.move(320, 100)
        self.saveButton.clicked.connect(self.saveButtonPressed)

        self.closeButton = QPushButton(self)
        self.closeButton.setText("Close")
        self.closeButton.move(320, 50)
        self.closeButton.clicked.connect(self.closeButtonPressed)

        container.addWidget(self.textEdit)

        buttonPanel.addWidget(self.saveButton)
        buttonPanel.addWidget(self.closeButton)

        container.addLayout(buttonPanel)
        self.setLayout(container)

    def saveButtonPressed(self):
        content = self.textEdit.toPlainText()

        req = request.PushRequest(fileID=self.fileID, content=content)
        transfer.send(self.connection, req)
        resp = response.OkResponse.fromJSON(transfer.recieve(self.connection))
        FunnyClassForErrorMsg().showMsg(self, resp.description)

        self.close()

    def closeButtonPressed(self):
        self.close()

    def set_connection(self, connection):
        self.connection = connection
