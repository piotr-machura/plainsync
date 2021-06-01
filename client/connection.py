import socket


class Connection:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('piotr-machura.com', 9999))

    def getSocket(self):
        return self.s
