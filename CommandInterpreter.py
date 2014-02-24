'''
Created on 2013-10-20

@author: Brydon
'''

class CommandInterpreter():

    def __init__(self, gui, assembler):
        """ Link's this module with the self.assembler instance """
        self.sysCodes = {"_EXIT":1, "_PRINTF":127, "_GETCHAR":117, "_SSCANF":125, "_READ":3, "_OPEN":5, "_CLOSE":6}
        self.assembler = assembler
        self.gui = gui
        self.LIST_TYPE = type([1, 1])

    def getCommandArgs(self):
        """ A dict whose keys are commands and their values are the # of arguments they expect """
        return {"AAA":0,  # Ascii adjust AL after addition
                "AAD":0,  # Ascii adjust AX before division
                "AAM":0,  # Ascii adjust AX after multiplication
                "AAS":0,  # Ascii adjust AL after subtraction
                "ADC":2,  # Add with carry
                "ADD":2,  # Add
                "AND":2,  # Logical and
                "CALL":1,  # Call procedure
                "CBW":0,  # Convert byte to word
                "CLC":0,  # Clear carry flag
                "CLD":0,  # Clear direction flag
                "CLI":0,  # Clear interrupt flag
                "CMC":0,  # Coplement carry flag
                "CMP":2,  # Compare operands
                "CMPB":2,
                "CMPSB":-1,  # Compare bytes in memory
                "CMPSW":-1,  # Compare words in memory
                "CWD":0,  # Convert word to doubleword
                "DAA":0,  # Decimal adjust AL after addition
                "DAS":0,  # Decimal adjust AL after subtraction
                "DEC":1,  # Decrement by 1
                "DIV":2,  # Unsigned divide
                "IDIV":1,  # Signed divide
                "IMUL":1,  # Signed multiply
                "INC":1,  # Increment by 1
                "JA":1,  # Jump if above
                "JAE":1,  # Jump if above or equal
                "JB":1,  # Jump if below
                "JBE":1,  # Jump if below or equal
                "JC":1,  # Jump if carry
                "JE":1,  # Jump if equal
                "JG":1,  # Jump if greater than
                "JGE":1,  # Jump if greater than or equal
                "JL":1,  # Jump if less than
                "JLE":1,  # Jump if less than or equal
                "JNA":1,  # Jump if not above
                "JNAE":1,  # Jump if not above or equal
                "JNB":1,  # Jump if not below
                "JNBE":1,  # Jump if not below or equal
                "JNC":1,  # Jump if not carry
                "JNE":1,  # Jump if not equal
                "JNG":1,  # Jump if not greater than
                "JNGE":1,  # Jump if not greater than or equal
                "JNL":1,  # Jump if not less than
                "JNLE":1,  # Jump if not less than or equal
                "JNO":1,  # Jump if not overflow
                "JNP":1,  # Jump if not ???
                "JNS":1,  # Jump if not ???
                "JNZ":1,  # Jump if noscreet zero
                "JO":1,  # Jump if overflow
                "JP":1,  # Jump if ???
                "JPE":1,  # Jump if ???
                "JPO":1,  # Jump if ???
                "JS":1,  # Jump if ???
                "JZ":1,  # Jump if zero
                "JCXZ":1,  # Jump if CX is zero
                "JMP":1,  # Jump
                "LAHF":0,  # Load flags into AH register
                "LDS":2,  # Load pointer using DS
                "LEA":2,  # Load effective address
                "LES":2,  # Load ES with pointer
                "LODSB":0,  # Load string byte
                "LODSW":0,  # Load string word
                "LOOP":1,  # Loop control
                "LOOPE":1,  # Loop if equal
                "LOOPNE":1,  # Loop if not equal
                "LOOPNZ":1,  # Loop if not zero
                "LOOPZ":1,  # Loop if zero
                "MOV":2,  # Move
                "MOVSB":0,  # Move byte from string to string
                "MOVSW":0,  # Move word from string to string
                "MUL":2,  # Unsigned Multiply
                "NEG":1,  # Two's complement negation
                "NOP":0,  # No Operation.
                "NOT":1,  # Negate the opearand, logical NOT
                "OR":2,  # Logical OR
                "POP":1,  # Pop data from stack
                "POPF":0,  # Pop data from flags register
                "PUSH":1,  # Push data to stacscreek
                "PUSHF":0,  # Push flags onto stack
                "RCL":2,  # Rotate left with carry
                "RCR":2,  # Rotate right with carry
                # "REP":-1,  # Repeat MOVS/STOS/CMPS/LODS/SCAS
                # "REPE":-1,  # Repeat if equal
                # "REPNE":-1,  # Repeat if not equal
                # "REPNZ":-1,  # Repeat if not zero
                # "REPZ":-1,  # Repeat if zero
                "RET":0,  # Return from procedure
                "ROL":2,  # Rotate left
                "ROR":2,  # Rotate right
                "SAHF":0,  # Store AH into flags
                "SAL":2,  # Shift Arithmetically Left
                "SAR":2,  # Shift Arithmetically Right
                "SBB":2,  # Subtraction with borrow
                "SCASB":0,  # Compare byte string
                "SCASW":0,  # Compare word string
                "SHL":2,  # unsigned Shift left
                "SHR":2,  # unsigned Shift right
                "STC":0,  # Set carry flag
                "STD":0,  # Set direction flag
                "STI":0,  # Set interrupt flag
                "STOSB":0,  # Store byte in string
                "STOSW":0,  # Store word in string
                "SUB":2,  # Subtraction
                "SYS":0,  # System trap
                "TEST":2,  # Logical compare (AND)
                "XCHG":2,  # Exchange data
                "XOR":2  # Logical XOR
                }

    def getFunctionTable(self):
        """ The jump table - the keys are commands and values are the functions that need called, i use anonymous lambda fnxns for argument passing """
        """
                "JNA":1,  # Jump if not above
                "JNAE":1,  # Jump if not above or equal
                "JNB":1,  # Jump if not below
                "JNBE":1,  # Jump if not below or equal
                """
        return {
                "ADD":lambda x, i: self.add(x, i),
                "PUSH":lambda x, i: self.push(x, i),
                "PUSHF":lambda x, i: self.pushf(x, i),
                "JMP":lambda x, i: self.jmp(x, i),
                "JC":lambda x, i: self.jf(x, i, self.assembler.flags['C'] == 1),
                "JCXZ":lambda x, i: self.jf(x, i, self.assembler.registers['CX'] == 0),
                "JE":lambda x, i: self.jf(x, i, self.assembler.flags['Z'] == 1),
                "JG":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 and self.assembler.flags['Z'] == 0),
                "JGE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 or self.assembler.flags['Z'] == 1),
                "JL":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 and self.assembler.flags['Z'] == 0),
                "JLE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 or self.assembler.flags['Z'] == 1),
                "JNC":lambda x, i: self.jf(x, i, self.assembler.flags['C'] == 0),
                "JNE":lambda x, i: self.jf(x, i, self.assembler.flags['Z'] == 0),
                "JNG":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 or self.assembler.flags['Z'] == 1),
                "JNGE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 and self.assembler.flags['Z'] == 0),
                "JNLE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 and self.assembler.flags['Z'] == 0),
                "JNL":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 or self.assembler.flags['Z'] == 1),
                "JNO":lambda x, i: self.jf(x, i, self.assembler.flags["O"] == 0),
                "JNP":lambda x, i: self.jf(x, i, self.assembler.flags['P'] == 0),
                "JNS":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0),
                "JNZ":lambda x, i: self.jf(x, i, self.assembler.flags['Z'] == 0),
                "JO":lambda x, i: self.jf(x, i, self.assembler.flags['O'] == 1),
                "JP":lambda x, i: self.jf(x, i, self.assembler.flags['P'] == 1),
                "JPE":lambda x, i: self.jf(x, i, self.assembler.flags['P'] == 1 or self.assembler.flags['Z'] == 1),
                "JPO":lambda x, i: self.jf(x, i, self.assembler.flags['P'] == 1 or self.assembler.flags['O'] == 1),
                "JS":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1),
                "JZ":lambda x, i: self.jf(x, i, self.assembler.flags['Z'] == 1),
                "LOOP":lambda x, i: self.loop(x, i),
                "LOOPE":lambda x, i: self.loop(x, i, self.assembler.flags["Z"]),
                "LOOPNE":lambda x, i: self.loop(x, i, not self.assembler.flags["Z"]),
                "LOOPNZ":lambda x, i: self.loop(x, i, not self.assembler.flags["Z"]),
                "LOOPZ":lambda x, i: self.loop(x, i, self.assembler.flags["Z"]),
                "MOV":lambda x, i: self.mov(x, i),
                "NOP":lambda x, i: 1 + 1,  # best instruction
                "SYS":lambda x, i: self.sys(x, i),
                "CLC":lambda x, i: self.clc(x, i),
                "STC":lambda x, i: self.stc(x, i),
                "POP":lambda x, i: self.pop(x, i),
                "STOSB":lambda x, i: self.stosb(x, i),
                "CMPB":lambda x, i: self.cmpb(x, i),
                "INC":lambda x, i: self.incdec(x, i, 1),
                "DEC":lambda x, i: self.incdec(x, i, -1),
                "XCHG":lambda x, i: self.xchg(x, i)
                }

    def add(self, command, i):
        """ add x,y translates to x = x + y
        where x is a register or mem address, y is a number, localvar, mem address, or register. """
        if command[1] == "SP" and command[2].isdigit():  # TODO: REPLACE THIS
            for j in range(int(command[2]) / 2):
                if len(self.assembler.stackData) > 0:
                    self.assembler.stackData.pop()
                    self.gui.updateStack()
        if command[1].isdigit():
            self.gui.outPut("Error on line " + str(i) + ". Add cannot have a numerical first argument.")
            self.gui.stopRunning(-1)
            return
        """ To save on code space, y will serve as "second guy" """
        if command[2].strip("abcdef").isdigit():  # y is a digit
            y = int(command[2], 16)
        elif command[2] in self.assembler.localVars.keys():  # y is a local var
            y = int(self.assembler.localVars[command[2]])
        elif command[2] in self.assembler.registers.keys():  # y is a register
            y = self.assembler.registers[command[2]]
        elif command[2] in self.assembler.DATA.keys():  # y is a mem address from DATA section
            y = self.assembler.addresSpace[self.assembler.DATA[command[2]][0]]
        elif command[2] in self.assembler.BSS.keys():  # y is a mem address from BSS section
            y = self.assembler.addresSpace[self.assembler.BSS[command[2]][0]]

        if command[1] in self.assembler.registers.keys():  # x is a register
            self.assembler.registers[command[1]] += y
            result = self.assembler.registers[command[1]]
        elif command[1] in self.assembler.DATA.keys():  # x is a data location
            self.assembler.addresSpace[self.assembler.DATA[command[1]][0]] += y
            result = self.assembler.addresSpace[self.assembler.DATA[command[1]][0]]
        elif command[1] in self.assembler.BSS.keys():  # x is a BSS location
            self.assembler.addresSpace[self.assembler.BSS[command[1]][0]] += y
            result = self.assembler.addresSpace[self.assembler.BSS[command[1]][0]]

        if result == 0:
            self.assembler.flags['Z'] = 1
        elif result < 0:
            self.assembler.flags['S'] = 1

    def clc(self, command, i):
        """ set the carry flag to false """
        self.assembler.flags["C"] = False

    def cld(self, command, i):
        """ set the direction flag to false """
        self.assembler.flags['D'] = False

    def cli(self, commmand, i):
        """ set the interrupt flag to false """
        self.assembler.flags['I'] = False

    def cmc(self, command, i):
        """ Complements the carry flag, toggling it """
        self.assembler.flags['C'] = not self.assembler.flags["C"]

    def cmpb(self, command, i):
        """ cmpb x,y where x and y are bytes, if equal set the zero flag accordingly """
        a = command[1:3]
        b = []
        for x in a:
            if x in ['AH', 'AL', 'BH', 'BL', 'CH', 'CL', 'DH', 'DL']:
                x = self.assembler.eightBitRegister(x)
            elif x in ['AX', 'BX', 'CX', 'DX']:
                self.gui.outPut("Illegal argument for cmpb on line %d. %s is a 16 bit register, perhaps you meant one of the 8 bit %s or %s registers?" % (i, x, x[0] + "H", x[0] + "L"))
                self.gui.stopRunning(-1)
                return
            elif type(x) == type(""):
                x = self.assembler.replaceEscapedSequences(x.rstrip("'\"").lstrip("'\""))

                if len(x) != 1:
                    self.gui.outPut("Illegal argument %s for cmpb on line %d. cmpb expects all strings to be ONE byte in length." % (x, i))
                    self.gui.stopRunning(-1)
                    return
                else:
                    try:
                        x = int(x)
                    except ValueError:
                        x = ord(x)
            elif type(x) != type(1):
                self.assembler.out("Illegal argument %s for cmpb on line %d. cmpb expects an argument to be a one byte register (ie: AH, AL, etc.), an integer, or a one byte string (ie: \"L\", etc.). Instead %s was given." % (x, i, x))
            b.append(x)

        self.assembler.flags["Z"] = b[0] == b[1]

    def incdec(self, command, i, p):
        """ A function for incrementing or decermenting a register.  p is the polarity (-1 for dec, 1 for inc) """
        if command[1] in self.assembler.registers.keys():
            self.assembler.registers[command[1]] += p;
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.addressSpace[self.assembler.BSS[command[1]][0]] += p
        elif command[1] in self.assembler.DATA.keys():
            self.assembler.addressSpace[self.assembler.DATA[command[1]][0]] += p
        else:
            self.gui.outPut("Invalid " + command[0] + " on line " + str(i) + ". " + command[0] + " expects its argument to be either a register or memory address.")

    def jf(self, command, i, flag):
        """ jmp if the flag is true, used for jo, jg, jge, etc. """
        if flag:
            self.jmp(command, i)

    def jmp(self, command, i, referer="jmp"):
        """ jmp x jumps to position x in the program """
        if command[1] in self.assembler.lookupTable.keys():
            if type(self.assembler.lookupTable[command[1]]) == self.LIST_TYPE:
                # Jumps where many are declared, gotta jump up or down, bit complicated. ie, jmp 1f
                1 + 1
            else:
                self.assembler.jumpLocation = self.assembler.lookupTable[command[1]]
        else:
            self.gui.outPut("Error on line " + str(i) + ". The label " + command[1] + " is not defined for " + referer + "-ing to.")

    def loop(self, command, i, flag=True):
        """ Decrements CX and jumps to a label if CX is greater than zero and flag is true. """
        self.assembler.registers["CX"] -= 1
        if flag and self.assembler.registers["CX"] > 0:
            self.jmp(command, i, "loop")

    def mov(self, command, i):
        """ Mov A,B  evaluates as A=B where A is a register or memory address and B is a memory,
            register address, local variable, or number. """

        if command[2].strip("abcdef").isdigit():  # B is digit
            b = int(command[2], 16)
        elif command[2] in self.assembler.localVars.keys():  # B is local var
            b = int(self.assembler.localVars[command[2]])
        elif command[2] in self.assembler.BSS.keys():  # B is BSS mem address
            b = int(self.assembler.BSS[command[2]][0])
        elif command[2] in self.assembler.DATA.keys():  # B is DATA mem address
            b = int(self.assembler.DATA[command[2]][0])

        if command[1] in self.assembler.registers.keys():
            self.assembler.registers[command[1]] = b
        elif command[1] in self.assembler.DATA.keys():
            self.assembler.addressSpace[self.assembler.DATA[command[1]][0]] = b
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.addressSpace[self.assembler.BSS[command[1]][0]] = b
        elif command[1].strip("abcdef").isdigit():
            self.gui.outPut("Error, you made your first argument a hex digit. MOV expects its first argument to be a register, or a memory address.")
        else:
            self.gui.outPut("MOV expects its first argument to be a memory address or register, and second to be a memory address, register, immediate value, or local variable.")

    def neg(self, command, i):
        """ Performs twos complement of the destination operand, and stores the result in the destination."""
        if command[1] in self.assembler.registers.keys():
            self.assembler.registers[command[1]] *= -1

    def pop(self, command, i):
        """ pop x will pop an element from the stack into register x """
        if command[1] in self.assembler.registers:
            self.assembler.registers[command[1]] = int(self.assembler.stackData.pop())
            self.gui.updateStack()

    def push(self, command, i):
        """ Push x will push the argument x to the stack """
        if command[1].strip("abcdef").isdigit():  # pushing a number to the stack, it's prolly hex so ignore the A-F chars
            self.assembler.stackData.append(int(command[1], 16))
            self.gui.updateStack()
        elif command[1] in self.assembler.registers:
            self.assembler.stackData.append(int(self.assembler.registers[command[1]]))
            self.gui.updateStack()
        elif command[1] in self.assembler.DATA.keys():  # pushing a string from .SECT .DATA to the stack
            self.assembler.stackData.append(self.assembler.DATA[command[1]][0])
            self.gui.updateStack()
        elif command[1] in self.assembler.localVars.keys():  # pushing a local int to the stack
            self.assembler.stackData.append(self.assembler.localVars[command[1]])
            self.gui.updateStack()
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.stackData.append(self.assembler.BSS[command[1]][0])
            self.gui.updateStack()
        elif "(" in command[1] and ")" in command[1]:
            temp = command[1][command[1].find("(") + 1:command[1].find(")")]
            if temp in self.assembler.BSS.keys():
                # TODO: memory
                1 + 1
            else:
                self.gui.outPut("Error on line " + str(i) + ". I don't understand what (" + temp + ") is")
                self.gui.stopRunning(-1)
        else:
            print(command)
            self.gui.outPut("Unknown error on line " + str(i) + ".")
            self.gui.stopRunning(-1)

    def pushf(self, command, i):
        """ Push the flags to the stack """

    def stosb(self, command, i):
        """ Stores contents of AX in the memory address contained in DI, then increments DI """
        self.assembler.addressSpace[self.assembler.registers["DI"]] = chr(self.assembler.registers["AX"])
        self.assembler.registers["DI"] += 1

    def stc(self, command, i):
        """ set the carry flag to true """
        self.assembler.flags["C"] = True

    def std(self, command, i):
        """ Set the direction flag to true """
        self.assembler.flags["D"] = True

    def sti(self, command, i):
        """ Set the interrupt flag to true """
        self.assembler.flags["I"] = True

    def sys(self, command, i):
        """ Call a system trap - evaluates based on the last piece of data on the stack """
        if len(self.assembler.stackData) == 0:
            self.gui.outPut("Invalid system trap: SYS called on line %d without any arguments on stack." % i)
            self.gui.stopRunning(-1)
        elif not int(self.assembler.stackData[-1]) in self.sysCodes.values():
            self.gui.outPut("Invalid system trap on line %d: The first argument \"%s\" on the stack is not understood" % (i, self.assembler.stackData[-1]))
            self.gui.stopRunning(-1)
        else:
            if int(self.assembler.stackData[-1]) == self.sysCodes["_EXIT"]:
                self.gui.stopRunning()
            elif int(self.assembler.stackData[-1]) == self.sysCodes["_GETCHAR"]:
                self.gui.getChar()
            elif int(self.assembler.stackData[-1]) == self.sysCodes["_OPEN"]:
                1 + 1
            elif int(self.assembler.stackData[-1]) == self.sysCodes["_PRINTF"]:
                try:
                    i = 2
                    args = []
                    while True:
                        if self.assembler.addressSpace.count("0") == 0:
                            formatStr = "".join(self.assembler.addressSpace[int(self.assembler.stackData[-i]):])
                        else:
                            formatStr = "".join(self.assembler.addressSpace[int(self.assembler.stackData[-i]):self.assembler.addressSpace.index("0", int(self.assembler.stackData[-i]))])
                        i += 1
                        print formatStr
                        numArgs = formatStr.count("%") - formatStr.count("\\%")
                        if numArgs == len(args): break
                        if numArgs != 0: continue
                        args.append(formatStr)
                    self.gui.outPut(formatStr % tuple(args))
                except IndexError:
                    self.gui.stopRunning(-1)
                    self.gui.outPut("Invalid system trap on line %d. Invalid number of arguments with _PRINTF." % i)

    def xchg(self, command, i):
        """ xchg, swaps two registers contents """
        if command[1] in self.assembler.registers and command[2] in self.assembler.registers:
            self.assembler.registers[command[1]], self.assembler.registers[command[2]] = self.assembler.registers[command[2]], self.assembler.registers[command[1]]
        else:
            self.gui.outPut("Error on line " + str(i) + ". XCHG expects both its arguments to be registers.")

