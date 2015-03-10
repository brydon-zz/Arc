"""
Emulates the basic components of an Intel8088 including:
    Memory
    Registers
    Stack

It also processes commands from the Intel 8088 instruction set
via the commandinterpreter class.

It also includes some "higher level" tracer functions like:
    Breakpoints
    Local Variables
    Receiving Input text

All registers and stack data types store INTEGERS
The flag data type stores BOOLEANS
The memory data type stores CHARS

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

import commandinterpreter
import time
import os


class Intel8088(object):
    _OVER = 0
    TIMETHRESH = 10
    FILEMODES = ['r', 'w', 'rw']
    BITTYPES = ["Byte", "Word", "Long"]

    def __init__(self):
        self.restart()

    def restart(self):
        self.registers = {"AX": 0, "BX": 0, "CX": 0, "DX": 0, "SP": 1024,
                          "BP": 1024, "SI": 0, "DI": 0, "PC": 0}

        """Z: zero flag, S: sign flag, O: overflow flag, C: carry flag,
        A: auxillary flag, P: parity flag, D: direction flag, I: interrupt"""
        self.flags = {"Z": False, "S": False, "O": False, "C": False,
                      "A": False, "P": False, "D": False, "I": False}

        self.lookupTable = {}
        self.localVars = {}
        self.lastLine = -1
        self.stack = []
        self.openFiles = [0, 0, 0]
        self.breakPoints = []
        self.DATA = {}
        self.BSS = {}
        self.effectiveBSSandDATALocation = {}
        self.codeBounds = [-1, -1]
        self.running = False
        self.ran = False
        self.runningAll = False
        self.waitingForChar = False
        self.inBuffer = ""

        self.addressSpace = [chr(0) for _ in range(1024)]

        self.jumpLocation = -1

        as88 = commandinterpreter.CommandInterpreter(self)

        self.commandArgs = as88.getCommandArgs()
        self.do = as88.getFunctionTable()

    def loadCode(self, lines):

        self.ran = False
        self.runningAll = False
        self.lines = [l.replace("\t", " ") for l in lines]

        errorString = ""

        lineCount = 0

        mode = "head"
        self.restart()

        errorCount = 0

        BSScount = 0

        # This for Loop is gonna go thru the self.lines, set up a nice lookUp
        # table for jumps
        # and record program start and end. and set up some memory stuff.

        """ FIRST PASS """

        for line in self.lines:
            # Looping thru every line
            # we will go thru, at most, 4 modes
            # a "head" mode - where constants are defined
            #      eg _EXIT = 1 etc.
            # a "text" mode (".SECT .TEXT") where the code is located
            #      on the first loop thru we just keep track of where this is,
            #      and set up a jump table
            # a "data" mode (".SECT .DATA") where variables are defined
            #      str: .ASCIZ "%s f"
            # a "bss" mode (".SECT .BSS") where memory chunks are defined
            #      fdes: .SPACE 2
            line = line.strip()

            if "!" in line:
                line = line[:line.find("!")].strip()  # ignore comments

            lineCount += 1

            if mode == "head" and "=" in line:
                line = line.split('=')
                line[0] = line[0].strip()
                line[1] = line[1].strip()

                if self.isLocalVar(line[0]):
                    errorString += "Error on line " + str(lineCount) + \
                                   ", cannot define \''" + line[0] + \
                                   "\' more than once.\n"
                    errorCount += 1
                else:
                    self.setLocalVar(line[0], line[1])

                continue

            if ".SECT" in line.upper():

                # record where the .SECT .TEXT section starts, and ends
                if mode == ".SECT .TEXT":  # ends, we've gone one too far
                    self.setCodeBounds(1, lineCount - 1)
                elif line.upper() == ".SECT .TEXT":  # starts we're 1 too short
                    self.setCodeBounds(0, lineCount)

                mode = line
                continue

            if ":" in line:  # Spliting on a colon, for defining vars, or jumps
                temp = line.split(":")[0]
                if mode == ".SECT .TEXT":
                    # a : in .SECT .TEXT means a jump location
                    # we can define multiple jump locations by digits
                    # but only one by ascii per each ascii name

                    if temp not in self.lookupTable.keys():
                        self.lookupTable[temp] = lineCount
                    else:
                        if temp.isdigit():
                            # If we're defining multiple jump locations for
                            # one digit, keep a list
                            if type(self.lookupTable[temp]) == self.LIST_TYPE:
                                self.lookupTable[temp].append(lineCount)
                            else:
                                self.lookupTable[temp] = [
                                                        self.lookupTable[temp],
                                                        lineCount]
                        else:
                            errorString += "Duplicate entry: \"" + temp + \
                                    "\" on line " + str(lineCount) + \
                                    " and line " + str(self.lookupTable[temp])\
                                     + "\n"

                elif mode == ".SECT .DATA":
                    # info in .SECT .DATA follows the format
                    # str: .ASCIZ "hello world"
                    # where .ASCIZ means an ascii string with a zero at the end
                    # and .ASCII means an ascii string
                    if ":" not in line:
                        trimmed = line.strip()
                        if trimmed.startsWith(".ALIGN "):
                            trimmed = trimmed[7:]
                            try:
                                trimmed = int(trimmed)
                                if BSScount % trimmed != 0:
                                    BSScount += trimmed - (BSScount % trimmed)
                            except:
                                errorString += ".ALIGN expects a single \
integer argument."
                        else:
                            errorString += "I do not understand this line. \
Either declarations or .ALIGN's are expected, and declarations need colons.\
e.g. hw: .ASCIZ \"Hello World\""
                    else:
                        dc = line[line.index(":") + 1:].strip()
                        if dc.startswith(".ASCIZ ") or dc.startswith(".ASCII "):
                            # If we're dealing with a string
                            if line.count("\"") < 2:
                                # each string to be defined should be in quotes
                                # raise error if quotes are messed
                                errorString += "Fatal error on line " + \
                                                str(lineCount) + \
                                                ". Too many quotes.\n"
                            temp2 = self.replaceEscapedSequences(
                                                    line[line.find("\"") + 1:\
                                                         line.rfind("\"")])
                            # otherwise grab the stuff in quotes
                            self.DATA[temp] = [BSScount, BSScount + len(temp2) + \
                                               (dc.startswith(".ASCIZ")) - 1]
                            # and set temp equal to a list of hex vals of each char
                            self.addressSpace[BSScount:BSScount + len(temp2)] = \
                                temp2 + chr(0) * (dc.startswith(".ASCIZ"))

                            BSScount += len(temp2) + (dc.startswith(".ASCIZ"))
                        elif dc.startswith(".BYTE ") or dc.startswith(".WORD ")\
                        or dc.startswith(".LONG "):
                            if dc.startswith(".BYTE"):
                                bTyp = 0
                            elif dc.startswith(".WORD"):
                                bTyp = 1
                            else:
                                bTyp = 2

                            left = dc[6:]  # whats after the .LONG or .WORD
                            try:
                                values = left.split(",")
                                varrays = []
                                for value in values:
                                    if value[-1] == 'h':
                                        value = int(value, 16)
                                    else:
                                        value = int(value)
                                    while value > 2 ** (8 * (2 ** bTyp)) - 1:
                                        value -= 2 ** (8 * (2 ** bTyp)) - 1
                                    varray = []
                                    if value < 2 ** 8 - 1:
                                        varray.append(value)
                                        for _ in range(bTyp):
                                            varray.append(0)
                                    elif value < 2 ** 16 - 1:
                                        hv = hex(value)[2:]
                                        varray.append(int(hv[-2:], 16))
                                        varray.append(int(hv[:-2], 16))
                                        if bTyp == 2:
                                            varray.append(0)
                                    else:
                                        hv = hex(value)[2:]
                                        varray.append(int(hv[-2:], 16))
                                        varray.append(int(hv[-4:-2], 16))
                                        varray.append(int(hv[:-4], 16))
                                    varrays.append(varray)

                                # varrays is a list of lists, each sublist
                                # being a list of bytes.
                                # each sublist represents a new number in the
                                # , possibly unit lengthed, array
                                # time to "flatten" it
                                varrays = [l for sub in varrays for l in sub]

                                BSSend = BSScount + len(varrays)
                                self.DATA[temp] = [BSScount, BSSend]

                                if bTyp != 0:
                                    self.addressSpace[BSScount:BSSend] = \
                                                [chr(v) for v in varrays]
                                else:
                                    self.addressSpace[BSScount:BSSend] = \
                                                            chr(varrays[0])
                                BSScount = BSSend
                            except:
                                errorString += "Fatal error on line " + \
                                        str(lineCount) + \
                                        " Byte declaration should follow:" + \
                                        " [name]: .BYTE [int or hex value]\n"
                        else:
                            errorString += "Fatal error on line " + \
                                            str(lineCount) + \
                                            " I do not recognise the command.\n"
                elif mode == ".SECT .BSS":
                    # info in .SECT .BSS follows the format
                    # fdes: .SPACE 2
                    # Where essentially .BSS just defines memory space

                    temp2 = line.split(".SPACE")[1]
                    # let's find the size of the mem chunk to def
                    self.BSS[temp.strip()] = [BSScount, BSScount + \
                                              int(temp2.strip()) - 1]
                    # and def it in bss as it's start and end pos
                    BSScount += int(temp2.strip())

        if mode == ".SECT .TEXT" and self.codeBounds[1] == -1:
            self.codeBounds[1] = len(self.lines)

        if errorString == "":
            self.setRegister('PC', self.codeBounds[0])
            self.running = True
            errorString = ""
        else:
            errorString += "Your code cannot be run, it contains %d errors" % \
                            errorString.count("\n")

        return errorString

    def stopRunning(self, i=1):
        self.running = False
        self.ran = True
        self.runningAll = False

    def addBreakPoint(self, bp):
        self.breakPoints.append(bp)

    def removeBreakPoint(self, bp):
        self.breakPoints.remove(bp)

    def runAll(self):
        startTime = time.time()
        totalResult = ""
        self.runningAll = True
        while self.running:
            if time.time() - startTime > self.TIMETHRESH:
                break

            if self.getRegister('PC') in self.breakPoints:
                response = self.step()
                if response is not None and response != 0:
                    totalResult += response
                self.runningAll = False
                break
            response = self.step()
            if response is not None and response != 0:
                    totalResult += str(response)
            if self.waitingForChar:
                break

        return totalResult

    def step(self):
        """ This executes a single line of code.
        Parses the command and performs basic error checking
            (are we done the program?
            does the command follow proper syntax (i.e. right arguments)?
            is the command recognised?)
        Before passing it off to the command interpreter class."""
        if self.running:
            try:
                line = self.lines[self.getRegister('PC')].replace("\t", "")
            except IndexError:
                self.stopRunning()
                return
            # clear out tabs

            if "!" in line:  # exclamations mean comments
                line = line[:line.find("!")].strip()  # ignore comments

            if ":" in line:  # colons mean labels, we dealt with those already.
                line = line[line.find(":") + 1:].strip()  # ignore jump points

            command = [self.replaceEscapedSequences(x.strip()) for x in \
                       line.replace(" ", ",").split(",")]

            for x in range(command.count("")):
                command.remove("")

            if command is None or command == []:
                self.lastLine = self.getRegister('PC')
                self.setRegister('PC', self.getRegister('PC') + 1)
                return  # skip the empty lines

            if command[0] not in self.commandArgs.keys():
                self.stopRunning(-1)
                return "Fatal error. " + command[0] + " not recognised."

            if self.commandArgs[command[0]] != -1 and \
               len(command) - 1 != self.commandArgs[command[0]]:
                self.stopRunning(-1)
                return "Invalid number of arguments on line " + \
                    str(self.getRegister('PC')) + ". " + command[0] + \
                    " expects " + str(self.commandArgs[command[0]]) + \
                    " argument" + "s" * (self.commandArgs[command[0]] > 1) + \
                    " and " + str(len(command) - 1) + \
                    (" were " if len(command) - 1 > 1 else " was ") + "given."

            if command[0] in self.do.keys():
                try:
                    response = self.do[command[0]](command,
                                                   self.getRegister('PC'))
                except:
                    response = "Fatal error occurred on line " + \
                                str(self.getRegister('PC'))
            else:
                self.stopRunning(-1)
                return "Fatal error. " + command[0] + " not recognised."

            if self.jumpLocation != -1:
                self.lastLine = self.getRegister('PC')
                self.setRegister('PC', self.jumpLocation)
                self.jumpLocation = -1
            else:
                self.lastLine = self.getRegister('PC')
                self.setRegister('PC', self.getRegister('PC') + 1)

            if self.getRegister('PC') >= self.codeBounds[1]:
                self.stopRunning()
                return self._OVER

            return response

    def requestsGetChar(self):
        """ The Machine needs to interface with the
        gui to get input characters. This function
        is called by the gui to check if the machine
        is waiting for a character """

        return self.waitingForChar

    def getChar(self):
        """ This function is activated by the system trap interface for
            char requests.
            If there is no character loaded into the input buffer then we
            Simply ensure our getchar flag is loaded.
            Otherwise we load the ASCII value of the current char in the
            input buffer into the AX register and "pop" the char out of the
            buffer. """
        if self.inBuffer == "":
            self.waitingForChar = True
        else:
            self.setRegister('AX', ord(self.inBuffer[0]))
            self.inBuffer = self.inBuffer[1:]

    def respondGetChar(self, string):
        """ When we have received a string back from the GUI element to be
            loaded in with the getChar() function, we merely load the string
            into the buffer and let the getChar function work. We turn off
            the waitingForChar flag because we are no longer waiting for a char
            """
        self.waitingForChar = False
        self.inBuffer = string
        self.getChar()

    def getFunctionDescriptions(self, function):
        """ Returns the docstrings of the instruction set functions. """
        return self.do[function].__doc__

    def getFunctions(self):
        """ Returns a list of the instruction set functions """
        return self.do.keys()

    def getEightBitRegisterNames(self):
        """ Returns a tuple of the names of the eight bit registers.
            ("AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL") """

        return ("AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL")

    def setJumpLocation(self, l):
        """ Sets the location to next jump PC to """
        self.jumpLocation = l

    def getLookupTable(self):
        """ Returns the jump table """
        return self.lookupTable

    def getStack(self):
        """ returns the data from the stack """
        return self.stack

    def getStackOffsetBy(self, offset):
        off = (-int(offset) + (1022 - self.getRegister('BP'))) / 2
        if off < 0:
            off = 0
        elif off >= len(self.stack):
            off = len(self.stack) - 1

        return self.stack[off]

    def stackChange(self, offset, to):
        off = (-int(offset) + (1022 - self.getRegister('BP'))) / 2
        if off < 0:
            off = 0
        elif off >= len(self.stack):
            off = len(self.stack) - 1

        self.stack[off] = to

    def insertInLookupTable(self, label, value):
        self.lookupTable[label] = value

    def isLabelInLookupTable(self, label):
        return label in self.lookupTable

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

    def intToHex(self, i, zerosToPad=2):
        """ Converts integers to 0-padded hex. Does twos complement for
        negative numbers.
        i.e. 17 is returned as 11, 15 is returned as 0F """
        while i > 2 ** 16:
            i -= 2 ** 16
        while i < 0:
            i += 2 ** 16  # 2s complement

        if i > 2 ** 16 or i < 0:
            print "FATAL ERROR"

        hexString = str(hex(i).split("x")[1]).upper()
        return "0" * (zerosToPad - len(hexString)) + hexString

    def replaceEscapedSequences(self, string):
        """ Replaces all escaped sequences with their counterparts """
        return string.replace("\\n", "\n").replace("\\'", "'")\
            .replace('\\"', '"').replace("\\a", "\a").replace("\\b", "\b")\
            .replace("\\f", "\f").replace("\\r", "\r").replace("\\t", "\t")\
            .replace("\\v", "\v")

    def escapeSequences(self, string):
        """ Escapes all things that may need escaped. """
        return string.replace("\n", "\\n").replace("\'", "\\'").\
            replace('\"', '\\"').replace("\a", "\\a").replace("\b", "\\b")\
            .replace("\f", "\\f").replace("\r", "\\r").replace("\t", "\\t")\
            .replace("\v", "\\v")

    def getFromMemoryAddress(self, addr, toAddr=-1):
        """ Returns the value located at address 'addr'.
        If the optional toAddr is supplied then it returns a sub-list
        including the range. """
        if toAddr == -1:
            return self.addressSpace[addr]
        else:
            return self.addressSpace[addr:toAddr]

    def getLocalVar(self, arg):
        return self.localVars[arg]

    def setLocalVar(self, key, val):
        self.localVars[key] = val

    def setCodeBounds(self, i, val):
        self.codeBounds[i] = val

    def getLastLine(self):
        return self.lastLine

    def setLastLine(self, l):
        self.lastLine = l

    def isLocalVar(self, v):
        return v in self.localVars.keys()

    def getLabelFromLookupTable(self, label):
        return self.lookupTable[label]

    def addToStack(self, value):
        self.stack.append(value)
        self.registers['SP'] -= 2
        hexval = self.intToHex(value, 4)
        try:
            self.addressSpace[self.registers['SP']] = \
                                        chr(int(hexval[-4:-2], 16))
            self.addressSpace[self.registers['SP'] + 1] = \
                                        chr(int(hexval[-2:], 16))
        except Exception as E:
            print E

    def popFromStack(self):
        self.registers['SP'] += 2
        return self.stack.pop()

    def stackSize(self):
        return len(self.stack)

    def peekOnStack(self, i=1):
        return self.stack[-i]

    def getZeroTerminatedMemStringAt(self, start):
        try:
            nextZero = self.addressSpace.index(chr(0), start)
        except:
            nextZero = len(self.addressSpace)
        a = self.addressSpace[start:nextZero]
        return "".join(a)

    def setFlag(self, f, a=1):
        self.flags[f] = a

    def getFlag(self, f):
        return self.flags[f]

    def getBSSKeys(self):
        return tuple(self.BSS.keys())

    def getDATAKeys(self):
        return tuple(self.DATA.keys())

    def inBSSKeys(self, key):
        return key in self.BSS

    def inDATAKeys(self, key):
        return key in self.DATA

    def getFromBSSorDATA(self, key, index=None):
        if key in self.BSS.keys():
            return self.getFromBSS(key, index)
        elif key in self.DATA.keys():
            return self.getFromDATA(key, index)

    def getFromBSS(self, key, index=None):
        if index is None:
            return self.BSS[key]
        else:
            return self.BSS[key][index]

    def getFromDATA(self, key, index=None):
        if index is None:
            return self.DATA[key]
        else:
            return self.DATA[key][index]

    def getCodeBounds(self):
        return tuple(self.codeBounds)

    def setMemoryAddress(self, addr, to):
        """ Sets the value located at address 'addr' to 'to'"""
        self.addressSpace[addr] = str(to)

    def insertStringAtMemLocation(self, string, addr):
        if addr + len(string) < len(self.addressSpace):
            self.addressSpace[addr:addr + len(string)] = string

    def insertIntAtMemLocation(self, i, addr):
        try:
            i = int(i)
        except:
            return -1

        while i > 256:
            i -= 256

        self.setMemoryAddress(addr, chr(i))

    def insertHexAtMemLocation(self, hexStr, addr):
        if hexStr[-1] == "h":
            hexStr = hexStr[:-1]
        try:
            hexStr = int(hexStr, 16)
        except:
            return -1

        self.insertIntAtMemLocation(hexStr, addr)

    def insertOctAtMemLocation(self, string, addr):
        try:
            string = int(string, 8)
        except:
            return -1

        self.insertIntAtMemLocation(string, addr)

    def insertBinAtMemLocation(self, string, addr):
        try:
            string = int(string, 2)
        except:
            return -1

        self.insertIntAtMemLocation(string, addr)

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

    def isRunning(self):
        return self.running

    def isRunningAll(self):
        return self.runningAll

    def hasRun(self):
        return self.ran

    def isBreakPoint(self, bp):
        return bp in self.breakPoints

    def openFile(self, fname, mode):
        try:
            self.openFiles.append(open(fname, self.FILEMODES[mode]))
        except:
            return -1
        return len(self.openFiles) - 1

    def createFile(self, fname, mode):
        if os.path.isfile(fname):
            os.remove(fname)
        return self.openFile(fname, mode)

    def closeFile(self, fd):
        try:
            self.openFiles[fd].close()
            self.openFiles.pop()
            return True
        except:
            return False

    def read(self, fd, buf, nbytes):
        try:
            response = self.openFiles[fd].read(nbytes)
            size = len(response)
            self.addressSpace[buf:size + buf] = response
            return size
        except:
            return 0

    def write(self, fd, buf, nbytes):
        try:
            toWrite = "".join(self.getFromMemoryAddress(buf, buf + nbytes))
            self.openFiles[fd].write(toWrite)
            return len(toWrite)
        except:
            return 0

    def lseek(self, fd, num):
        try:
            self.openFiles[fd].seek(num, 1)
            return
        except:
            return -1
