from struct import *

from io import BufferedReader, BytesIO


class Reader(BufferedReader):
    def __init__(self, initial_bytes):
        super().__init__(BytesIO(initial_bytes))

    def readInteger(self, length: int = 1):
        return int.from_bytes(self.read(length), 'big', signed=True)

    def readUInt32(self):
        return unpack('>I', self.read(4))[0]

    def readInt32(self):
        return unpack('>i', self.read(4))[0]

    def readString(self):
        return self.read(self.readInteger(2)).decode('utf-8')

    def readUShort(self):
        return unpack('>H', self.read(2))[0]

    def readShort(self):
        return unpack('>h', self.read(2))[0]

    def readUFloat(self):
        return unpack('>F', self.read(4))

    def readFloat(self):
        return unpack('>f', self.read(4))[0]

    def readUByte(self):
        return unpack('>B', self.read(1))[0]

    def readByte(self):
        return unpack('>b', self.read(1))[0]

    def readVertex(self, shorts, scale, count):
        vertex = []
        for x1 in range(count):
            for x2 in range(shorts):
                vertex.append(self.readShort() / 32767 * scale)
        return vertex

    def readTexCoord(self, shorts, scale, count):
        vertex = []
        for x1 in range(count):
            for x2 in range(shorts):
                vertex.append(self.readShort() / 32512 * scale)
        return vertex

    def readColor(self, shorts, scale, count):
        vertex = []
        for x1 in range(count):
            for x2 in range(shorts):
                vertex.append(self.readShort() / 32512 * scale)
        return vertex

    def readMatrix(self):
        matrix = []
        for x1 in range(16):
            matrix.append(self.readFloat())
        return matrix

    def readWeights(self):
        jA = self.readUByte()
        jB = self.readUByte()
        jC = self.readUByte()
        jD = self.readUByte()
        wA = self.readUShort()
        wB = self.readUShort()
        wC = self.readUShort()
        wD = self.readUShort()
        return [[jA, wA], [jB, wB], [jC, wC], [jD, wD]]
