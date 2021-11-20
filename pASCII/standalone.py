from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import curses
import os
import struct

'''
To do:

- Local version
--- don't write 'quit' into the save file

- Network version
-- send chars to server
-- have server display (for now, to confirm that it's working correctly)
-- have it so when another client connects, the charsOnScreen is their starting point that they can add to.

'''

class pASCII(object):

    def start(self, window = None):

        self.window = window        
        self.main()     

    lastTenChars = []
    RESET = 'reset'
    QUIT = 'quit'
    PRINTOUT = 'printout'
    SAVE = 'save'
    DIRECTIONAL_KEYS = { curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT }
    COMMAND_MODE = ':'
    charsOnScreen = {}
    x = 0
    y = 0
    ch = ndch = ord('*')
    
    def main(self):

        self.screen = curses.initscr()

        self.setBoundaries()

        self.charsOnScreen = self.getCharsAtCoordsFromString()
        self.drawSavedCharsToScreen()
        self.drawFooter()
        
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

        while True:
            
            curses.setsyx(self.y, self.x)
            self.prevCh = self.ch
            try:
                self.ch = self.screen.getch()
            except:
                pass

            if self.ch in self.DIRECTIONAL_KEYS:
                if self.ch == curses.KEY_LEFT:
                    self.goLeft()

                elif self.ch == curses.KEY_RIGHT:
                    self.goRight()
                    if self.prevCh not in self.DIRECTIONAL_KEYS:
                        self.goLeft()

                elif self.ch == curses.KEY_DOWN:
                    self.goDown()
                    if self.prevCh not in self.DIRECTIONAL_KEYS and not self.hitEnterKey(self.prevCh):
                        self.goLeft()

                elif self.ch == curses.KEY_UP:
                    self.goUp()
                    if self.prevCh not in self.DIRECTIONAL_KEYS and not self.hitEnterKey(self.prevCh):
                        self.goLeft()

                self.addCharAtPos(self.ndch)
                
            elif self.ch == curses.KEY_RESIZE:
                prevWidth = self.width
                prevHeight = self.height
                self.setBoundaries()

                if self.height > prevHeight:
                    for i in range(0, self.width):
                        self.addCharAtPos(' ', prevHeight-1, i)
                        self.addCharAtPos(' ', prevHeight, i)

            elif self.hitEnterKey(self.ch):

                if self.should(self.RESET):
                    self.reset()

                elif self.should(self.QUIT):
                    self.quit()

                elif self.should(self.SAVE):
                    self.save()
                    
                elif self.should(self.PRINTOUT):
                    self.printout()
                    
                else:
                    self.goDown()
                    if self.prevCh not in self.DIRECTIONAL_KEYS and not self.hitEnterKey(self.prevCh):
                        self.goLeft()

                    self.addCharAtPos(self.ndch)

            else:
                if self.ch >= 0:
                    self.ndch = self.ch
                    self.trackLastTen()

                    self.addCharAtPos()
                    
                    if self.x < self.drawingWidth:
                        self.x += 1
                    else:
                        self.x = 0

            self.drawFooter()

            self.moveToPos()
            self.refreshWindow()

    def refreshWindow(self):
        self.window.refresh()
        
    def printout(self):

        curses.endwin()
        print(self.getString() + '\n')
        self.quit()

    def drawSavedCharsToScreen(self):
    
        for (y, x) in self.charsOnScreen:
            ch = self.charsOnScreen[(y, x)]
            self.addCharAtPos(ch, y, x, False)
            self.y, self.x = (y, x)
        
        self.moveToPos()
         
    def getCharsAtCoordsFromString(self):

        chars = {}
        try:
            with open("pASCII.txt", "r") as f:
                y = x = 0
                for line in f:
                    x = 0
                    for s in line:
                        ch = ord(s)
                        if not self.isNewline(ch) and ch != None and ch != 32:
                            if y <= self.drawingHeight and x <= self.drawingWidth:
                                chars[(y, x)] = ch
                        x+=1
                    y+=1
        except:
            pass

        
        return chars
    
    def getString(self):

        displayString = ""

        for y in range(0, self.drawingHeight):
            for x in range(0, self.drawingWidth):
                if x == 0 and y > 0:
                    displayString += '\n'
                if (y, x) in self.charsOnScreen:
                    try:
                        ch = self.charsOnScreen[(y, x)]
                        s = chr(ch)
                        displayString += s
                    except:
                        pass
                else:
                    displayString += ' '

        displayString+= '\n'
        
        return displayString
                    
    def save(self):
        try:
            out = self.getString()
            f = open("pASCII.txt", "w")
            f.write(out)
            f.close()
        except:
            pass
    
    def quit(self):
        self.save()
        curses.endwin()
        client_socket.sendall(packData(0, 0, 0, 'QUIT'))
