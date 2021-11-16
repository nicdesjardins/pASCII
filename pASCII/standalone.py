import curses

'''
To do:

- Local version
-- Save charsOnScreen to a text file
-- On start, open the charsOnScreen file as a starting 
  point so you can leave / come back w/o losing your "work"

- Network version
-- send chars to server
-- have server display (for now, to confirm that it's working correctly)
-- have it so when another client connects, the charsOnScreen is their starting point that they can add to.

'''

class pASCII(object):

    def start(self, window):
        self.window = window
        self.main()

    lastTenChars = []
    RESET = 'reset'
    QUIT = 'quit'
    PRINTOUT = 'printout'
    DIRECTIONAL_KEYS = { curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT }
    charsOnScreen = {}
    x = 0
    y = 0
    ch = ndch = '*'

    def main(self):

        self.screen = curses.initscr()

        #ch = ndch = '*'
        #x = 0
        #y = 0
        curses.setsyx(self.x, self.y)

        self.setBoundaries()

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

                #window.addch(y, x, ndch)
                self.addCharAtPos(self.ndch)
                
            elif self.ch == curses.KEY_RESIZE:
                prevWidth = self.width
                prevHeight = self.height
                self.setBoundaries()

                if self.height > prevHeight:
                    for i in range(0, self.width):
                        #self.screen.addch(prevHeight-1, i, ' ')
                        #self.screen.addch(prevHeight, i, ' ')
                        self.addCharAtPos(' ', prevHeight-1, i)
                        self.addCharAtPos(' ', prevHeight, i)

            elif self.hitEnterKey(self.ch):
                if self.should(self.RESET):
                    self.reset()
                elif self.should(self.QUIT):
                    exit(0)
                elif self.should(self.PRINTOUT):

                    import sys
                    curses.endwin()

                    print(self.charsOnScreen)
                    
                    for y in range(0, self.height):
                        for x in range(0, self.width):
                            if x == 0 and y > 0:
                                sys.stdout.write('\n')
                            if (y, x) in self.charsOnScreen:
                                sys.stdout.write(chr(self.charsOnScreen[(y, x)]))
                            else:
                                sys.stdout.write(' ')

                    print('\nOk, bye')
                                    
                    
                    
                    exit(0)
                else:
                    self.goDown()
                    if self.prevCh not in self.DIRECTIONAL_KEYS and not self.hitEnterKey(self.prevCh):
                        self.goLeft()

                    #self.window.addch(y, x, ndch)
                    self.addCharAtPos(self.ndch)

            else:
                if self.ch >= 0:
                    self.ndch = self.ch
                    self.trackLastTen()

                    #self.window.addch(self.y, self.x, self.ch)
                    self.addCharAtPos()
                    
                    if self.x < self.drawingWidth:
                        self.x += 1
                    else:
                        self.x = 0

            self.drawFooter()

            #self.screen.move(self.y, self.x)
            self.moveToPos()

            self.window.refresh()

    def moveToPos(self):
        self.screen.move(self.y, self.x)
            
    def addCharAtPos(self, ch = None, y = None, x = None):
        if ch == None:
            ch = self.ch
        if y == None:
            y = self.y
        if x == None:
            x = self.x

        self.charsOnScreen[(y, x)] = ch
        self.window.addch(y, x, ch)
    
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
        self.screen.addstr(self.height, 0, "x: " + str(self.x) + "; y: "+ str(self.y) + "; lastTen: " + self.lastTen())

    def setBoundaries(self):
        self.width, self.height = self.getDimensions()
        self.drawingWidth = self.width
        self.drawingHeight = self.height - 2
        #return self.width, self.height, self.drawingWidth, self.drawingHeight

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
        return ch in { curses.KEY_ENTER, 10, 13}

    def reset(self):
        self.screen.clear()
        self.screen.refresh()
        self.ndch = '*'
        self.x = self.y = 0
        self.charsOnScreen = {}
        return self.x, self.y

    def should(self, action):
        return self.lastTen()[-len(action):None] == action

def main(window):
    p = pASCII()
    p.start(window)
    
if __name__ == '__main__':
    curses.wrapper(main)
