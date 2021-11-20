import struct

class pASCII_packet(object):

    y = 0
    x = 0
    ch = 0
    msg = ''
    detail = ''
    packer = struct.Struct('I I I s s')
    size = packer.size

    def unpack(self, data):
        try:
            self.y, self.x, self.ch, self.msg, self.detail = packer.unpack(data)
        except:
            pass
        return (self.y, self.x, self.ch, self.msg, self.detail)

    def pack(self):
        unpacked = (self.y, self.x, self.ch, self.msg, self.detail)
        return packer.pack(*unpacked)