#        _quit = True
#        if mode == 'n':
#            client_socket.close()
        exit(0)

    def moveToPos(self, y = None, x = None):
        if y == None:
            y = self.y
        if x == None:
            x = self.x
        self.screen.move(y, x)
        self.y = y
        self.x = x
            
    def addCharAtPos(self, ch = None, y = None, x = None, sendToServer = True):
        if ch == None:
            ch = self.ch
        if y == None:
            y = self.y
        if x == None:
            x = self.x

        self.charsOnScreen[(y, x)] = ch
        self.window.addch(y, x, ch)
        if sendToServer and mode == 'n':
            self.sendToServer()
    
    def getDimensions(self):
        import os
        size = os.get_terminal_size()
        return [size.columns-1, size.lines-1]

    def trackLastTen(self):
        if len(self.lastTenChars) >= 9:
            self.lastTenChars.pop(0)
        try:
            self.lastTenChars.append(chr(self.ch))
        except:
            pass

    def lastTen(self):
        lastTen = ''
        return lastTen.join(self.lastTenChars)

    def drawFooter(self):
        for i in range(0, self.width):
            self.screen.addch(self.height-1, i, '-')
        self.screen.addstr(self.height, 0, "x: " + str(self.x) + "; y: "+ str(self.y) + "; lastTen: " + self.lastTen() + '; last char: ' + chr(self.ndch) + ' (' + str(self.ndch) + ')')

    def setBoundaries(self):
        self.width, self.height = self.getDimensions()
        self.drawingWidth = self.width
        self.drawingHeight = self.height - 1

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
        if self.y  > 0:
            self.y -= 1
        else:
            self.y = self.drawingHeight

    def hitEnterKey(self, ch = None):
        if ch == None:
            ch = self.ch
        return self.isNewline(ch)
    
    def isNewline(self, ch):
        return ch in { curses.KEY_ENTER, 10, 13}
    
    def reset(self):
        self.screen.clear()
        self.screen.refresh()
        self.ndch = ord('*')
        self.x = self.y = 0
        self.charsOnScreen = {}
        return self.x, self.y

    def should(self, action):
        return self.lastTen()[-len(action):None] == action
    
    def sendToServer(self):
        client_socket.sendall(packData(self.y, self.x, self.ndch))
    
p = pASCII()
packer = struct.Struct('I I I S')
client_socket = socket(AF_INET, SOCK_STREAM)
mode = ''
_quit = False

def packData(y, x, ch):
    values = (y, x, ch)
    packed_data = packer.pack(*values)
    return packed_data

def unpackData(data):
    unpacked_data = packer.unpack(data)
    return unpacked_data

def receiveFromServer():
    while True:
        try:
            data = client_socket.recv(packer.size)
            y, x, ch = packer.unpack(data)

            if isClientQuit(data):
                client_socket.close()
                break
            
            p.addCharAtPos(ch, y, x, False)
            p.refreshWindow()
            
        except OSError:
            if _quit:
                client_socket.close()
                break

def isClientQuit(data):
    y, x, ch = packer.unpack(data)
    return y  == -1 and x == -1 and ch == -1

receive_thread = Thread(target=receiveFromServer)

def main(window = None):
#    p = pASCII()
    p.start(window)
    
if __name__ == '__main__':

    while mode == '':
        m = input('What mode? s for standalone, n for networked: ')
        if m in ('s','n'):
            mode = m
    if mode == 'n':

        HOST = input('Server address [default: 127.0.0.1]: ')
        if not HOST:
            HOST = '127.0.0.1'
        
        PORT = input('Port [default: 1234]: ')
        if not PORT:
            PORT = 1234
        else:
            PORT = int(PORT)
        
        NICK = input('What\'s your name? ')
        
        ADDR = (HOST, PORT)
        client_socket.connect(ADDR)
        receive_thread.start()

    curses.wrapper(main)
