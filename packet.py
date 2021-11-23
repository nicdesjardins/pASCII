import struct

class pASCII_packet(object):

    ENCODING = 'utf-8'
    y = 0
    x = 0
    ch = 0
    msg = ''
    detail = ''
    packer = struct.Struct('I I I 16s 16s')
    size = packer.size

    def __str__(self):
        return (
            'y: '+str(self.y)
            +'; x: '+str(self.x)
            +'; ch: '+str(self.ch)
            +'; msg: '+str(self.msg)
            +'; detail: '+str(self.detail)
        )
    def unpack(self, data):
        try:
            self.y, self.x, self.ch, msgBytes, detailBytes = self.packer.unpack(data)
            self.msg = msgBytes.decode('utf-8-')
            self.msg = self.msg.rstrip("\x00")
            self.detailBytes = detailsBytes.decode(self.ENCODING)
        except:
            pass
        return self

    def pack(self):
        unpacked = (self.y, self.x, self.ch, self.msg.encode(self.ENCODING), self.detail.encode(self.ENCODING))
        return self.packer.pack(*unpacked)
