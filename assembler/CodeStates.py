'''
Created on 2015-01-06

@author: beewhy
'''


class TextStates(object):
    '''
    A class that holds the states of the text for a textfield
    that has undo and redo actions.
    '''
    _MAXSIZE = 50

    def __init__(self):
        '''
        Constructor
        '''
        self.states = []
        self.pos = -1

    def saveState(self, state):
        if len(self.states) >= 1 and state == self.states[self.pos]:
            return

        self.pos += 1

        if not self.canRedo():
            self.states.append(state)
        else:
            self.states[self.pos] = state
            for i in range(self.pos + 1, len(self.states)):
                self.states.pop(i)

        self.trimToSize()

    def canUndo(self):
        return self.pos > 0

    def canRedo(self):
        return self.pos < len(self.states) - 1

    def undo(self, state):
        if not self.canUndo():
            Exception("Cannot Undo")

        if self.pos == len(self.states) - 1:
            if state != self.states[-1]:
                self.states.append(state)
        else:
            if state != self.states[self.pos]:
                self.states[self.pos + 1] = state
                for i in range(self.pos + 2, len(self.states)):
                    self.states.pop(i)

        self.pos -= 1
        self.trimToSize()

        return self.states[self.pos]

    def redo(self):
        if not self.canRedo():
            Exception("Cannot Redo")

        self.pos += 1
        return self.states[self.pos]

    def trimToSize(self):
        while len(self.states) > self._MAXSIZE:
            self.states.pop(0)
            self.pos -= 1

    def __str__(self):
        retStr = "["
        for i in range(len(self.states)):
            if i == self.pos:
                retStr += "***" + self.states[i] + "***"
            else:
                retStr += self.states[i]
            if i + 1 != len(self.states):
                retStr += ", "
        return retStr + "]"
