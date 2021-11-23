import curses

class Commands(object):

    RESET = 'reset'
    QUIT = 'quit'
    PRINTOUT = 'printout'
    SAVE = 'save'

    def __str__(self):
        return str((self.RESET, self.QUIT, self.PRINTOUT, self.SAVE))
    
class Constants(object):

#    Commands = Commands()
    DIRECTIONAL_KEYS = { curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT }    
    COMMAND_MODE = ':'

    def __init__(self):
        self.Commands = Commands()
        
    def __str__(self):
        return str((str(self.Commands), self.DIRECTIONAL_KEYS, self.COMMAND_MODE))

