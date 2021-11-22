from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import curses
import os


lastTenChars = []
RESET = 'reset'
QUIT = 'QUIT'
PRINTOUT = 'printout'
DIRECTIONAL_KEYS = { curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT }

class pASCII(object):

    def __init__(self):
        self.connectToServer()
    

    
    ch = ndch = '*'
    x = 0
    y = 0
    width, height, drawingWidth, drawingHeight = (None, None, None, None)
    prevCh = None
    enteredChars = []
    
    def start(self, window):

        self.window = window
        
        self.screen = curses.initscr()

        curses.setsyx(self.y, self.x)
        self.setBoundaries()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

        while True:
            curses.setsyx(self.y, self.x)
            self.prevCh = self.ch
            
            try:
                self.ch = self.screen.getch()
            except:
                pass

            if self.ch in DIRECTIONAL_KEYS:
#                self.screen.addstr("directional key pressed")
                self.goDirection(self.ch)
                self.addCharAtCoords()

            if self.hitEnterKey():
                self.goDown()
                if self.prevCh not in DIRECTIONAL_KEYS and not self.hitEnterKey(self.prevCh):
                    self.goLeft()
                self.addCharAtCoords()
            
            elif self.ch == curses.KEY_RESIZE:
                self.setBoundaries()

                if self.isHigher():
                    self.clearPreviousStatusLines()
            
            else:
                if self.ch >= 0:
                    self.ndch = self.ch
                    self.addCharAtCoords()

            self.screen.move(self.y, self.x)
            self.window.refresh()

    def clearPreviousStatusLines(self):
        for i in range(0, self.width):
            self.screen.addch(prevHeight-1, i, ' ')
            self.screen.addch(prevHeight, i, '')

    def isHigher(self):
        return self.height > self.prevHeight
    
    def hitEnterKey(self, ch = None):
        if ch == None:
            ch = self.ch
        return ch in { curses.KEY_ENTER, 10, 13 }
            
    def addCharAtCoords(self):
        self.window.addch(self.y, self.x, self.ndch)
        self.relayChangeToServer()
        
    def relayChangeToServer(self):
        pass

    def connectToServer(self):
        HOST = '127.0.0.1'
        PORT = '1234'
        NICK = 'nic'
        if not PORT:
            PORT = 1234
        else:
            PORT = int(PORT)
        self.BUFFSIZE = 1024
        ADDR = (HOST, PORT)

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(ADDR)
        receive_thread = Thread(target=self.receiveFromServer)
        receive_thread.start()
        
    def receiveFromServer(self):
        while True:
            try:
                received = self.client_socket.recv(self.BUFFSIZE).decode("utf8")
                print(received)
            except OSError:
                break

    def sendToServer(self, message):
        client_socket.send(bytes(message, "utf8"))
   
    def goDirection(self, directionKey):
        switch={
            curses.KEY_LEFT: self.goLeft(),
            curses.KEY_RIGHT: self.goRight(),
            curses.KEY_DOWN: self.goDown(),
            curses.KEY_UP: self.goUp()
        }
        return switch.get(directionKey)

    def goLeft(self):
        if self.x > 0:
            self.x -= 1
        else:
            self.x = self.drawingWidth
        
    def goRight(self):
        if self.x < self.drawingWidth:
            self.x += 1
        else:
            self.x = 0

    def goDown(self):
        if self.y < self.drawingHeight:
            self.y += 1
        else:
            self.y = 0
        
    def goUp(self):
        if self.y > 0:
            self.y -= 1
        else:
            self.y = self.drawingHeight
    
    def getDimensions(self):
        size = os.get_terminal_size()
        return [size.columns-1, size.lines-1]

    def setBoundaries(self):
        self.prevHeight = self.height
        self.prevWidth = self.width
        
        self.width, self.height = self.getDimensions()
        self.drawingWidth = self.width
        self.drawingHeight = self.height - 2

def main(window):
    p = pASCII()
    p.start(window)
        
if __name__ == '__main__':
    curses.wrapper(main)
