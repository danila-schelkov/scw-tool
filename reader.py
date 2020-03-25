from struct import unpack
from io import BufferedReader, BytesIO


class Reader(BufferedReader):
    def __init__(self, data: bytes):
        super().__init__(BytesIO(data))

    def readUnsignedInteger64(self):
        return unpack('>Q', self.read(8))[0]

    def readInteger64(self):
        return unpack('>q', self.read(8))[0]

    def readUnsignedInteger32(self):
        return unpack('>I', self.read(4))[0]

    def readInteger32(self):
        return unpack('>i', self.read(4))[0]

    def readUnsignedFloat(self):
        return unpack('>F', self.read(4))[0]

    def readFloat(self):
        return unpack('>f', self.read(4))[0]

    def readUnsignedShort(self):
        return unpack('>H', self.read(2))[0]

    def readShort(self):
        return unpack('>h', self.read(2))[0]

    def readUnsignedByte(self):
        return unpack('>B', self.read(1))[0]

    def readByte(self):
        return unpack('>b', self.read(1))[0]

    def readUnsignedInteger(self, lenght: int = 1):
        return int.from_bytes(self.read(lenght), 'big', signed=False)

    def readInteger(self, lenght: int = 1):
        return int.from_bytes(self.read(lenght), 'big', signed=True)

    def readString(self):
        return self.read(self.readShort()).decode('utf-8')

    readUInt64 = readUnsignedInteger64
    readInt64 = readInteger64
    readUInt32 = readUnsignedInteger32
    readInt32 = readInteger32
    readUFloat = readUnsignedFloat
    readUShort = readUnsignedShort
    readUByte = readUnsignedByte
    readUInt = readUnsignedInteger
    readStr = readString
