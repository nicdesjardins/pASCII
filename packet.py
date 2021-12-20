import pickle

class pASCII_packet(object):

    y = 0
    x = 0
    ch = 0
    msg = ''
    detail = ''
    size = 1024

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
            decoded = pickle.loads(data)
            self.y = decoded['y']
            self.x = decoded['x']
            self.ch = decoded['ch']
            self.msg = decoded['msg']
            self.detail = decoded['detail']
        except:
            pass
        return self

    def pack(self):
        return pickle.dumps(
            {
                'y': self.y,
                'x': self.x,
                'ch': self.ch,
                'msg': self.msg,
                'detail': self.detail,
            }
        )
