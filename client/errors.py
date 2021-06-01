from PyQt5.QtWidgets import QMessageBox


class FunnyClassForErrorMsg:
    def showMsg(self, cls, msg):
        QMessageBox.question(cls, 'Error', msg, QMessageBox.Ok,
                             QMessageBox.Ok)
