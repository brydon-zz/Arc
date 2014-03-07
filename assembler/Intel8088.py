'''
Created on 2014-02-04

@author: beewhy
'''
class Intel8088(object):

    def __init__(self):
        self.restart()

    def restart(self):
        self.registers = {"AX":0, "BX":0, "CX":0, "DX":0, "SP":32760, "BP":32760, "SI":0, "DI":0, "PC":0}

        """Z: zero flag, S: sign flag, O: overflow flag, C: carry flag, A: auxillary flag, P: parity flag, D: direction flag, I: interrupt flag"""
        self.flags = {"Z":False, "S":False, "O":False, "C":False, "A":False, "P":False, "D":False, "I":False}

        self.lookupTable = {}
        self.localVars = {}
        self.stackData = []
        self.DATA = {}
        self.BSS = {}
        self.effectiveBSSandDATALocation = {}
        self.codeBounds = [1, 1]

        self.addressSpace = []
        for i in range(1024):
            self.addressSpace.append(str(0))

        self.jumpLocation = -1

    def eightBitRegister(self, s):
        """ Returns the 8 bit register s, if it exists, otherwise returns 0.
        i.e. self.eightBitRegister('BH') is the top 8 bits of BX """
        try:
            temp = ""

            if s == "AH":
                temp = self.intToHex(self.registers["AX"])[-4:-2]
            elif s == "AL":
                temp = self.intToHex(self.registers["AX"])[-2:]
            elif s == "BH":
                temp = self.intToHex(self.registers["BX"])[-4:-2]
            elif s == "BL":
                temp = self.intToHex(self.registers["BX"])[-2:]
            elif s == "CH":
                temp = self.intToHex(self.registers["CX"])[-4:-2]
            elif s == "CL":
                temp = self.intToHex(self.registers["CX"])[-2:]
            elif s == "DH":
                temp = self.intToHex(self.registers["DX"])[-4:-2]
            elif s == "DL":
                temp = self.intToHex(self.registers["DX"])[-2:]

            return int(temp, 16)

        except ValueError:
            return 0

    def intToHex(self, i):
        """ Converts integers to 0-padded hex. Does twos complement for negative numbers.
        i.e. 17 is returned as 11, 15 is returned as 0F """
        while i > 2 ** 16:
            i -= 2 ** 16
        while i < 0:
            i += 2 ** 16  # 2s complement

        if i > 2 ** 16 or i < 0:
            print "FATAL ERROR"

        hexString = str(hex(i).split("x")[1]).upper()
        return "0"*(2 - len(hexString)) + hexString
    def replaceEscapedSequences(self, string):
        """ Replaces all escaped sequences with their unescaped counterparts """
        return string.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"').replace("\\a", "\a").replace("\\b", "\b").replace("\\f", "\f").replace("\\r", "\r").replace("\\t", "\t").replace("\\v", "\v")

    def escapeSequences(self, string):
        """ Escapes all things that may need escaped. """
        return string.replace("\n", "\\n").replace("\'", "\\'").replace('\"', '\\"').replace("\a", "\\a").replace("\b", "\\b").replace("\f", "\\f").replace("\r", "\\r").replace("\t", "\\t").replace("\v", "\\v")

    def isHex(self, string):
        try:
            int(str(string), 16)
            return True
        except ValueError:
            return False
