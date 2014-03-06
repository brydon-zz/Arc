'''
Created on 2013-10-20

@author: Brydon
'''

class CommandInterpreter(object):

    def __init__(self, gui, assembler):
        """ Link's this module with the self.assembler instance """
        self.SYSCodes = {"_EXIT":1, "_PRINTF":127, "_GETCHAR":117, "_SSCANF":125, "_READ":3, "_OPEN":5, "_CLOSE":6}
        self.assembler = assembler
        self.gui = gui
        self.LIST_TYPE = type([1, 1])

    def getCommandArgs(self):
        """ A dict whose keys are commands and their values are the # of arguments they expect """
        return {"AAA":0,  # Ascii adjust AL after ADDition
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
                "DAA":0,  # Decimal adjust AL after ADDition
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
                "JCXZ":1,  # Jump if CX is zero
                "JE":1,  # Jump if equal
                "JG":1,  # Jump if greater than
                "JGE":1,  # Jump if greater than or equal
                "JL":1,  # Jump if less than
                "JLE":1,  # Jump if less than or equal
                "JMP":1,  # Jump
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
                "NEG":1,  # Two's complement NEGation
                "NOP":0,  # No Operation.
                "NOT":1,  # Negate the opearand, logical NOT
                "OR":2,  # Logical OR
                "POP":1,  # Pop data from stack
                "POPF":0,  # Pop data from flags register
                "PUSH":1,  # Push data to stacscreek
                "PUSHF":0,  # Push flags onto stack
                "RCL":2,  # Rotate left with carry
                "RCR":2,  # Rotate right with carry
                "REP":-1,  # Repeat MOVS/STOS/CMPS/LODS/SCAS
                "REPE":-1,  # Repeat if equal
                "REPNE":-1,  # Repeat if not equal
                "REPNZ":-1,  # Repeat if not zero
                "REPZ":-1,  # Repeat if zero
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
                "ADC":lambda x, i: self.ADC(x, i),
                "ADD":lambda x, i: self.ADD(x, i),
                "AND":lambda x, i: self.AND(x, i),
                "CALL":lambda x, i: self.CALL(x, i),
                "CLC":lambda x, i: self.CLC(x, i),
                "CLD":lambda x, i: self.CLD(x, i),
                "CLI":lambda x, i: self.CLI(x, i),
                "CMPB":lambda x, i: self.CMPB(x, i),
                "DEC":lambda x, i: self.incdec(x, i, -1),
                "INC":lambda x, i: self.incdec(x, i, 1),
                "JA":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 and self.assembler.flags['Z'] == 0),
                "JAE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 or self.assembler.flags['Z'] == 1),
                "JB":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 and self.assembler.flags['Z'] == 0),
                "JBE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 or self.assembler.flags['Z'] == 1),
                "JC":lambda x, i: self.jf(x, i, self.assembler.flags['C'] == 1),
                "JCXZ":lambda x, i: self.jf(x, i, self.assembler.registers['CX'] == 0),
                "JE":lambda x, i: self.jf(x, i, self.assembler.flags['Z'] == 1),
                "JG":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 and self.assembler.flags['Z'] == 0),
                "JGE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 or self.assembler.flags['Z'] == 1),
                "JL":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 and self.assembler.flags['Z'] == 0),
                "JLE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 or self.assembler.flags['Z'] == 1),
                "JMP":lambda x, i: self.JMP(x, i),
                "JNA":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 or self.assembler.flags['Z'] == 1),
                "JNAE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 and self.assembler.flags['Z'] == 0),
                "JNB":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 or self.assembler.flags['Z'] == 1),
                "JNBE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 and self.assembler.flags['Z'] == 0),
                "JNC":lambda x, i: self.jf(x, i, self.assembler.flags['C'] == 0),
                "JNE":lambda x, i: self.jf(x, i, self.assembler.flags['Z'] == 0),
                "JNG":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 or self.assembler.flags['Z'] == 1),
                "JNGE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 1 and self.assembler.flags['Z'] == 0),
                "JNL":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 or self.assembler.flags['Z'] == 1),
                "JNLE":lambda x, i: self.jf(x, i, self.assembler.flags['S'] == 0 and self.assembler.flags['Z'] == 0),
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
                "LODSB":lambda x, i: self.LODSB(x, i),
                "LODSW":lambda x, i: self.LODSW(x, i),
                "LOOP":lambda x, i: self.LOOP(x, i),
                "LOOPE":lambda x, i: self.LOOPE(x, i),
                "LOOPNE":lambda x, i: self.LOOPNE(x, i),
                "LOOPNZ":lambda x, i: self.LOOPNZ(x, i),
                "LOOPZ":lambda x, i: self.LOOPZ(x, i),
                "MOV":lambda x, i: self.MOV(x, i),
                "NOP":lambda x, i: 1,  # best instruction
                "NOT":lambda x, i: self.NOT(x, i),
                "OR":lambda x, i: self.OR(x, i),
                "POP":lambda x, i: self.POP(x, i),
                "POPF":lambda x, i: self.POPF(x, i),
                "PUSH":lambda x, i: self.PUSH(x, i),
                "PUSHF":lambda x, i: self.PUSHF(x, i),
                "RCL":lambda x, i: self.RCL(x, i),
                "RCR":lambda x, i: self.RCR(x, i),
                "REP":lambda x, i: self.REP(x, i),
                "REPE":lambda x, i: self.REPE(x, i),
                "REPNE":lambda x, i: self.REPNE(x, i),
                "REPNZ":lambda x, i: self.REPNZ(x, i),
                "REPZ":lambda x, i: self.REPZ(x, i),
                "RET":lambda x, i: self.RET(x, i),
                "ROL":lambda x, i: self.ROL(x, i),
                "ROR":lambda x, i: self.ROR(x, i),
                "SAL":lambda x, i: self.SAL(x, i),
                "SAR":lambda x, i: self.SAR(x, i),
                "SBB":lambda x, i: self.SBB(x, i),
                "SHL":lambda x, i: self.SHL(x, i),
                "SHR":lambda x, i: self.SHR(x, i),
                "STC":lambda x, i: self.STC(x, i),
                "STD":lambda x, i: self.STD(x, i),
                "STI":lambda x, i: self.STI(x, i),
                "STOSB":lambda x, i: self.STOSB(x, i),
                "SUB":lambda x, i: self.SUB(x, i),
                "SYS":lambda x, i: self.SYS(x, i),
                "XCHG":lambda x, i: self.XCHG(x, i),
                "XOR":lambda x, i: self.XOR(x, i)
                }
    def ADC(self, command, i):
        """ ADC """
        self.ADD(command, i, True)

    def ADD(self, command, i, carry=False):
        """ ADD x,y translates to x = x + y
        where x is a register or mem address, y is a number, localvar, mem address, or register. """
        if command[1] == "SP" and command[2].isdigit():  # TODO: REPLACE THIS
            for j in range(int(command[2]) / 2):
                if len(self.assembler.stackData) > 0:
                    self.assembler.stackData.pop()
                    self.gui.updateStack()
            self.assembler.registers['SP'] += int(command[2])
            return
        if self.assembler.isHex(command[1]):
            self.gui.outPut("Error on line " + str(i) + ". " + command[0] + " cannot have a numerical first argument.")
            self.gui.stopRunning(-1)
            return

        """ To save on code space, y will serve as "second guy" """
        if self.assembler.isHex(command[2]):  # y is a digit
            y = int(command[2], 16)
        elif command[2] in self.assembler.localVars.keys():  # y is a local var
            y = int(self.assembler.localVars[command[2]])
        elif command[2] in self.assembler.registers.keys():  # y is a register
            y = self.assembler.registers[command[2]]
        elif command[2] in self.assembler.DATA.keys():  # y is a mem address from DATA section
            y = self.assembler.addressSpace[self.assembler.DATA[command[2]][0]]
        elif command[2] in self.assembler.BSS.keys():  # y is a mem address from BSS section
            y = self.assembler.addressSpace[self.assembler.BSS[command[2]][0]]

        if carry: y += self.assembler.flags['C']
        if command[0].upper() == "SUB" or command[0].upper() == "SBB": y *= -1

        if command[1] in self.assembler.registers.keys():  # x is a register
            self.assembler.registers[command[1]] += y
            result = self.assembler.registers[command[1]]
        elif command[1] in self.assembler.DATA.keys():  # x is a data location
            self.assembler.addressSpace[self.assembler.DATA[command[1]][0]] += y
            result = self.assembler.addressSpace[self.assembler.DATA[command[1]][0]]
        elif command[1] in self.assembler.BSS.keys():  # x is a BSS location
            self.assembler.addressSpace[self.assembler.BSS[command[1]][0]] += y
            result = self.assembler.addressSpace[self.assembler.BSS[command[1]][0]]

        if result == 0:
            self.assembler.flags['Z'] = 1
        elif result < 0:
            self.assembler.flags['S'] = 1

        if result >= 2 ** 15 and command[1] in self.assembler.registers.keys():
            while self.assembler.registers[command[1]] >= 2 ** 15:
                self.assembler.registers[command[1]] -= 2 ** 16
                self.assembler.flags['O'] = 1
        elif result < -2 ** 15 and command[1] in self.assembler.registers.keys():
            while self.assembler.registers[command[1]] < -2 ** 15:
                self.assembler.registers[command[1]] += 2 ** 16
                self.assembler.flags['O'] = 1

    def AND(self, command, i):
        """ AND [register or memory address], [register, memory address, local variable, or hex value]
        
        AND A, B --> A = A & B
        
        Logical AND: Each bit in A is anded with the corresponding bit in B."""

        if self.assembler.isHex(command[2]):  # y is a digit
            t = int(command[2], 16)
        elif command[2] in self.assembler.localVars.keys():  # y is a local var
            t = self.assembler.localVars[command[2]]
        elif command[2] in self.assembler.registers:
            t = self.assembler.registers[command[2]]
        elif command[2] in self.assembler.DATA.keys():
            t = self.assembler.DATA[self.assembler.registers[command[2]]]
        elif command[2] in self.assembler.BSS.keys():
            t = self.assembler.BSS[self.assembler.registers[command[2]]]

        if command[1] in self.assembler.registers:
            self.assembler.registers[command[1]] &= t
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.BSS[command[1]] &= t
        elif command[1] in self.assembler.DATA.keys():
            self.assembler.DATA[command[1]] &= t

    def CALL(self, command, i):
        """ CALL [label]
        
        
        """
        if command[1] in self.assembler.lookupTable.keys():
            self.assembler.jumpLocation = self.assembler.lookupTable[command[1]]
            self.assembler.stackData.append(self.assembler.registers['PC'] + 1)
            self.gui.updateStack()
        else:
            self.gui.outPut("Big issue with this label guy.")

    def CBW(self, command, i):
        """ CBW """
        if self.assembler.eightBitRegister("AL") >= 128:
            self.assembler.registers['AX'] -= 256

    def CLC(self, command, i):
        """ set the carry flag to false """
        self.assembler.flags["C"] = False

    def CLD(self, command, i):
        """ set the direction flag to false """
        self.assembler.flags['D'] = False

    def CLI(self, commmand, i):
        """ set the interrupt flag to false """
        self.assembler.flags['I'] = False

    def CMC(self, command, i):
        """ Complements the carry flag, toggling it """
        self.assembler.flags['C'] = not self.assembler.flags["C"]

    def CMPB(self, command, i):
        """ CMPB x,y where x and y are bytes, if equal set the zero flag accordingly """
        a = command[1:3]
        b = []
        for x in a:
            if x in ['AH', 'AL', 'BH', 'BL', 'CH', 'CL', 'DH', 'DL']:
                x = self.assembler.eightBitRegister(x)
            elif x in ['AX', 'BX', 'CX', 'DX']:
                self.gui.outPut("Illegal argument for CMPB on line %d. %s is a 16 bit register, perhaps you meant one of the 8 bit %s or %s registers?" % (i, x, x[0] + "H", x[0] + "L"))
                self.gui.stopRunning(-1)
                return
            elif type(x) == type(""):
                x = self.assembler.replaceEscapedSequences(x.rstrip("'\"").lstrip("'\""))

                if len(x) != 1:
                    self.gui.outPut("Illegal argument %s for CMPB on line %d. CMPB expects all strings to be ONE byte in length." % (x, i))
                    self.gui.stopRunning(-1)
                    return
                else:
                    try:
                        x = int(x)
                    except ValueError:
                        x = ord(x)
            elif type(x) != type(1):
                self.assembler.out("Illegal argument %s for CMPB on line %d. CMPB expects an argument to be a one byte register (ie: AH, AL, etc.), an integer, or a one byte string (ie: \"L\", etc.). Instead %s was given." % (x, i, x))
            b.append(x)

        self.assembler.flags["Z"] = b[0] == b[1]

    def JMP(self, command, i, referer="JMP"):
        """ JMP x jumps to position x in the program """
        if command[1] in self.assembler.lookupTable.keys() and not self.assembler.isHex(command[1]):
            self.assembler.jumpLocation = self.assembler.lookupTable[command[1]]
        elif (command[1].rstrip('b').isdigit() or command[1].rstrip('f').isdigit()) and command[1].strip('bf') in self.assembler.lookupTable.keys():
            temp = command[1].rstrip('bf')
            m = -1
            if type(self.assembler.lookupTable[temp]) == self.LIST_TYPE:
                for x in self.assembler.lookupTable[temp]:
                    if command[1][-1] == 'b':
                        if x < self.assembler.registers['PC'] and (m < x or m == -1):
                            m = x
                    else:
                        if x > self.assembler.registers['PC'] and (x < m or m == -1):
                            m = x
            else:
                m = self.assembler.lookupTable[temp]

            if m == -1:
                self.gui.outPut("Fatal error on line " + str(i) + ". The label " + command[1] + " could not be resolved.")
                self.gui.stopRunning(-1)
            else:
                self.assembler.jumpLocation = m

        elif self.assembler.isHex(command[1]):
            self.assembler.jumpLocation = int(command[1], 16)
        else:
            self.gui.outPut("Error on line " + str(i) + ". The label " + command[1] + " is not defined for " + referer + "-ing to.")

    def LODSB(self, command, i):
        """ LODSB
        
        """
        self.assembler.registers['AX'] = self.assembler.addressSpace[self.assembler.registers['SI']]

        self.assembler.registers['SI'] += -1 if self.assembler.flags['D'] else 1

    def LODSW(self, command, i):
        """ LODSW
        
        """
        self.assembler.registers['AX'] = self.assembler.addressSpace[self.assembler.registers['SI']] + self.assembler.addressSpace[self.assembler.registers['SI'] + 1] * 256

        self.assembler.registers['SI'] += -2 if self.assembler.flags['D'] else 2

    def LOOP(self, command, i, flag=True):
        """ Decrements CX and jumps to a label if CX is greater than zero. """
        if flag and self.assembler.registers["CX"] > 0:
            self.JMP(command, i, "LOOP")
            self.assembler.registers["CX"] -= 1

    def LOOPE(self, command, i):
        """ LOOPE
        """
        self.LOOP(command, i, self.assembler.flags['Z'])

    def LOOPNE(self, command, i):
        """ LOOPNE
        """
        self.LOOP(command, i, not self.assembler.flags['Z'])

    def LOOPNZ(self, command, i):
        """ LOOPNZ
        """
        self.LOOP(command, i, not self.assembler.flags['Z'])

    def LOOPZ(self, command, i):
        """ LOOPZ
        """
        self.LOOP(command, i, self.assembler.flags['Z'])

    def MOV(self, command, i):
        """ Mov A,B  evaluates as A=B where A is a register or memory address and B is a memory,
            register address, local variable, or number. """

        if self.assembler.isHex(command[2]):  # B is digit
            b = int(command[2], 16)
        elif command[2] in self.assembler.localVars.keys():  # B is local var
            b = int(self.assembler.localVars[command[2]])
        elif command[2] in self.assembler.BSS.keys():  # B is BSS mem address
            b = int(self.assembler.BSS[command[2]][0])
        elif command[2] in self.assembler.DATA.keys():  # B is DATA mem address
            b = int(self.assembler.DATA[command[2]][0])
        else:
            self.gui.outPut("Incorrect B val.")
            self.gui.stopRunning(-1)

        if command[1] in self.assembler.registers.keys():
            self.assembler.registers[command[1]] = b
        elif command[1] in self.assembler.DATA.keys():
            self.assembler.addressSpace[self.assembler.DATA[command[1]][0]] = b
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.addressSpace[self.assembler.BSS[command[1]][0]] = b
        elif self.assembler.isHex(command[1]):
            self.gui.outPut("Error, you made your first argument a hex digit. MOV expects its first argument to be a register, or a memory address.")
        else:
            self.gui.outPut("MOV expects its first argument to be a memory address or register, and second to be a memory address, register, immediate value, or local variable.")

    def MOVSB(self, command, i):
        """ MOVSB"""
        self.assembler.addressSpace[self.assembler.registers['DI']] = self.assembler.addressSpace[self.assembler.registers['SI']]
        self.assembler.registers['SI'] += -1 if self.assembler.flags['D'] else 1


    def MOVSW(self, command, i):
        """ MOVSW"""
        self.assembler.addressSpace[self.assembler.registers['DI']] = self.assembler.addressSpace[self.assembler.registers['SI']]
        self.assembler.addressSpace[self.assembler.registers['DI'] + 1] = self.assembler.addressSpace[self.assembler.registers['SI'] + 1]
        self.assembler.registers['SI'] += -2 if self.assembler.flags['D'] else 2

    def NEG(self, command, i):
        """ Performs twos complement of the deSTInation operand, and stores the result in the deSTInation."""
        if command[1] in self.assembler.registers.keys():
            self.assembler.registers[command[1]] *= -1

    def NOT(self, command, i):
        """NOT [register or memory address]
        
        NOT A --> A = not A
        
        Performs a logical NOT on an operand by reversing each of its bits."""
        if command[1] in self.assembler.registers:
            self.assembler.registers[command[1]] = ~self.assembler.registers[command[1]]
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.BSS[command[1]] = ~self.assembler.BSS[command[1]]
        elif command[1] in self.assembler.DATA.keys():
            self.assembler.DATA[command[1]] = ~self.assembler.DATA[command[1]]

    def OR(self, command, i):
        """ OR [register or memory address], [register, memory address, local variable, or hex value]
        
        OR A, B --> A = A or B
        
        Inclusive OR: Performs a logical OR between each bit in A and each bit in B. If either bit is a 1 in each position, the resulting bit is a 1."""

        if self.assembler.isHex(command[2]):  # y is a digit
            t = int(command[2], 16)
        elif command[2] in self.assembler.localVars.keys():  # y is a local var
            t = self.assembler.localVars[command[2]]
        elif command[2] in self.assembler.registers:
            t = self.assembler.registers[command[2]]
        elif command[2] in self.assembler.DATA.keys():
            t = self.assembler.DATA[self.assembler.registers[command[2]]]
        elif command[2] in self.assembler.BSS.keys():
            t = self.assembler.BSS[self.assembler.registers[command[2]]]

        if command[1] in self.assembler.registers:
            self.assembler.registers[command[1]] |= t
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.BSS[command[1]] |= t
        elif command[1] in self.assembler.DATA.keys():
            self.assembler.DATA[command[1]] |= t

    def POP(self, command, i):
        """ POP x will POP an element from the stack into register x """
        if command[1] in self.assembler.registers:
            self.assembler.registers[command[1]] = int(self.assembler.stackData.pop())
            self.assembler.registers['SP'] += 2
            self.gui.updateStack()

    def POPF(self, command, i):
        """ POPF
        
        Pops the data from the top of the stack into the flags register."""
        flags = self.assembler.stackData.pop()

        self.assembler.flags['C'] = flags % 2
        flags /= 4
        self.assembler.flags['P'] = flags % 2
        flags /= 4
        self.assembler.flags['A'] = flags % 2
        flags /= 4
        self.assembler.flags['Z'] = flags % 2
        flags /= 2
        self.assembler.flags['S'] = flags % 2

        self.gui.updateStack()
        self.assembler.registers['SP'] += 2

    def PUSH(self, command, i):
        """ Push x will PUSH the argument x to the stack """
        if self.assembler.isHex(command[1]):  # PUSHing a number to the stack, it's prolly hex so ignore the A-F chars
            self.assembler.stackData.append(int(command[1], 16))
            self.assembler.registers['SP'] -= 2
            self.gui.updateStack()
        elif command[1] in self.assembler.registers:
            self.assembler.stackData.append(int(self.assembler.registers[command[1]]))
            self.assembler.registers['SP'] -= 2
            self.gui.updateStack()
        elif command[1] in self.assembler.DATA.keys():  # PUSHing a string from .SECT .DATA to the stack
            self.assembler.stackData.append(self.assembler.DATA[command[1]][0])
            self.assembler.registers['SP'] -= 2
            self.gui.updateStack()
        elif command[1] in self.assembler.localVars.keys():  # PUSHing a local int to the stack
            self.assembler.stackData.append(self.assembler.localVars[command[1]])
            self.assembler.registers['SP'] -= 2
            self.gui.updateStack()
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.stackData.append(self.assembler.BSS[command[1]][0])
            self.assembler.registers['SP'] -= 2
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

    def PUSHF(self, command, i):
        """ PUSHF
        
        Pushes the flags register onto the stack."""
        flags = self.assembler.flags['S'] * (128) + self.assembler.flags['Z'] * (64) + self.assembler.flags['A'] * (16) + self.assembler.flags['P'] * (4) + self.assembler.flags['C']
        self.assembler.stackData.append(flags)
        self.assembler.registers['SP'] -= 2
        self.gui.updateStack()

    def RCL(self, command, i):
        """ RCL [register]
        
        Rotates the operand left. The carry flag is copied into the lowest bit, and the highest bit is copied into the carry flag."""
        if command[1] in self.assembler.registers:
            temp = self.assembler.registers[command[1]] < 0

            if temp:
                self.assembler.registers[command[1]] += 2 ** 16

            self.assembler.registers[command[1]] = self.assembler.registers[command[1]] << 1

            self.assembler.registers[command[1]] += self.assembler.flags['C']

            while self.assembler.registers[command[1]] >= 2 ** 15:
                self.assembler.registers[command[1]] -= 2 ** 16

            self.assembler.flags['C'] = temp
        else:
            self.gui.outPut("RCL expects its argument to be a register.")
            self.gui.stopRunning(-1)
            return

    def RCR(self, command, i):
        """ RCR [register]
        
        Rotates the operand right. The carry flag is copied into the highest bit, and the lowest bit is copied into the carry flag."""
        if command[1] in self.assembler.registers:
            temp = self.assembler.registers[command[1]] % 2

            if self.assembler.registers[command[1]] < 0:
                self.assembler.registers[command[1]] += 2 ** 16

            self.assembler.registers[command[1]] = self.assembler.registers[command[1]] >> 1

            while self.assembler.registers[command[1]] >= 2 ** 15:
                self.assembler.registers[command[1]] -= 2 ** 16

            if self.assembler.flags['C']:
                self.assembler.registers[command[1]] -= 2 ** 15

            self.assembler.flags['C'] = temp
        else:
            self.gui.outPut("RCR expects its argument to be a register.")
            self.gui.stopRunning(-1)
            return

    def REP(self, command, i):
        """ REP
        
        Repeats the instruction until CX is zero. """
        if command[1] in ["MOVS", "MOVSB", "CMPS", "CMPSB", "CMPSW", "SCAS", "SCASB", "SCASW", "STOS", "STOSB", "STOSW", "LODS", "LODSB", "LODSW"]:
            while self.assembler.registers['CX'] > 0:
                self.getFunctionTable()[command[1:], i]
                self.assembler.registers['CX'] -= 1
        else:
            self.gui.outPut("Innapropriate command used with REP")
            self.gui.stopRunning(-1)

    def REPE(self, command, i):
        """ REPE [command]
        
        fdfd """
        if command[1] in ["CMPS", "CMPSB", "CMPSW", "SCAS", "SCASB", "SCASW"]:
            while self.assembler.flags["Z"] and self.assembler.registers['CX'] > 0:
                self.getFunctionTable()[command[1:], i]
                self.assembler.registers['CX'] -= 1
        else:
            self.gui.outPut("Innapropriate command used with " + command[0])
            self.gui.stopRunning(-1)

    def REPNE(self, command, i):
        """ REPNE [command]
        
        fdfd """
        if command[1] in ["CMPS", "CMPSB", "CMPSW", "SCAS", "SCASB", "SCASW"]:
            while not self.assembler.flags["Z"] and self.assembler.registers['CX'] > 0:
                self.getFunctionTable()[command[1:], i]
                self.assembler.registers['CX'] -= 1
        else:
            self.gui.outPut("Innapropriate command used with " + command[0])
            self.gui.stopRunning(-1)

    def REPNZ(self, command, i):
        """ REPNZ [command]
        
        fdfd """
        self.REPNE(command, i)

    def REPZ(self, command, i):
        """REPZ [command]
        
        fdfd """
        self.REPE(command, i)

    def RET(self, command, i):
        """ RET 
        
        Return from a procedure call.  Pops the last entry off the stack into the program count register and returns there."""
        if len(self.assembler.stackData) == 0:
            self.gui.outPut("Stack empty, where do i return tooo!!!!???")
            self.gui.stopRunning(-1)
        elif self.assembler.codeBounds[0] <= self.assembler.stackData[-1] <= self.assembler.codeBounds[1]:
            self.assembler.jumpLocation = self.assembler.stackData.pop()
            self.gui.updateStack()
        else:
            self.gui.outPut("Returning on a suspect address.")
            print self.assembler.codeBounds[0]
            print self.assembler.stackData[-1]
            print self.assembler.codeBounds[1]
            self.gui.stopRunning(-1)

    def ROL(self, command, i):
        """ ROL [register]
        
        Rotates the operand left, the highest bit is copied into the carry flag and MOVed into the lowest bit position."""
        if command[1] in self.assembler.registers:
            temp = self.assembler.registers[command[1]] < 0

            if temp:
                self.assembler.registers[command[1]] += 2 ** 16

            self.assembler.registers[command[1]] = self.assembler.registers[command[1]] << 1

            while self.assembler.registers[command[1]] >= 2 ** 15:  # this is when 0100
                self.assembler.registers[command[1]] -= 2 ** 16

            self.assembler.registers[command[1]] += temp

            self.assembler.flags['C'] = temp
        else:
            self.gui.outPut("RCL expects its argument to be a register.")
            self.gui.stopRunning(-1)
            return

    def ROR(self, command, i):
        """ ROR [register]
        
        Rotates the operand right, the lowest bit is copied into the carry flag and MOVed into the highest bit position."""
        if command[1] in self.assembler.registers:
            temp = self.assembler.registers[command[1]] % 2

            while self.assembler.registers[command[1]] < 0:
                self.assembler.registers[command[1]] += 2 ** 16

            self.assembler.registers[command[1]] = self.assembler.registers[command[1]] >> 1

            if self.assembler.registers[command[1]] >= 2 ** 15:
                self.assembler.registers[command[1]] -= 2 ** 16

            self.assembler.registers[command[1]] -= temp * 2 ** 15

            self.assembler.flags['C'] = temp
        else:
            self.gui.outPut("RCL expects its argument to be a register.")
            self.gui.stopRunning(-1)
            return

    def SAHF(self, command, i):
        """ SAHF
        
        Store AH into flags: Copies AH into bits 0 through 7 into the flags register."""
        flags = self.assembler.eightBitRegister('AH')
        for f in ['C', 'P', 'A', 'Z', 'S', 'I', 'D', 'O']:
            self.assembler.flags[f] = self.flags % 2
            flags /= 2
        self.gui.updateStack()

    def SAL(self, command, i):
        """ SAL register
        
        SAL is identical to SHL and is included in the instruction set only for completeness."""
        self.SHL(self, command, i)

    def SAR(self, command, i):
        """ SAR register
        """
        if command[1] in self.assembler.registers:
            temp = self.assembler.registers[command[1]] < 0
            self.assembler.flags['C'] = self.assembler.registers[command[1]] % 2

            if temp:
                self.assembler.registers[command[1]] += 2 ** 16

            self.assembler.registers[command[1]] = self.assembler.registers[command[1]] >> 1

            if self.assembler.registers[command[1]] >= 2 ** 15:  # this is when 0100
                self.assembler.registers[command[1]] -= 2 ** 16

            self.assembler.registers[command[1]] -= temp * 2 ** 15


        else:
            self.gui.outPut("RCL expects its argument to be a register.")
            self.gui.stopRunning(-1)
            return

    def SBB(self, command, i):
        """ SBB """
        self.ADD(command, i, True)

    def SHL(self, command, i):
        """SHL register
        """

        if command[1] in self.assembler.registers:
            temp = self.assembler.registers[command[1]] < 0

            if temp:
                self.assembler.registers[command[1]] += 2 ** 16

            self.assembler.registers[command[1]] = self.assembler.registers[command[1]] << 1

            if self.assembler.registers[command[1]] >= 2 ** 15:  # this is when 0100
                self.assembler.registers[command[1]] -= 2 ** 16

            self.assembler.flags['C'] = temp
        else:
            self.gui.outPut("RCL expects its argument to be a register.")
            self.gui.stopRunning(-1)
            return

    def SHR(self, command, i):
        """SHR register
        """

        if command[1] in self.assembler.registers:
            temp = self.assembler.registers[command[1]] % 2

            if self.assembler.registers[command[1]] < 0:
                self.assembler.registers[command[1]] += 2 ** 16

            self.assembler.registers[command[1]] = self.assembler.registers[command[1]] >> 1

            if self.assembler.registers[command[1]] >= 2 ** 15:  # this is when 0100
                self.assembler.registers[command[1]] -= 2 ** 16

            self.assembler.flags['C'] = temp
        else:
            self.gui.outPut("RCL expects its argument to be a register.")
            self.gui.stopRunning(-1)
            return

    def STC(self, command, i):
        """ set the carry flag to true """
        self.assembler.flags["C"] = True

    def STD(self, command, i):
        """ Set the direction flag to true """
        self.assembler.flags["D"] = True

    def STI(self, command, i):
        """ Set the interrupt flag to true """
        self.assembler.flags["I"] = True

    def STOSB(self, command, i):
        """ Stores contents of AX in the memory address contained in DI, then increments DI """
        self.assembler.addressSpace[self.assembler.registers["DI"]] = chr(self.assembler.registers["AX"])
        self.assembler.registers["DI"] += 1

    def SUB(self, command, i):
        """ SUB x,y
        
        """
        self.ADD(command, i, -1)

    def SYS(self, command, i):
        """ Call a system trap - evaluates based on the last piece of data on the stack """
        if len(self.assembler.stackData) == 0:
            self.gui.outPut("Invalid system trap: SYS called on line %d without any arguments on stack." % i)
            self.gui.stopRunning(-1)
        elif not int(self.assembler.stackData[-1]) in self.SYSCodes.values():
            self.gui.outPut("Invalid system trap on line %d: The first argument \"%s\" on the stack is not understood" % (i, self.assembler.stackData[-1]))
            self.gui.stopRunning(-1)
        else:
            if int(self.assembler.stackData[-1]) == self.SYSCodes["_EXIT"]:
                self.gui.stopRunning()
            elif int(self.assembler.stackData[-1]) == self.SYSCodes["_GETCHAR"]:
                self.gui.getChar()
            elif int(self.assembler.stackData[-1]) == self.SYSCodes["_OPEN"]:
                1 + 1
            elif int(self.assembler.stackData[-1]) == self.SYSCodes["_PRINTF"]:
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
                        numArgs = formatStr.count("%") - formatStr.count("\%")
                        if numArgs == len(args): break
                        if numArgs != 0: continue
                        args.append(formatStr)
                    self.gui.outPut(formatStr % tuple(args))
                except IndexError:
                    self.gui.stopRunning(-1)
                    self.gui.outPut("Invalid system trap on line %d. Invalid number of arguments with _PRINTF." % i)

    def XCHG(self, command, i):
        """ XCHG, swaps two registers contents """
        if command[1] in self.assembler.registers and command[2] in self.assembler.registers:
            self.assembler.registers[command[1]], self.assembler.registers[command[2]] = self.assembler.registers[command[2]], self.assembler.registers[command[1]]
        else:
            self.gui.outPut("Error on line " + str(i) + ". XCHG expects both its arguments to be registers.")

    def XOR(self, command, i):
        """ XOR [register or memory location],[register, memory location, local variable, or hex value]
        
        XOR A, B --> A = XOR(A,B)
        Exclusive OR: Each bit in B is exclusive ORed with its corresponding bit in A. The result is stored in A."""

        if self.assembler.isHex(command[2]):  # y is a digit
            t = int(command[2], 16)
        elif command[2] in self.assembler.localVars.keys():  # y is a local var
            t = self.assembler.localVars[command[2]]
        elif command[2] in self.assembler.registers:
            t = self.assembler.registers[command[2]]
        elif command[2] in self.assembler.DATA.keys():
            t = self.assembler.DATA[self.assembler.registers[command[2]]]
        elif command[2] in self.assembler.BSS.keys():
            t = self.assembler.BSS[self.assembler.registers[command[2]]]

        if command[1] in self.assembler.registers:
            self.assembler.registers[command[1]] ^= t
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.BSS[command[1]] ^= t
        elif command[1] in self.assembler.DATA.keys():
            self.assembler.DATA[command[1]] ^= t

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
        """ JMP if the flag is true, used for jo, jg, jge, etc. """
        if flag:
            self.JMP(command, i)

"""   20 more to go
"AAA":0,  # Ascii adjust AL after ADDition
"AAD":0,  # Ascii adjust AX before division
"AAM":0,  # Ascii adjust AX after multiplication
"AAS":0,  # Ascii adjust AL after subtraction
"CMP":2,  # Compare operands
"CMPSB":-1,  # Compare bytes in memory
"CMPSW":-1,  # Compare words in memory
"DAA":0,  # Decimal adjust AL after ADDition
"DAS":0,  # Decimal adjust AL after subtraction
"DIV":2,  # Unsigned divide 
"IDIV":1,  # Signed divide
"IMUL":1,  # Signed multiply
"LDS":2,  # Load pointer using DS
"LEA":2,  # Load effective address
"LES":2,  # Load ES with pointer
"MUL":2,  # Unsigned Multiply
"SCASB":0,  # Compare byte string
"SCASW":0,  # Compare word string
"STOSW":0,  # Store word in string
"TEST":2,  # Logical compare (AND)
"""
