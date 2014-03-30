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
                "AAA":self.AAA,
                "AAD":self.AAD,
                "AAM":self.AAM,
                "AAS":self.AAS,
                "ADC":self.ADC,
                "ADD":self.ADD,
                "AND":self.AND,
                "CALL":self.CALL,
                "CLC":self.CLC,
                "CLD":self.CLD,
                "CLI":self.CLI,
                "CMPB":self.CMPB,
                "DAA":self.DAA,
                "DAS":self.DAS,
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
                "JMP":self.JMP,
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
                "LODSB":self.LODSB,
                "LODSW":self.LODSW,
                "LOOP":self.LOOP,
                "LOOPE":self.LOOPE,
                "LOOPNE":self.LOOPNE,
                "LOOPNZ":self.LOOPNZ,
                "LOOPZ":self.LOOPZ,
                "MOV":self.MOV,
                "NOP":lambda x, i: 1,  # best instruction
                "NOT":self.NOT,
                "OR":self.OR,
                "POP":self.POP,
                "POPF":self.POPF,
                "PUSH":self.PUSH,
                "PUSHF":self.PUSHF,
                "RCL":self.RCL,
                "RCR":self.RCR,
                "REP":self.REP,
                "REPE":self.REPE,
                "REPNE":self.REPNE,
                "REPNZ":self.REPNZ,
                "REPZ":self.REPZ,
                "RET":self.RET,
                "ROL":self.ROL,
                "ROR":self.ROR,
                "SAL":self.SAL,
                "SAR":self.SAR,
                "SBB":self.SBB,
                "SHL":self.SHL,
                "SHR":self.SHR,
                "STC":self.STC,
                "STD":self.STD,
                "STI":self.STI,
                "STOSB":self.STOSB,
                "STOSW":self.STOSW,
                "SUB":self.SUB,
                "SYS":self.SYS,
                "XCHG":self.XCHG,
                "XOR":self.XOR
                }

    def AAA(self, command, i):
        """name:AAA
		args:None
        title:ASCII Adjust AL After Addition
		description:Adjusts the result in AL after two ASCII digits have been added together. If AL>9, the high digit of the result is placed in AH, and the Carry and Auxiliary flags are set.
		flags:?,,,?,?,*,?,*"""
        if (self.assembler.eightBitRegister('AL') & 15 > 9) or self.assembler.flags['A']:
            tempAH = self.assembler.eightbitRegister('AH')
            self.assembler.registers['AX'] = (self.assembler.eightBitRegister('AL') + 6) & 15
            self.assembler.registers['AX'] += (tempAH + 1) * 256
            self.assembler.flags['A'] = 1
            self.assembler.flags['C'] = 1
        else:
            self.assembler.flags['A'] = 0
            self.assembler.flags['C'] = 0

    def AAD(self, command, i):
        """name:AAD
		args:None
        title:ASCII Adjust AL Before Division
		description:Converts unpacked BCD digits in AH and AL to a single binary value in preperation for the DIV instruction.
		flags:?,,,*,*,?,*,?"""
        self.assembler.registers['AX'] = self.assembler.eightBitRegister('AL') + self.assembler.eightBitRegister('AH') * 10

    def AAM(self, command, i):
        """name:AAM
        args:None
        title:ASCII Adjust AL After Multiplication
		description:Adjusts the result in AX after two unpacked BCD digits have been multiplied together
		flags:?,,,*,*,?,*,?"""
        tempAL = self.assembler.eightBitRegister('AL')
        self.assembler.registers['AX'] = (tempAL % 10) + (tempAL / 10) * 256

    def AAS(self, command, i):
        """name:AAS
        args:None
        title:ASCII Adjust AL After Subtraction
		description:Adjusts the result in AX after a subtraction operation. If AL>9, AAS decrements AH and sets the Carry and Auxiliary Carry flags.
		flags:?,,,?,?,*,?,*"""
        if (self.assembler.eightBitRegister('AL') & 15 > 9) or self.assembler.flags['A']:
            tempAH = self.assembler.eightbitRegister('AH')
            self.assembler.registers['AX'] = (self.assembler.eightBitRegister('AL') - 6) & 15
            self.assembler.registers['AX'] += (tempAH - 1) * 256
            self.assembler.flags['A'] = 1
            self.assembler.flags['C'] = 1
        else:
            self.assembler.flags['A'] = 0
            self.assembler.flags['C'] = 0

    def ADC(self, command, i):
        """name:ADC
		args:[reg:mem],[reg:mem:immed]
		title:Add with Carry
		description:Adds the source and destination operands, and adds the contents of the Carry flag to the sum, which is stored in the destination
		flags:*,,,*,*,*,*,*"""
        self.ADD(command, i, carry=True)

    def ADD(self, command, i, carry=False, inPlace=False):
        """name:ADD
		args:[reg:mem],[reg:mem:immed]
		title:Add
		description:A source operand is added to a destination operand, and the sum is stored in the destination.
		flags:*,,,*,*,*,*,*"""
        if command[1] == "SP" and command[2].isdigit():  # TODO: REPLACE THIS
            for j in range(int(command[2]) / 2):
                if len(self.assembler.stackData) > 0:
                    self.assembler.stackData.pop()
                    self.gui.updateStack()
            self.assembler.registers['SP'] += int(command[2])
            return
        if self.assembler.isHex(command[1]):
            if not inPlace:
                self.gui.outPut("Error on line " + str(i) + ". " + command[0] + " cannot have a numerical first argument.")
                self.gui.stopRunning(-1)
                return

        """ To save on code space, y will serve as "second guy" """
        if self.assembler.isHex(command[2]):  # y is a digit
            if command[2][-1] == "h":
                y = int(command[2][:-1], 16)
            else:
                y = int(command[2])
        elif command[2] in self.assembler.localVars.keys():  # y is a local var
            y = int(self.assembler.localVars[command[2]])
        elif command[2] in self.assembler.registers.keys():  # y is a register
            y = self.assembler.registers[command[2]]
        elif command[2] in self.assembler.DATA.keys():  # y is a mem address from DATA section
            y = self.assembler.addressSpace[self.assembler.DATA[command[2]][0]]
        elif command[2] in self.assembler.BSS.keys():  # y is a mem address from BSS section
            y = self.assembler.addressSpace[self.assembler.BSS[command[2]][0]]
        elif len(command[2].strip('"').strip("'")) == 1:
            y = ord(command[2].strip('"').strip("'"))
        else:
            self.gui.outPut("What the heck is going on with your second argument!?!?!")
            self.gui.stopRunning(-1)
            return

        if carry: y += self.assembler.flags['C']
        if command[0].upper() in ["SUB", "SBB", "CMP", "CMPB", "SCASB", "SCASW"]: y *= -1

        if command[1] in self.assembler.registers.keys():  # x is a register
            result = self.assembler.registers[command[1]] + y
            if not inPlace: self.assembler.registers[command[1]] = result
        elif command[1] in self.assembler.DATA.keys():  # x is a data location
            result = self.assembler.addressSpace[self.assembler.DATA[command[1]][0]] + y
            if not inPlace: self.assembler.addressSpace[self.assembler.DATA[command[1]][0]] = result
        elif command[1] in self.assembler.BSS.keys():  # x is a BSS location
            result = self.assembler.addressSpace[self.assembler.BSS[command[1]][0]] + y
            if not inPlace: self.assembler.addressSpace[self.assembler.BSS[command[1]][0]] = result
        elif inPlace:
            result = int(command[1], 10) + y

        if result >= 2 ** 15 and command[1] in self.assembler.registers.keys():
            while self.assembler.registers[command[1]] >= 2 ** 15:
                self.assembler.registers[command[1]] -= 2 ** 16
                self.assembler.flags['O'] = 1
        elif result < -2 ** 15 and command[1] in self.assembler.registers.keys():
            while self.assembler.registers[command[1]] < -2 ** 15:
                self.assembler.registers[command[1]] += 2 ** 16
                self.assembler.flags['O'] = 1

        if result == 0:
            self.assembler.flags['Z'] = 1
        elif result < 0:
            self.assembler.flags['S'] = 1

    def AND(self, command, i, inPlace=False):
        """name:AND
		title:Logical And
		args:[reg:mem],[reg:mem:immed]
		description:Each bit in the destination operand is ANDed with the corresponding bit in the source operand
		flags:*,,,*,*,?,*,0"""
        
        AND A, B --> A = A & B
        
        Logical AND: Each bit in A is anded with the corresponding bit in B."""

        if self.assembler.isHex(command[2]):  # y is a digit
            if command[2][-1] == "h":
                t = int(command[2][:-1], 16)
            else:
                t = int(command[2])
        elif command[2] in self.assembler.localVars.keys():  # y is a local var
            t = self.assembler.localVars[command[2]]
        elif command[2] in self.assembler.registers:
            t = self.assembler.registers[command[2]]
        elif command[2] in self.assembler.DATA.keys():
            t = self.assembler.DATA[self.assembler.registers[command[2]]]
        elif command[2] in self.assembler.BSS.keys():
            t = self.assembler.BSS[self.assembler.registers[command[2]]]
        else:
            self.gui.outPut("No Idea what's going on there bud")
            self.gui.stopRunning(-1)
            return

        if command[1] in self.assembler.registers:
            result = self.assembler.registers[command[1]] & t
            if not inPlace: self.assembler.registers[command[1]] = result
        elif command[1] in self.assembler.BSS.keys():
            result = self.assembler.BSS[command[1]] & t
            if not inPlace: self.assembler.BSS[command[1]] = result
        elif command[1] in self.assembler.DATA.keys():
            result = self.assembler.DATA[command[1]] & t
            if not inPlace: self.assembler.DATA[command[1]] = result
        else:
            self.gui.outPut("There was a fatal error with "+command[0]+" on line "+str(i))
            self.gui.stopRunning(-1)
            return
		self.assembler.flags['C'] = 0

    def CALL(self, command, i):
        """name:CALL
		title:Call
		args:[label]
		description:Calls the function in the source operand. The current program counter value is pushed to the stack before the call.
		flags:,,,,,,,
        """
        if command[1] in self.assembler.lookupTable.keys():
            self.assembler.jumpLocation = self.assembler.lookupTable[command[1]]
            self.assembler.stackData.append(self.assembler.registers['PC'] + 1)
            self.gui.updateStack()
        else:
            self.gui.outPut("Big issue with this label guy.")

    def CBW(self, command, i):
        """name:CBW
		title:Convert Byte to Word
		args:None
		description:Extends the sign bit in AL throughout the AH register
		flags:,,,,,,,"""
        if self.assembler.eightBitRegister("AL") >= 128:
            self.assembler.registers['AX'] -= 256

    def CLC(self, command, i):
        """name:CLC
		title:Clear carry flag
		args:None
		description:Clears the carry flag to zero.
		flags:,,,,,,,0
		"""
        self.assembler.flags["C"] = False

    def CLD(self, command, i):
        """name:CLD
		title:Clear direction flag
		args:None
		description:Clears the Direction flag to zero. String primitive instructions will automatically increment SI and DI
		flags:,0,,,,,,"""
        self.assembler.flags['D'] = False

    def CLI(self, commmand, i):
        """name:CLI
		title:Clear Interrupt flag
		args:None
		description:Clears the interrupt flag to zero. This disables maskable hardware interrupts until an STI instruction is executed
		flags:,,0,,,,,"""
        self.assembler.flags['I'] = False

    def CMC(self, command, i):
        """name:CMC
		title:Complement Carry flag
		args:None
		description:Toggles the current value of the Carry flag
		flags:,,,,,,,*"""
        self.assembler.flags['C'] = not self.assembler.flags["C"]

    def CMPB(self, command, i):
        """name:CMPB
		title:Compare Byte
		args:[reg:mem],[reg:mem:immed]
		description:Compares the destination byte to the source byte by performing an implied subtraction of the source from the destination.
		flags:*,,,*,*,*,*,*"""
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
                        x = int(x, 16) % 255
                    except ValueError:
                        x = ord(x)
            elif type(x) != type(1):
                self.assembler.out("Illegal argument %s for CMPB on line %d. CMPB expects an argument to be a one byte register (ie: AH, AL, etc.), an integer, or a one byte string (ie: \"L\", etc.). Instead %s was given." % (x, i, x))
            b.append(x)

        self.SUB(["CMPB", str(b[0]), str(b[1])], i, inPlace=True)

    def DAA(self, command, i):
        """name:DAA
		title:Decimal adjust after addition
		args:None
		description:Adjusts the binary sum in AL after two packed BCD values have been added. Converts the sum to two BCD digits in AL.
		flags:?,,,*,*,*,*,*"""

        if (self.assembler.eightBitRegister('AL') & 15 > 9) or self.assembler.flags['A']:
            self.assembler.registers['AX'] += 6
            self.assembler.flags['A'] = 1
        else:
            self.assembler.flags['A'] = 0

        if self.assembler.eightBitRegister('AL') > 159 or self.assembler.flags['C']:
            self.assembler.registers['AX'] += 96
            self.assembler.flags['C'] = 1
        else:
            self.assembler.flags['C'] = 0

    def DAS(self, command, i):
        """name:DAS
		title:Decimal adjust after subtraction
		args:None
		description:Converts the binary result of a subtraction operation to two packed BCD digits in AL.
		flags:?,,,*,*,*,*,*"""

        if (self.assembler.eightBitRegister('AL') & 15 > 9) or self.assembler.flags['A']:
            self.assembler.registers['AX'] -= 6
            self.assembler.flags['A'] = 1
        else:
            self.assembler.flags['A'] = 0

        if self.assembler.eightBitRegister('AL') > 159 or self.assembler.flags['C']:
            self.assembler.registers['AX'] -= 96
            self.assembler.flags['C'] = 1
        else:
            self.assembler.flags['C'] = 0

    def JMP(self, command, i, referer="JMP"):
        """name:JMP
		title:Jump unconditionally to a label
		args: [label]
		description:The program counter is adjusted to the value referenced by the label and program execution continues.
		flags:,,,,,,,"""
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
            if command[1][-1] == "h":
                self.assembler.jumpLocation = int(command[1][:-1], 16)
            else:
                self.assembler.jumpLocation = int(command[1])
        else:
            self.gui.outPut("Error on line " + str(i) + ". The label " + command[1] + " is not defined for " + referer + "-ing to.")

    def LODSB(self, command, i):
        """name:LODSB
		title:Load accumulator from string
		args: None
		description: Loads a memory byte addressed by SI into AL.
		flags:,,,,,,,"""
        self.assembler.registers['AX'] = self.assembler.addressSpace[self.assembler.registers['SI']]

        self.assembler.registers['SI'] += -1 if self.assembler.flags['D'] else 1

    def LODSW(self, command, i):
        """name:LODSW
		title:Load accumulator from string
		args:None
		description: Loads a memory word addressed by SI into AX.
		flags:,,,,,,,"""
        self.assembler.registers['AX'] = self.assembler.addressSpace[self.assembler.registers['SI']] + self.assembler.addressSpace[self.assembler.registers['SI'] + 1] * 256

        self.assembler.registers['SI'] += -2 if self.assembler.flags['D'] else 2

    def LOOP(self, command, i, flag=True):
        """name:LOOP
		title: Loop
		args: [label]
		description: Decrements CX and jumps to the label if CX is greater than zero.
		flags:,,,,,,,"""
        if flag and self.assembler.registers["CX"] > 0:
            self.JMP(command, i, "LOOP")
            self.assembler.registers["CX"] -= 1

    def LOOPE(self, command, i):
        """name:LOOPE
		title:Loop if equal
		args:[label]
		description:Decrements CX and jumps to a label if CX>0 and the Zero flag is set.
		flags:,,,,,,,"""
        self.LOOP(command, i, self.assembler.flags['Z'])

    def LOOPNE(self, command, i):
        """name:LOOPNE
		title:Loop if not equal
		args:[label]
		description:Decrements CX and jumps to a label if CX>0 and the Zero flag is clear.
		flags:,,,,,,,"""
        self.LOOP(command, i, not self.assembler.flags['Z'])

    def LOOPNZ(self, command, i):
        """name:LOOPNZ
		title:Loop if not zero
		args:[label]
		description:Decrements CX and jumps to a label if CX>0 and the Zero flag is clear.
		flags:,,,,,,,"""
        self.LOOP(command, i, not self.assembler.flags['Z'])

    def LOOPZ(self, command, i):
        """name:LOOPZ
		title:Loop if zero
		args:[label]
		description:Decrements CX and jumps to a label if CX>0 and the Zero flag is set.
		flags:,,,,,,,"""
        self.LOOP(command, i, self.assembler.flags['Z'])

    def MOV(self, command, i):
        """name:MOV
		title:Move
		args:[reg:mem],[reg:mem:immed]
		description:Copies a byte or word from a source operand to a destination operand.
		flags:,,,,,,,"""

        if self.assembler.isHex(command[2]):  # B is digit
            if command[2][-1] == "h":
                b = int(command[2][:-1], 16)
            else:
                b = int(command[2])
        elif command[2] in self.assembler.localVars.keys():  # B is local var
            b = int(self.assembler.localVars[command[2]])
        elif command[2] in self.assembler.BSS.keys():  # B is BSS mem address
            b = int(self.assembler.BSS[command[2]][0])
        elif command[2] in self.assembler.DATA.keys():  # B is DATA mem address
            b = int(self.assembler.DATA[command[2]][0])
        elif len(command[2].strip("'").strip('"')) == 1:
            b = ord(command[2].strip("'").strip('"'))
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
            self.gui.outPut("MOV expects its first argument to be a memory address or register")

    def MOVSB(self, command, i):
        """name:MOVSB
		title:Move string
		args:None
		description:Copies a byte from memory addressed by SI to a memory addressed by DI. SI and DI are increased if the Direction flag is clear (0) and decreased if the Direction flag is set (1).
		flags:,,,,,,,"""
        self.assembler.addressSpace[self.assembler.registers['DI']] = self.assembler.addressSpace[self.assembler.registers['SI']]
        self.assembler.registers['SI'] += -1 if self.assembler.flags['D'] else 1


    def MOVSW(self, command, i):
        """name:MOVSW
		title:Move string
		args:None
		description:Copies a word from memory addressed by SI to a memory addressed by DI. SI and DI are increased if the Direction flag is clear (0) and decreased if the Direction flag is set (1).
		flags:,,,,,,,"""
        self.assembler.addressSpace[self.assembler.registers['DI']] = self.assembler.addressSpace[self.assembler.registers['SI']]
        self.assembler.addressSpace[self.assembler.registers['DI'] + 1] = self.assembler.addressSpace[self.assembler.registers['SI'] + 1]
        self.assembler.registers['SI'] += -2 if self.assembler.flags['D'] else 2

    def NEG(self, command, i):
        """"""name:NEG
		title:Negate
		args:[reg]
		description:Calculates the twos complement of the argument in place.
		flags:*,,,*,*,*,*,*""""""
        if command[1] in self.assembler.registers.keys():
            self.assembler.registers[command[1]] *= -1

    def NOT(self, command, i):
        """name:NOT
		title:Logical Not
		args:[reg:mem]
		description:Performs a logical not on an operand by reversing each of its bits.
		flags:,,,,,,,"""
        if command[1] in self.assembler.registers:
            self.assembler.registers[command[1]] = ~self.assembler.registers[command[1]]
        elif command[1] in self.assembler.BSS.keys():
            self.assembler.BSS[command[1]] = ~self.assembler.BSS[command[1]]
        elif command[1] in self.assembler.DATA.keys():
            self.assembler.DATA[command[1]] = ~self.assembler.DATA[command[1]]

    def OR(self, command, i):
        """name:OR
		title:Inclusive Or
		args:[reg:mem],[reg:mem:immed]
		description:Performs a logical OR between each bit in the destination operand and each bit in the source operand. If either bit is a 1 in each position, the result bit is a 1.
		flags:0,,,*,*,?,*,0"""

        if self.assembler.isHex(command[2]):  # y is a digit
            if command[2][-1] == "h":
                t = int(command[2][:-1], 16)
            else:
                t = int(command[2])
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
		
		self.assembler.flags['O'] = 0
		self.assembler.flags['C'] = 0

    def POP(self, command, i):
        """name:POP
		title:Pop from stack
		args:[reg:mem]
		description:Copies a word at the current stack pointer location into the destination operand, and adds 2 to the SP.
		flags:,,,,,,,"""
        if command[1] in self.assembler.registers:
            self.assembler.registers[command[1]] = int(self.assembler.stackData.pop())
            self.assembler.registers['SP'] += 2
            self.gui.updateStack()

    def POPF(self, command, i):
        """name:POPF
		title:Pop flags from stack
		args:None
		description:POPF pops the top of the stack into the 16-bit Flags register.
		flags:*,*,*,*,*,*,*,*"""
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
        """name:PUSH
		title:Push on stack
		args:[reg:mem:immed]
		description:Subtracts 2 from SP and copies the source operand into the stack location pointed to by SP.
		flags:,,,,,,,"""
        if self.assembler.isHex(command[1]):  # PUSHing a number to the stack, it's prolly hex so ignore the A-F chars
            if command[1][-1] == "h":
                self.assembler.stackData.append(int(command[1][:-1], 16))
            else:
                self.assembler.stackData.append(int(command[1]))
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
        """name:PUSHF
		title:Push flags onto the stack
		args:None
		description:PUSHF pushes the Flags register onto the stack.
		flags:,,,,,,,"""
        flags = self.assembler.flags['S'] * (128) + self.assembler.flags['Z'] * (64) + self.assembler.flags['A'] * (16) + self.assembler.flags['P'] * (4) + self.assembler.flags['C']
        self.assembler.stackData.append(flags)
        self.assembler.registers['SP'] -= 2
        self.gui.updateStack()

    def RCL(self, command, i):
        """name:RCL
		title:Rotate carry left
		args:[reg]
		description:Rotates the destionation operand left. The carry flag is copied into the lowest bit, and the highest bit is copied into the Carry flag
		flags:*,,,,,,,*"""
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
        """name:RCR
		title:Rotates carry right
		args:[reg]
		description:Rotates the destination operand right, using the source operand to determine the number of rotations. The carry flag is copied into the highest bit, and the lowest bit is copied into the Carry flag.
		flags:*,,,,,,,*"""
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
        """name:REP
		title:Repeating string primitive command
		args: [MOVS:MOVSB:CMPS:CMPSB:CMPSW:SCAS:SCASB:SCASW:STOS:STOSB:STOSW:LODS:LODSB:LODSW]
		description:Repeats a string primitive instruction, using CX as a counter. CX is decremented each time the instruction is repeated, until CX = 0. EG REP MOVSB
		flags:,,,,,,,"""
        if command[1] in ["MOVS", "MOVSB", "CMPS", "CMPSB", "CMPSW", "SCAS", "SCASB", "SCASW", "STOS", "STOSB", "STOSW", "LODS", "LODSB", "LODSW"]:
            while self.assembler.registers['CX'] > 0:
                self.getFunctionTable()[command[1:], i]
                self.assembler.registers['CX'] -= 1
        else:
            self.gui.outPut("Innapropriate command used with REP")
            self.gui.stopRunning(-1)

    def REPE(self, command, i):
        """name:REPE
		title:Repeating string primitive command if equal
		args: [MOVS:MOVSB:CMPS:CMPSB:CMPSW:SCAS:SCASB:SCASW:STOS:STOSB:STOSW:LODS:LODSB:LODSW]
		description:Repeats a string primitive instruction, using CX as a counter. CX is decremented each time the instruction is repeated, until CX = 0 while the zero flag is set. EG REP MOVSB
		flags:,,,,*,,,"""
        if command[1] in ["CMPS", "CMPSB", "CMPSW", "SCAS", "SCASB", "SCASW"]:
            while self.assembler.flags["Z"] and self.assembler.registers['CX'] > 0:
                self.getFunctionTable()[command[1:], i]
                self.assembler.registers['CX'] -= 1
        else:
            self.gui.outPut("Innapropriate command used with " + command[0])
            self.gui.stopRunning(-1)

    def REPNE(self, command, i):
        """name:REPNE
		title:Repeating string primitive command if not equal
		args: [MOVS:MOVSB:CMPS:CMPSB:CMPSW:SCAS:SCASB:SCASW:STOS:STOSB:STOSW:LODS:LODSB:LODSW]
		description:Repeats a string primitive instruction, using CX as a counter. CX is decremented each time the instruction is repeated, until CX = 0 while the zero flag is clear. EG REP MOVSB
		flags:,,,,*,,,"""
        if command[1] in ["CMPS", "CMPSB", "CMPSW", "SCAS", "SCASB", "SCASW"]:
            while not self.assembler.flags["Z"] and self.assembler.registers['CX'] > 0:
                self.getFunctionTable()[command[1:], i]
                self.assembler.registers['CX'] -= 1
        else:
            self.gui.outPut("Innapropriate command used with " + command[0])
            self.gui.stopRunning(-1)

    def REPNZ(self, command, i):
        """name:REPNZ
		title:Repeating string primitive command if not zero
		args: [MOVS:MOVSB:CMPS:CMPSB:CMPSW:SCAS:SCASB:SCASW:STOS:STOSB:STOSW:LODS:LODSB:LODSW]
		description:Repeats a string primitive instruction, using CX as a counter. CX is decremented each time the instruction is repeated, until CX = 0 while the zero flag is clear. EG REP MOVSB
		flags:,,,,*,,,"""
        self.REPNE(command, i)

    def REPZ(self, command, i):
        """name:REPZ
		title:Repeating string primitive command if zero
		args: [MOVS:MOVSB:CMPS:CMPSB:CMPSW:SCAS:SCASB:SCASW:STOS:STOSB:STOSW:LODS:LODSB:LODSW]
		description:Repeats a string primitive instruction, using CX as a counter. CX is decremented each time the instruction is repeated, until CX = 0 while the zero flag is set. EG REP MOVSB
		flags:,,,,*,,,"""
        self.REPE(command, i)

    def RET(self, command, i):
        """name:RET
		title:Return from procedure
		args:[None:immed]
		description:Pop a return address from the stack. An optional argument tells the CPU to add a value to SP after popping the return address.
		flags:,,,,,,,"""
        if len(self.assembler.stackData) == 0:
            self.gui.outPut("Fatal Error: The stack is empty and RET was called, there was no address to return to!")
            self.gui.stopRunning(-1)
        elif self.assembler.codeBounds[0] <= self.assembler.stackData[-1] <= self.assembler.codeBounds[1]:
            self.assembler.jumpLocation = self.assembler.stackData.pop()
			ADD(self.assembler.registers['SP'],self.command[1],i,inPlace=False)
            self.gui.updateStack()
        else:
            self.gui.outPut("Returning on a suspect address.")
            print self.assembler.codeBounds[0]
            print self.assembler.stackData[-1]
            print self.assembler.codeBounds[1]
            self.gui.stopRunning(-1)

    def ROL(self, command, i):
        """name:ROL
		title:Rotate left
		args:[reg]
		description:Rotates the destination operand left. The highest bit is copied into the Carry flag and moved into the loewst bit position.
		flags:*,,,,,,,*"""
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
        """name:ROR
		title:Rotate right
		args:[reg]
		description:Rotates the destination operand right. The lowest bit is copied into both the Carry flag and the highest bit position.
		flags:*,,,,,,,*"""
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
        """name:SAHF
		title:Store AH into flags
		args:None
		description:Copies AH into bits 0 through 7 of the Flags register. The Trap, Interrupt, DIrection, and Overflow flags are not affected.
		flags:,,,*,*,*,*,*"""
        flags = self.assembler.eightBitRegister('AH')
        for f in ['C', 'P', 'A', 'Z', 'S', 'I', 'D', 'O']:
            self.assembler.flags[f] = self.flags % 2
            flags /= 2
        self.gui.updateStack()

    def SAL(self, command, i):
        """name:SAL
		title:Shift arithmetic left
		args:[reg]
		description:Identical to SHL, only included in the instruction set for completeness.
		flags:*,,,*,*,?,*,*"""
        self.SHL(self, command, i)

    def SAR(self, command, i):
        """name:SAR
		title:Shift arithmetic right
		args:[reg]
		description:Shifts each bit in the destination operand to the right. THe lowest bit is copied into the Carry flag, and the highest bit retains its previous value. This hift is often used with signed operands, because it preserves the number's sign.
		flags:*,,,*,*,?,*,*"""
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
            self.gui.outPut("SAR expects its argument to be a register.")
            self.gui.stopRunning(-1)
            return

    def SBB(self, command, i):
        """name:SBB
		title:Subtract with borrow
		args:[reg:mem],[reg:mem:immed]
		description:Subtracts the source operand from the destination operand and then subtracts the Carry flag from the destination.
		flags:*,,,*,*,*,*,*"""
        self.ADD(command, i, carry=True)

    def SCASB(self, command, i):
        """name:SCASB
		title:Scan string
		args:None
		description:Scans a string in memory pointed to by DI for a value that matches AL. DI is increased if the Direction flag is clear (0) and decreased if the Direction flag is set (1).
		flags:*,,,*,*,*,*,*"""
        self.SUB(['SCASB', str(self.assembler.eightBitRegister('AL')), str(self.assembler.addressSpace[self.assembler.registers['DI']])], i, inPlace=True)
        self.assembler.registers['DI'] += -1 if self.assembler.flags['D'] else 1

    def SCASW(self, command, i):
        """name:SCASW
		title:Scan string
		args:None
		description:Scans a string in memory pointed to by DI for a value that matches AX. DI is increased if the Direction flag is clear (0) and decreased if the Direction flag is set (1).
		flags:,,,,,,,"""
        self.SUB(['SCASW', str(self.assembler.registers['AX']), str(self.assembler.addressSpace[self.assembler.registers['DI'] + 1] + 256 * self.assembler.addressSpace[self.assembler.registers['DI']])], i, inPlace=True)
        self.assembler.registers['DI'] += -2 if self.assembler.flags['D'] else 2

    def SHL(self, command, i):
        """name:SHL
		title:Shift left
		args:[reg]
		description:Shifts each bit in the destination operand to the left. The highest bit is copied into the Carry flag and the lowest bit is filled with a zero.
		flags:*,,,*,*,?,*,*"""

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
        """name:SHR
		title:Shift right
		args:None
		description:SHifts each bit in the destination operand to the right. The highest bit is filled with a zero, and the lowest bit is copied into the Carry flag.
		flags:*,,,*,*,?,*,*"""

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
        """name:STC
		title:Set the Carry flag
		args:None
		description:Sets the Carry flag to 1
		flags:,,,,,,,1"""
        self.assembler.flags["C"] = True

    def STD(self, command, i):
        """name:STD
		title:Set the Direction flag
		args:None
		description:Sets the Direction flag to 1
		flags:,1,,,,,,"""
        self.assembler.flags["D"] = True

    def STI(self, command, i):
        """name:STI
		title:Sets the Interrupt flag
		args:None
		description:Sets the Interrupt flag to 1
		flags:,,1,,,,,"""
        self.assembler.flags["I"] = True

    def STOSB(self, command, i):
        """name:STOSB
		title:Store string data
		args:None
		description:Stores the value of AL in the memory location addressed by DI. DI is increased if the Direction flag is clear (0), and decreased if the Direction flag is set (1).
		flags:,,,,,,,"""
        self.assembler.addressSpace[self.assembler.registers["DI"]] = chr(self.assembler.eightBitRegister("AL"))
        self.assembler.registers["DI"] += -1 if self.assembler.flags['D'] else 1

    def STOSW(self, command, i):
        """name:STOSW
		title:Store string data
		args:None
		description:Stores the value of AX in the memory location addressed by DI. DI is increased if the Direction flag is clear (0), and decreased if the Direction flag is set (1).
		flags:,,,,,,,"""
        self.assembler.addressSpace[self.assembler.registers["DI"]] = chr(self.assembler.eightBitRegister("AH"))
        self.assembler.addressSpace[self.assembler.registers["DI"] + 1] = chr(self.assembler.eightBitRegister("AL"))
        self.assembler.registers["DI"] += -2 if self.assembler.flags['D'] else 2

    def SUB(self, command, i, inPlace=False):
        """name:SUB
		title:Subtract
		args:[reg:mem],[reg:mem:immed]
		description:Subtracts the source opearand from the destination operand.
		flags:*,,,*,*,*,*,*"""
        self.ADD(command, i, inPlace=inPlace)

    def SYS(self, command, i):
        """name:SYS
		title:System trap
		args:None
		description:Calls a system trap: evaluates based on the last piece of data on the stack
		flags:,,,,,,,"""
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

    def TEST(self, command, i):
        """name:TEST
		title:Test
		args:[reg:mem],[reg:mem:immed]
		description:Tests individual bits in the destination operand against those in the source operand. Performs a logial AND operation that affects the flags but not the destination operand.
		flags:0,,,*,*,?,*,0"""
        self.AND(command, i, inPlace=True)

    def XCHG(self, command, i):
        """name:XCHG
		title:Exchange
		args:[reg],[reg]
		description:Exchanges the contents of the source and destination operands
		flags:,,,,,,,"""
        if command[1] in self.assembler.registers and command[2] in self.assembler.registers:
            self.assembler.registers[command[1]], self.assembler.registers[command[2]] = self.assembler.registers[command[2]], self.assembler.registers[command[1]]
        else:
            self.gui.outPut("Error on line " + str(i) + ". XCHG expects both its arguments to be registers.")

    def XOR(self, command, i):
        """name:XOR
		title:Exclusive OR
		args:[reg:mem],[reg:mem:immed]
		description:Each bit in the source operand is exclusive ORed with its corresponding bit in the destination. The destination bit is a 1 only when the original source and destination bits are different.
		flags:0,,,*,*,?,*,0"""

        if self.assembler.isHex(command[2]):  # y is a digit
            if command[2][-1] == "h":
                t = int(command[2][:-1], 16)
            else:
                t = int(command[2])
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

		self.assembler.flags['O'] = 0
		self.assembler.flags['C'] = 0
		
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

"""   10 more to go
"CMP":2,  # Compare operands
"CMPSB":-1,  # Compare bytes in memory
"CMPSW":-1,  # Compare words in memory
"DIV":2,  # Unsigned divide 
"IDIV":1,  # Signed divide
"IMUL":1,  # Signed multiply
"LDS":2,  # Load pointer using DS
"LEA":2,  # Load effective address
"LES":2,  # Load ES with pointer
"MUL":2,  # Unsigned Multiply
"""
