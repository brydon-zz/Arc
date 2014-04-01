"""
    Copyright (C) 2014 Brydon Eastman

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. Or by
    email to brydon.eastman@gmail.com.
"""

class Intel8088(object):

    def __init__(self):
        self.restart()

    def restart(self):
        self.registers = {"AX":0, "BX":0, "CX":0, "DX":0, "SP":32760, "BP":32760, "SI":0, "DI":0, "PC":0}

        """Z: zero flag, S: sign flag, O: overflow flag, C: carry flag, A: auxillary flag, P: parity flag, D: direction flag, I: interrupt flag"""
        self.flags = {"Z":False, "S":False, "O":False, "C":False, "A":False, "P":False, "D":False, "I":False}

        self.lookupTable = {}
        self.localVars = {}
        self.lastLine = -1
        self.stackData = []
        self.DATA = {}
        self.BSS = {}
        self.effectiveBSSandDATALocation = {}
        self.codeBounds = [-1, -1]

        self.addressSpace = []
        for i in range(1024):
            self.addressSpace.append(str(0))

        self.jumpLocation = -1

    def getEightBitRegisterNames(self):
        """ Returns a tuple of the names of the eight bit registers. 
            ("AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL") """

        return ("AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL")

    def setJumpLocation(self, l):
        self.jumpLocation = l

    def getLookupTable(self):
        return self.lookupTable

    def getRegisterNames(self):
        """ Returns a tuple of the names of the sixteen bit registers. 
            ("AX", "BX", "CX", "DX", "BP", "SP", "DI", "SI", "PC") """
        return ("AX", "BX", "CX", "DX", "BP", "SP", "DI", "SI", "PC")

    def setRegister(self, reg, to):
        """ Sets the value of the 16 bit register 'reg' to the value 'to'.
        If 'reg' isn't a valid sixteen bit register a TypeError is raised."""
        if reg in self.registers.keys():
            self.registers[reg] = to
        else:
            raise TypeError

    def getRegister(self, reg):
        """ Returns the value of the 16 bit register 'reg'.
        If 'reg' isn't a valid sixteen bit register a TypeError is raised."""
        if reg in self.registers.keys():
            return self.registers[reg]
        else:
            raise TypeError

    def setEightBitRegister(self, reg, to):
        """ Sets the eight bit register 'reg' to the value 'to' while 
        preserving the state of the other associated register.
        If 'reg' isn't a valid eight bit register a TypeError is raised.
        I.E. setting AH will not influence AL. """
        if reg == 'AL':
            self.registers['AX'] = to + self.getEightBitRegister('AH') * 256
        elif reg == 'BL':
            self.registers['BX'] = to + self.getEightBitRegister('BH') * 256
        elif reg == 'CL':
            self.registers['CX'] = to + self.getEightBitRegister('CH') * 256
        elif reg == 'DL':
            self.registers['DX'] = to + self.getEightBitRegister('DH') * 256
        elif reg == "AH":
            self.registers['AX'] = to * 256 + self.getEightBitRegister('AL')
        elif reg == "BH":
            self.registers['BX'] = to * 256 + self.getEightBitRegister('BL')
        elif reg == "CH":
            self.registers['CX'] = to * 256 + self.getEightBitRegister('CL')
        elif reg == "DH":
            self.registers['DX'] = to * 256 + self.getEightBitRegister('DL')
        else:
            raise TypeError

    def getEightBitRegister(self, s):
        """ Returns the 8 bit register s, if it exists, otherwise returns 0.
        If 's' isn't a value eightbit register, then it raises a TypeError
        i.e. self.getEightBitRegister('BH') is the top 8 bits of BX """
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
            else:
                raise TypeError

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

    def getFromMemoryAddress(self, addr, toAddr=-1):
        """ Returns the value located at address 'addr'.
        If the optional toAddr is supplied then it returns a sub-list including the range. """
        if toAddr == -1:
            return self.addressSpace[addr]
        else:
            return self.addressSpace[addr:toAddr]

    def getLocalVar(self, arg):
        return self.localVars[arg]

    def isLocalVar(self, v):
        return v in self.localVars.keys()

    def getLabelFromLookupTable(self, label):
        return self.lookupTable[label]

    def setFlag(self, f, a=1):
        self.flags[f] = a

    def getFlag(self, f):
        return self.flags[f]

    def getStack(self):
        return self.stackData

    def getBSS(self):
        return self.BSS

    def getDATA(self):
        return self.DATA

    def getCodeBounds(self):
        return self.codeBounds

    def setMemoryAddress(self, addr, to):
        """ Sets the value located at address 'addr' to 'to'"""
        self.addressSpace[addr] = to

    def isHex(self, string):
        try:
            if str(string)[-1] == "h":
                int(str(string)[:-1], 16)
                return True
            else:
                int(str(string))
                return True

        except ValueError:
            return False
