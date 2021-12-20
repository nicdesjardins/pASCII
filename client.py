from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import curses
import os
import struct
from packet import pASCII_packet as Packet
from constants import Constants, Commands

'''
To do:

- Local version
-- Don't write 'quit' into the save file:
--- Maybe we need an interface that doesn't draw to screen where we can add commands
--- > a COMMAND palette

- Network version
-- Add a curses interface to the server so that you can enter commands, like? well for one, quit.

'''

class Position(object):
    x = 0
    y = 0
    
class pASCII(object):

    Constants = Constants()
    Position = Position()

    
    def start(self, window = None):
        self.window = window        
        self.main()     

    lastTenChars = []
    charsOnScreen = {}

    ch = ndch = ord('*')
    WHITE_ON_BLUE = 1
    BLUE_ON_WHITE = 2
    def main(self):

        self.screen = curses.initscr()
        curses.init_pair(self.WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(self.BLUE_ON_WHITE, curses.COLOR_BLUE, curses.COLOR_WHITE)

        self.screen.bkgd(' ', curses.color_pair(self.WHITE_ON_BLUE))
        
        self.setBoundaries()

        if mode != 'n':
            self.charsOnScreen = self.getCharsAtCoordsFromString()
        
        self.drawSavedCharsToScreen()
        self.drawFooter()
        
        curses.start_color()
       # curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

        if mode == 'n':
            self.getCharsInSpace()
        
        while True:
            
            curses.setsyx(self.Position.y, self.Position.x)
            self.prevCh = self.ch
            try:
                self.ch = self.screen.getch()
                print(str(ord(self.ch)))
            except:
                pass

            if self.ch in self.Constants.DIRECTIONAL_KEYS:
                if self.ch == curses.KEY_LEFT:
                    self.goLeft()

                elif self.ch == curses.KEY_RIGHT:
                    self.goRight()
                    if self.prevCh not in self.Constants.DIRECTIONAL_KEYS:
                        self.goLeft()

                elif self.ch == curses.KEY_DOWN:
                    self.goDown()
                    if self.prevCh not in self.Constants.DIRECTIONAL_KEYS and not self.hitEnterKey(self.prevCh):
                        self.goLeft()

                elif self.ch == curses.KEY_UP:
                    self.goUp()
                    if self.prevCh not in self.Constants.DIRECTIONAL_KEYS and not self.hitEnterKey(self.prevCh):
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
            #elif self.ch in (curses.KEY_END, curses.KEY_EXIT):
            elif self.ch in (curses.KEY_CANCEL,):
                print('hit escape key')
            elif self.hitEnterKey(self.ch):

                if self.should(self.Constants.Commands.RESET):
                    if mode != 'n':
                        self.reset()

                elif self.should(self.Constants.Commands.QUIT):
                    self.quit()

                elif self.should(self.Constants.Commands.SAVE):
                    self.save()
                    
                elif self.should(self.Constants.Commands.PRINTOUT):
                    self.printout()
                    
                elif self.should(self.Constants.Commands.CHARSINSPACE):
#                    print("should get chars in space")
                    self.getCharsInSpace()
                    
                else:
                    self.goDown()
                    if self.prevCh not in self.Constants.DIRECTIONAL_KEYS and not self.hitEnterKey(self.prevCh):
                        self.goLeft()

                    self.addCharAtPos(self.ndch)

            else:
                if self.ch >= 0:
                    self.ndch = self.ch
                    self.trackLastTen()

                    self.addCharAtPos()
                    
                    if self.Position.x < self.drawingWidth:
                        self.Position.x += 1
                    else:
                        self.Position.x = 0

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
            self.Position.y, self.Position.x = (y, x)
        
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

    def moveToPos(self, y = None, x = None):
        if y == None:
            y = self.Position.y
        if x == None:
            x = self.Position.x
        self.screen.move(y, x)
        self.Position.y = y
        self.Position.x = x
   
    def getDimensions(self):
        import os
        size = os.get_terminal_size()
        return [size.columns-1, size.lines-1]

    def trackLastTen(self):
        if len(self.lastTenChars) >= 16:
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
        self.screen.addstr(self.height, 0, "x: " + str(self.Position.x) + "; y: "+ str(self.Position.y) + "; lastTen: " + self.lastTen() + '; last char: ' + chr(self.ndch) + ' (' + str(self.ndch) + ')')

    def setBoundaries(self):
        self.width, self.height = self.getDimensions()
        self.drawingWidth = self.width
        self.drawingHeight = self.height - 1

    def goLeft(self):
        if self.Position.x > 0:
            self.Position.x -= 1
        else:
            self.Position.x = self.drawingWidth

    def goRight(self):
        if self.Position.x < self.drawingWidth:
            self.Position.x += 1
        else:
            self.Position.x = 0

    def goDown(self):
        if self.Position.y < self.drawingHeight:
            self.Position.y += 1
        else:
            self.Position.y = 0

    def goUp(self):
        if self.Position.y  > 0:
            self.Position.y -= 1
        else:
            self.Position.y = self.drawingHeight

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
        self.Position.x = self.Position.y = 0
        self.charsOnScreen = {}
        return self.Position.x, self.Position.y

    def should(self, action):
        return self.lastTen()[-len(action):None] == action

    def quit(self):
        if mode != 'n':
            self.save()

        curses.endwin()

        if mode == 'n':
            packet = Packet()
            packet.msg = self.Constants.Commands.QUIT
            client_socket.sendall(packet.pack())

        exit(0)            

    def addCharAtPos(self, ch = None, y = None, x = None, sendToServer = True):
        if ch == None:
            ch = self.ch
        if y == None:
            y = self.Position.y
        if x == None:
            x = self.Position.x

        if x < self.drawingWidth and y < self.drawingHeight:
            self.charsOnScreen[(y, x)] = ch
            self.window.addch(y, x, ch)
            
        if sendToServer and mode == 'n':
            self.sendToServer()
    
    def sendToServer(self):
        client_socket.sendall(packData(self.Position.y, self.Position.x, self.ndch))

    def getCharsInSpace(self):
        if mode == 'n':
             packet = Packet()
             packet.msg = self.Constants.Commands.CHARSINSPACE
             client_socket.sendall(packet.pack())
    
p = pASCII()
client_socket = socket(AF_INET, SOCK_STREAM)
mode = ''

def packData(y, x, ch):
    packet = Packet()
    packet.y = y
    packet.x = x
    packet.ch = ch
    return packet.pack()

def unpackData(data):
    packet = Packet()
    return packet.unpack(data)

def receiveFromServer():
    while True:
        try:
            packet = Packet()
            data = client_socket.recv(packet.size)
            packet.unpack(data)
            y, x, ch = (packet.y, packet.x, packet.ch)

            if isClientQuit(packet):
                client_socket.close()
                return
            else:
                p.addCharAtPos(ch, y, x, False)
                p.refreshWindow()
            
        except OSError:
            if _quit:
                client_socket.close()
                break

def isClientQuit(packet):
    return packet.msg == p.Constants.Commands.QUIT

receive_thread = Thread(target=receiveFromServer)

def main(window = None):
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