"""
"AAA":0,  # Ascii adjust AL after addition
"AAD":0,  # Ascii adjust AX before division
"AAM":0,  # Ascii adjust AX after multiplication
"AAS":0,  # Ascii adjust AL after subtraction
"ADC":2,  # Add with carry
"AND":2,  # Logical and
"CALL":1,  # Call procedure
"CBW":0,  # Convert byte to word
"CMP":2,  # Compare operands
"CMPSB":-1,  # Compare bytes in memory
"CMPSW":-1,  # Compare words in memory
"CWD":0,  # Convert word to doubleword
"DAA":0,  # Decimal adjust AL after addition
"DAS":0,  # Decimal adjust AL after subtraction
"DIV":2,  # Unsigned divide
"IDIV":1,  # Signed divide
"IMUL":1,  # Signed multiply
"JA":1,  # Jump if above
"JAE":1,  # Jump if above or equal
"JB":1,  # Jump if below
"JBE":1,  # Jump if below or equal
"JNA":1,  # Jump if not above
"JNAE":1,  # Jump if not above or equal
"JNB":1,  # Jump if not below
"JNBE":1,  # Jump if not below or equal
"LAHF":0,  # Load flags into AH register
"LDS":2,  # Load pointer using DS
"LEA":2,  # Load effective address
"LES":2,  # Load ES with pointer
"LODSB":0,  # Load string byte
"LODSW":0,  # Load string word
"MOVSB":0,  # Move byte from string to string
"MOVSW":0,  # Move word from string to string
"MUL":2,  # Unsigned Multiply
"NOP":0,  # No Operation.
"NOT":1,  # Negate the opearand, logical NOT
"OR":2,  # Logical OR
"POPF":0,  # Pop data from flags register
"PUSHF":0,  # Push flags onto stack
"RCL":2,  # Rotate left with carry
"RCR":2,  # Rotate right with carry
"RET":0,  # Return from procedure
"ROL":2,  # Rotate left
"ROR":2,  # Rotate right
"SAHF":0,  # Store AH into flags
"SAL":2,  # Shift Arithmetically Left
"SAR":2,  # Shift Arithmetically Right
"SBB":2,  # Subtraction with borrow
"SCASB":0,  # Compare byte string
"SCASW":0,  # Compare word string
"SHL":2,  # unsigned Shift left
"SHR":2,  # unsigned Shift right
"STOSW":0,  # Store word in string
"SUB":2,  # Subtraction
"TEST":2,  # Logical compare (AND)
"XOR":2  # Logical XOR
"""