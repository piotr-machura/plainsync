"""Transfer module.

This module contains a common tools for sending and recieving messages.
"""


def recieve(sock):
    """Recieve a message as a JSON string from the specified TCP socket.

    Returns:
        JSON representation of a Message, ready to be used in Message.fromJSON.
    Raises:
        ConnectionAbortedError when null is read from the first 8 bytes.
    """
    msgLen = int.from_bytes(sock.recv(2).strip(), byteorder='big')
    if msgLen == 0:
        raise ConnectionAbortedError
    return sock.recv(msgLen).decode('utf-8')


def send(socket, message):
    """
    Sends the message over a TCP connection on the specified socket.

    The message is encoed as a Bytes object where the first 8 bytes represent
    length of the UTF-8 message as uint64 in byteorder 'big', after which the
    message as UTF-8 encoded JSON bytes object follows.
    """
    payload = message.toJSON().encode('utf-8')
    payload = len(payload).to_bytes(2, byteorder='big', signed=False) + payload
    socket.sendall(payload)
