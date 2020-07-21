from io import BufferedReader, BytesIO
from struct import unpack
import requests
import socket
import json


class Reader(BufferedReader):
    def __init__(self, initial_bytes):
        super().__init__(BytesIO(initial_bytes))

    def readString(self):
        length = self.readUInt32()
        if length == pow(2, 32) - 1:
            return ''
        else:
            try:
                decoded = self.read(length)
            except MemoryError:
                raise IndexError("String out of range.")
            else:
                return decoded.decode('utf-8')

    def readUInt32(self):
        return unpack('>I', self.read(4))[0]

    def readUInt8(self):
        return unpack('>B', self.read(1))[0]

    def readInt8(self):
        return unpack('>b', self.read(1))[0]

    readUByte = readUInt8
    readByte = readInt8


class Writer:
    def __init__(self):
        self.buffer = b''
        self.header = b''

    def writeInt32(self, data, length=4):
        self.buffer += data.to_bytes(length, 'big')

    def writeString(self, string=None):
        self.writeInt32(len(string))
        self.buffer += string.encode('utf-8')

    def sendPacket(self):
        self.writeInt32(2)
        self.writeInt32(11)
        self.writeInt32(28)
        self.writeInt32(0)
        self.writeInt32(178)
        self.writeString('')
        self.writeInt32(2)
        self.writeInt32(2)
        self.header += (10100).to_bytes(2, 'big')
        self.header += len(self.buffer).to_bytes(3, 'big')
        self.header += (0).to_bytes(2, 'big')
        return self.header + self.buffer


def recvall(sock, size):
    data = b''
    while size > 0:
        sock.settimeout(5.0)
        s = sock.recv(size)
        sock.settimeout(None)
        if not s:
            raise EOFError
        data += s
        size -= len(s)
    return data


class Downloader(Reader):
    def __init__(self):
        s = socket.socket()
        s.connect(("game.brawlstarsgame.com", 9339))
        s.send(Writer().sendPacket())
        header = s.recv(7)
        size = int.from_bytes(header[2:5], 'big')
        data = recvall(s, size)
        super().__init__(data)
        code = self.readUInt32()
        self.finger = json.loads(self.readString())
        self.readString()
        self.readString()
        self.readString()
        self.readString()
        self.readUInt32()
        self.readByte()
        self.readUInt32()
        self.readUInt32()
        self.content_url = self.readString()
        self.assets_url = self.readString()

    def get(self, filename):
        return requests.get(f'{self.content_url}/{self.finger["sha"]}/{filename}').content


if __name__ == '__main__':
    Downloader().get()
