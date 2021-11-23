import struct

class pASCII_packet(object):

    y = 0
    x = 0
    ch = 0
    msg = b''
    detail = b''
    packer = struct.Struct('I I I 16s 16s')
    size = packer.size

    def __str__(self):
        return (
            'y: '+str(self.y)
            +'; x: '+str(self.x)
            +'; ch: '+str(self.ch)
            +'; msg: '+str(self.msg.decode('utf-8'))
            +'; detail: '+str(self.detail.decode('utf-8'))
        )
    def unpack(self, data):
        try:
            self.y, self.x, self.ch, self.msg, self.detail = self.packer.unpack(data)
        except:
            pass
        return self

    def pack(self):
        unpacked = (self.y, self.x, self.ch, self.msg, self.detail)
        return self.packer.pack(*unpacked)
