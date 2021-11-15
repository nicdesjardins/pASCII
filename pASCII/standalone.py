import curses

lastTenChars = []
RESET = 'reset'
QUIT = 'quit'
PRINTOUT = 'printout'
DIRECTIONAL_KEYS = { curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT }



def main(window):
    
    screen = curses.initscr()
    
    ch = ndch = '*'
    x = 0
    y = 0
    curses.setsyx(x, y)
    
    width, height, drawingWidth, drawingHeight = setBoundaries()

    drawFooter(screen, width, height, x, y)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    
    while True:
        
        curses.setsyx(y, x)
        prevCh = ch
        try:
            ch = screen.getch()
        except:
            pass

        if ch in DIRECTIONAL_KEYS:
            if ch == curses.KEY_LEFT:
                x = goLeft(x, drawingWidth)

            elif ch == curses.KEY_RIGHT:
                x = goRight(x, drawingWidth)
                if prevCh not in DIRECTIONAL_KEYS:
                    x = goLeft(x, drawingWidth)
                
            elif ch == curses.KEY_DOWN:
                y = goDown(y, drawingHeight)
                if prevCh not in DIRECTIONAL_KEYS and not hitEnterKey(prevCh):
                    x = goLeft(x, drawingWidth)

            elif ch == curses.KEY_UP:
                y = goUp(y, drawingHeight)
                if prevCh not in DIRECTIONAL_KEYS and not hitEnterKey(prevCh):
                    x = goLeft(x, drawingWidth)
                
            window.addch(y, x, ndch)
        elif ch == curses.KEY_RESIZE:
            prevWidth = width
            prevHeight = height
            width, height, drawingWidth, drawingHeight = setBoundaries()

            if height > prevHeight:
                for i in range(0,width):
                    screen.addch(prevHeight-1, i, ' ')
                    screen.addch(prevHeight, i, ' ')

        elif hitEnterKey(ch):
            if should(RESET):
                x, y = reset(screen)
            elif should(QUIT):
                exit(0)
            elif should(PRINTOUT):
                screen_bytes = window.instr(0,0)
                curses.endwin()
                print(screen_bytes)
                exit(0)
            else:
                y = goDown(y, drawingHeight)
                if prevCh not in DIRECTIONAL_KEYS and not hitEnterKey(prevCh):
                    x = goLeft(x, drawingWidth)
                window.addch(y, x, ndch)
            
        else:
            if ch >= 0:
                ndch = ch
                trackLastTen(ch)
                window.addch(y, x, ch)

                if x < drawingWidth:
                    x += 1
                else:
                    x = 0

        drawFooter(screen, width, height, x, y)
        screen.move(y, x)
        
        window.refresh()

def getDimensions():
    import os
    size = os.get_terminal_size()
    return [size.columns-1, size.lines-1]

def trackLastTen(ch):
    if len(lastTenChars) >= 9:
        lastTenChars.pop(0)
    try:
        lastTenChars.append(chr(ch))
    except:
        pass

def lastTen():
    lastTen = ''
    return lastTen.join(lastTenChars)

def drawFooter(screen, width, height, x, y):
    for i in range(0, width):
        screen.addch(height-1, i, '-')
    screen.addstr(height, 0, "x: " + str(x) + "; y: "+ str(y) + "; lastTen: " + lastTen())

def setBoundaries():
    width, height = getDimensions()
    drawingWidth = width
    drawingHeight = height - 2
    return width,height,drawingWidth,drawingHeight

def goLeft(x, drawingWidth):
    if x > 0:
        x -= 1
    else:
        x = drawingWidth
    return x

def goRight(x, drawingWidth):
    if x < drawingWidth:
        x += 1
    else:
        x = 0
    return x

def goDown(y, drawingHeight):
    if y < drawingHeight:
        y += 1
    else:
        y = 0
    return y

def goUp(y, drawingHeight):
    if y  > 0:
        y -= 1
    else:
        y = drawingHeight
    return y

def hitEnterKey(ch):
    return ch in { curses.KEY_ENTER, 10, 13}

def reset(screen):
    screen.clear()
    screen.refresh()
    ndch = '*'
    x = y = 0
    return x,y

def should(action):
    return lastTen()[-len(action):None] == action

if __name__ == '__main__':
    curses.wrapper(main)
