'''
Created on 2013-10-20

@author: Brydon
'''

sysCodes = {"_EXIT":1, "_PRINTF":127, "_GETCHAR":117, "_SSCANF":125, "_READ":3, "_OPEN":5, "_CLOSE":6}

def newAssembler(A):
    """ Link's this module with the assembler instance """
    global assembler
    assembler = A

def getRegisters():
    """ 8088 registers (minus the flag register) """
    return {"AX":0, "BX":0, "CX":0, "DX":0, "SP":0, "BP":0, "SI":0, "DI":0, "PC":0}

def getFlags():
    """ 8088 flag registers """
    """Z: zero flag, S: sign flag, O: overflow flag, C: carry flag, A: auxillary flag, P: parity flag, D: direction flag, I: interrupt flag"""
    return {"Z":False, "S":False, "O":False, "C":False, "A":False, "P":False, "D":False, "I":False}

def getCommandArgs():
    """ A dict whose keys are commands and their values are the # of arguments they expect """
    return {"AAA":-1,  # Ascii adjust AL after addition
            "AAD":-1,  # Ascii adjust AX before division
            "AAM":-1,  # Ascii adjust AX after multiplication
            "AAS":-1,  # Ascii adjust AL after subtraction
            "ADC":-1,  # Add with carry
            "ADD":2,  # Add
            "AND":2,  # Logical and
            "CALL":1,  # Call procedure
            "CBW":-1,  # Convert byte to word
            "CLC":0,  # Clear carry flag
            "CLD":0,  # Clear direction flag
            "CLI":0,  # Clear interrupt flag
            "CMC":0,  # Coplement carry flag
            "CMP":2,  # Compare operands
            "CMPB":2,
            "CMPSB":-1,  # Compare bytes in memory
            "CMPSW":-1,  # Compare words in memory
            "CWD":-1,  # Convert word to doubleword
            "DAA":-1,  # Decimal adjust AL after addition
            "DAS":-1,  # Decimal adjust AL after subtraction
            "DEC":1,  # Decrement by 1
            "DIV":2,  # Unsigned divide
            "HLT":-1,  # Enter halt state
            "IDIV":-1,  # Signed divide
            "IMUL":-1,  # Signed multiply
            "IN":-1,  # Input from port
            "INC":1,  # Increment by 1
            "INT":-1,  # Call to interrupt
            "INTO":-1,  # Call to interrupt if overflow
            "IRET":-1,  # Return from interrupt
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
            "LAHF":-1,  # Load flags into AH register
            "LDS":-1,  # Load pointer using DS
            "LEA":-1,  # Load effective address
            "LES":-1,  # Load ES with pointer
            "LODSB":-1,  # Load string byte
            "LODSW":-1,  # Load string word
            "LOOP":1,  # Loop control
            "LOOPE":1,  # Loop if equal
            "LOOPNE":1,  # Loop if not equal
            "LOOPNZ":1,  # Loop if not zero
            "LOOPZ":1,  # Loop if zero
            "MOV":2,  # Move
            "MOVSB":-1,  # Move byte from string to string
            "MOVSW":-1,  # Move word from string to string
            "MUL":-1,  # Unsigned Multiply
            "NEG":1,  # Two's complement negation
            "NOP":0,  # No Operation.
            "NOT":-1,  # Negate the opearand, logical NOT
            "OR":-1,  # Logical OR
            "OUT":-1,  # Output to port
            "POP":1,  # Pop data from stack
            "POPF":1,  # Pop data from flags register
            "PUSH":1,  # Push data to stacscreek
            "PUSHF":-1,  # Push flags onto stack
            "RCL":-1,  # Rotate left with carry
            "RCR":-1,  # Rotate right with carry
            "REP":-1,  # Repeat MOVS/STOS/CMPS/LODS/SCAS
            "REPE":-1,  # Repeat if equal
            "REPNE":-1,  # Repeat if not equal
            "REPNZ":-1,  # Repeat if not zero
            "REPZ":-1,  # Repeat if zero
            "RET":0,  # Return from procedure
            "ROL":-1,  # Rotate left
            "ROR":-1,  # Rotate right
            "SAHF":-1,  # Store AH into flags
            "SAL":-1,  # Shift Arithmetically Left
            "SAR":-1,  # Shift Arithmetically Right
            "SBB":-1,  # Subtraction with borrow
            "SCASB":-1,  # Compare byte string
            "SCASW":-1,  # Compare word string
            "SHL":-1,  # unsigned Shift left
            "SHR":-1,  # unsigned Shift right
            "STC":0,  # Set carry flag
            "STD":0,  # Set direction flag
            "STI":0,  # Set interrupt flag
            "STOSB":0,  # Store byte in string
            "STOSW":0,  # Store word in string
            "SUB":-1,  # Subtraction
            "SYS":0,  # System trap
            "TEST":-1,  # Logical compare (AND)
            "XCHG":2,  # Exchange data
            "XLAT":-1,  # Table look-up translation ?
            "XOR":-1  # Logical XOR
            }

def getFunctionTable():
    """ The jump table - the keys are commands and values are the functions that need called, i use anonymous lambda fnxns for argument passing """
    return {
            """
            "JNA":1,  # Jump if not above
            "JNAE":1,  # Jump if not above or equal
            "JNB":1,  # Jump if not below
            "JNBE":1,  # Jump if not below or equal
            "JNP":1,  # Jump if not ???
            "JNS":1,  # Jump if not ???
            "JP":1,  # Jump if ???
            "JPE":1,  # Jump if ???
            "JPO":1,  # Jump if ???
            "JS":1,  # Jump if ???
            """
            "ADD":lambda x, i: add(x, i),
            "PUSH":lambda x, i: push(x, i),
            "PUSHF":lambda x, i: pushf(x, i),
            "JMP":lambda x, i: jmp(x, i),
            "JC":lambda x, i: jf(x, i, assembler.flags['C'] == 1),
            "JCXZ":lambda x, i: jf(x, i, assembler.registers['CX'] == 0),
            "JE":lambda x, i: jf(x, i, assembler.flags['Z'] == 1),
            "JG":lambda x, i: jf(x, i, assembler.flags['S'] == 0 and assembler.flags['Z'] == 0),
            "JGE":lambda x, i: jf(x, i, assembler.flags['S'] == 0 or assembler.flags['Z'] == 1),
            "JL":lambda x, i: jf(x, i, assembler.flags['S'] == 1 and assembler.flags['Z'] == 0),
            "JLE":lambda x, i: jf(x, i, assembler.flags['S'] == 1 or assembler.flags['Z'] == 1),
            "JNC":lambda x, i: jf(x, i, assembler.flags['C'] == 0),
            "JNE":lambda x, i: jf(x, i, assembler.flags['Z'] == 0),
            "JNG":lambda x, i: jf(x, i, assembler.flags['S'] == 1 or assembler.flags['Z'] == 1),
            "JNGE":lambda x, i: jf(x, i, assembler.flags['S'] == 1 and assembler.flags['Z'] == 0),
            "JNLE":lambda x, i: jf(x, i, assembler.flags['S'] == 0 and assembler.flags['Z'] == 0),
            "JNL":lambda x, i: jf(x, i, assembler.flags['S'] == 0 or assembler.flags['Z'] == 1),
            "JNO":lambda x, i: jf(x, i, assembler.flags["O"] == 0),
            "JNP":lambda x, i: jf(x, i, assembler.flags['P'] == 0),
            "JNZ":lambda x, i: jf(x, i, assembler.flags['Z'] == 0),
            "JO":lambda x, i: jf(x, i, assembler.flags['O'] == 1),
            "JP":lambda x, i: jf(x, i, assembler.flags['P'] == 1),
            "JZ":lambda x, i: jf(x, i, assembler.flags['Z'] == 1),
            "LOOP":lambda x, i: loop(x, i),
            "LOOPE":lambda x, i: loop(x, i, assembler.flags["Z"]),
            "LOOPNE":lambda x, i: loop(x, i, not assembler.flags["Z"]),
            "LOOPNZ":lambda x, i: loop(x, i, not assembler.flags["Z"]),
            "LOOPZ":lambda x, i: loop(x, i, assembler.flags["Z"]),
            "MOV":lambda x, i: mov(x, i),
            "NOP":lambda x, i: 1 + 1,  # best instruction
            "SYS":lambda x, i: sys(x, i),
            "CLC":lambda x, i: clc(x, i),
            "STC":lambda x, i: stc(x, i),
            "POP":lambda x, i: pop(x, i),
            "STOSB":lambda x, i: stosb(x, i),
            "CMPB":lambda x, i: cmpb(x, i),
            "INC":lambda x, i: incdec(x, i, 1),
            "DEC":lambda x, i: incdec(x, i, -1),
            "XCHG":lambda x, i: xchg(x, i)
            }

def add(command, i):
    """ add x,y translates to x = x + y
    where x is a register or mem address, y is a number, localvar, mem address, or register. """
    if command[1] == "SP" and command[2].isdigit():  # TODO: REPLACE THIS
        for j in range(int(command[2]) / 2):
            if len(assembler.stackData) > 0:
                assembler.stackData.pop()
                assembler.updateStack()
    if command[1].isdigit():
        assembler.outPut("Error on line " + str(i) + ". Add cannot have a numerical first argument.")
        assembler.stopRunning(-1)
        return
    """ To save on code space, y will serve as "second guy" """
    if command[2].strip("abcdef").isdigit():  # y is a digit
        y = int(command[2], 16)
    elif command[2] in assembler.localVars.keys():  # y is a local var
        y = int(assembler.localVars[command[2]])
    elif command[2] in assembler.registers.keys():  # y is a register
        y = assembler.registers[command[2]]
    elif command[2] in assembler.DATA.keys():  # y is a mem address from DATA section
        y = assembler.addresSpace[assembler.DATA[command[2]][0]]
    elif command[2] in assembler.BSS.keys():  # y is a mem address from BSS section
        y = assembler.addresSpace[assembler.BSS[command[2]][0]]

    if command[1] in assembler.registers.keys():  # x is a register
        assembler.registers[command[1]] += y
        result = assembler.registers[command[1]]
    elif command[1] in assembler.DATA.keys():  # x is a data location
        assembler.addresSpace[assembler.DATA[command[1]][0]] += y
        result = assembler.addresSpace[assembler.DATA[command[1]][0]]
    elif command[1] in assembler.BSS.keys():  # x is a BSS location
        assembler.addresSpace[assembler.BSS[command[1]][0]] += y
        result = assembler.addresSpace[assembler.BSS[command[1]][0]]

    if result == 0:
        assembler.flags['Z'] = 1
    elif result < 0:
        assembler.flags['S'] = 1

def clc(command, i):
    """ set the carry flag to false """
    assembler.flags["C"] = False

def cld(command, i):
    """ set the direction flag to false """
    assembler.flags['D'] = False

def cli(commmand, i):
    """ set the interrupt flag to false """
    assembler.flags['I'] = False

def cmc(command, i):
    """ Complements the carry flag, toggling it """
    assembler.flags['C'] = not assembler.flags["C"]

def cmpb(command, i):
    """ cmpb x,y where x and y are bytes, if equal set the zero flag accordingly """
    a = command[1:3]
    b = []
    for x in a:
        if x in ['AH', 'AL', 'BH', 'BL', 'CH', 'CL', 'DH', 'DL']:
            x = assembler.eightBitRegister(x)
        elif x in ['AX', 'BX', 'CX', 'DX']:
            assembler.outPut("Illegal argument for cmpb on line %d. %s is a 16 bit register, perhaps you meant one of the 8 bit %s or %s registers?" % (i, x, x[0] + "H", x[0] + "L"))
            assembler.stopRunning(-1)
            return
        elif type(x) == type(""):
            x = assembler.replaceEscapedSequences(x.rstrip("'\"").lstrip("'\""))

            if len(x) != 1:
                assembler.outPut("Illegal argument %s for cmpb on line %d. cmpb expects all strings to be ONE byte in length." % (x, i))
                assembler.stopRunning(-1)
                return
            else:
                try:
                    x = int(x)
                except ValueError:
                    x = ord(x)
        elif type(x) != type(1):
            assembler.out("Illegal argument %s for cmpb on line %d. cmpb expects an argument to be a one byte register (ie: AH, AL, etc.), an integer, or a one byte string (ie: \"L\", etc.). Instead %s was given." % (x, i, x))
        b.append(x)

    assembler.flags["Z"] = b[0] == b[1]

def incdec(command, i, p):
    """ A function for incrementing or decermenting a register.  p is the polarity (-1 for dec, 1 for inc) """
    if command[1] in getRegisters().keys():
        assembler.registers[command[1]] += p;
    elif command[1] in assembler.BSS.keys():
        assembler.addressSpace[assembler.BSS[command[1]][0]] += p
    elif command[1] in assembler.DATA.keys():
        assembler.addressSpace[assembler.DATA[command[1]][0]] += p
    else:
        assembler.outPut("Invalid " + ("inc" if p == 1 else "dec") + " on line " + str(i) + ". " + ("inc" if p == 1 else "dec") + " expects its argument to be either a register or memory address.")

def jf(command, i, flag):
    """ jmp if the flag is true, used for jo, jg, jge, etc. """
    if flag:
        jmp(command, i)

def jmp(command, i, referer="jmp"):
    """ jmp x jumps to position x in the program """
    if command[1] in assembler.lookupTable.keys():
        if type(assembler.lookupTable[command[1]]) == assembler.LIST_TYPE:
            # Jumps where many are declared, gotta jump up or down, bit complicated. ie, jmp 1f
            1 + 1
        else:
            assembler.jumpLocation = assembler.lookupTable[command[1]]
    else:
        assembler.outPut("Error on line " + str(i) + ". The label " + command[1] + " is not defined for " + referer + "-ing to.")

def loop(command, i, flag=True):
    """ Decrements CX and jumps to a label if CX is greater than zero and flag is true. """
    assembler.registers["CX"] -= 1
    if flag and assembler.registers["CX"] > 0:
        jmp(command, i, "loop")

def mov(command, i):
    """ Mov A,B  evaluates as A=B where A is a register or memory address and B is a memory,
        register address, local variable, or number. """

    if command[2].strip("abcdef").isdigit():  # B is digit
        b = int(command[2], 16)
    elif command[2] in assembler.localVars.keys():  # B is local var
        b = int(assembler.localVars[command[2]])
    elif command[2] in assembler.BSS.keys():  # B is BSS mem address
        b = int(assembler.BSS[command[2]][0])
    elif command[2] in assembler.DATA.keys():  # B is DATA mem address
        b = int(assembler.DATA[command[2]][0])

    if command[1] in assembler.registers.keys():
        assembler.registers[command[1]] = b
    elif command[1] in assembler.DATA.keys():
        assembler.addressSpace[assembler.DATA[command[1]][0]] = b
    elif command[1] in assembler.BSS.keys():
        assembler.addressSpace[assembler.BSS[command[1]][0]] = b
    elif command[1].strip("abcdef").isdigit():
        assembler.outPut("Error, you made your first argument a hex digit. MOV expects its first argument to be a register, or a memory address.")
    else:
        assembler.outPut("MOV expects its first argument to be a memory address or register, and second to be a memory address, register, immediate value, or local variable.")

def neg(command, i):
    """ Performs twos complement of the destination operand, and stores the result in the destination."""
    if command[1] in assembler.registers.keys():
        assembler.registers[command[1]] *= -1

def pop(command, i):
    """ pop x will pop an element from the stack into register x """
    if command[1] in getRegisters():
        assembler.registers[command[1]] = int(assembler.stackData.pop())
        assembler.updateStack()

def push(command, i):
    """ Push x will push the argument x to the stack """
    if command[1].strip("abcdef").isdigit():  # pushing a number to the stack, it's prolly hex so ignore the A-F chars
        assembler.stackData.append(int(command[1], 16))
        assembler.updateStack()
    elif command[1] in getRegisters():
        assembler.stackData.append(int(assembler.registers[command[1]]))
        assembler.updateStack()
    elif command[1] in assembler.DATA.keys():  # pushing a string from .SECT .DATA to the stack
        assembler.stackData.append(assembler.DATA[command[1]][0])
        assembler.updateStack()
    elif command[1] in assembler.localVars.keys():  # pushing a local int to the stack
        assembler.stackData.append(assembler.localVars[command[1]])
        assembler.updateStack()
    elif command[1] in assembler.BSS.keys():
        assembler.stackData.append(assembler.BSS[command[1]][0])
        assembler.updateStack()
    elif "(" in command[1] and ")" in command[1]:
        temp = command[1][command[1].find("(") + 1:command[1].find(")")]
        if temp in assembler.BSS.keys():
            # TODO: memory
            1 + 1
        else:
            assembler.outPut("Error on line " + str(i) + ". I don't understand what (" + temp + ") is")
            assembler.stopRunning(-1)
    else:
        print(command)
        assembler.outPut("Unknown error on line " + str(i) + ".")
        assembler.stopRunning(-1)

def pushf(command, i):
    """ Push the flags to the stack """

def stosb(command, i):
    """ Stores contents of AX in the memory address contained in DI, then increments DI """
    assembler.addressSpace[assembler.registers["DI"]] = chr(assembler.registers["AX"])
    assembler.registers["DI"] += 1

def stc(command, i):
    """ set the carry flag to true """
    assembler.flags["C"] = True

def std(command, i):
    """ Set the direction flag to true """
    assembler.flags["D"] = True

def sti(command, i):
    """ Set the interrupt flag to true """
    assembler.flags["I"] = True

def sys(command, i):
    """ Call a system trap - evaluates based on the last piece of data on the stack """
    if len(assembler.stackData) == 0:
        assembler.outPut("Invalid system trap: SYS called on line %d without any arguments on stack." % i)
        assembler.stopRunning(-1)
    elif not int(assembler.stackData[-1]) in sysCodes.values():
        assembler.outPut("Invalid system trap on line %d: The first argument \"%s\" on the stack is not understood" % (i, assembler.stackData[-1]))
        assembler.stopRunning(-1)
    else:
        if int(assembler.stackData[-1]) == sysCodes["_EXIT"]:
            assembler.stopRunning()
        elif int(assembler.stackData[-1]) == sysCodes["_GETCHAR"]:
            assembler.getChar()
        elif int(assembler.stackData[-1]) == sysCodes["_OPEN"]:
            1 + 1
        elif int(assembler.stackData[-1]) == sysCodes["_PRINTF"]:
            try:
                i = 2
                args = []
                while True:
                    if assembler.addressSpace.count("0") == 0:
                        formatStr = "".join(assembler.addressSpace[int(assembler.stackData[-i]):])
                    else:
                        formatStr = "".join(assembler.addressSpace[int(assembler.stackData[-i]):assembler.addressSpace.index("0", int(assembler.stackData[-i]))])
                    i += 1
                    print formatStr
                    numArgs = formatStr.count("%") - formatStr.count("\\%")
                    if numArgs == len(args): break
                    if numArgs != 0: continue
                    args.append(formatStr)
                assembler.outPut(formatStr % tuple(args))
            except IndexError:
                assembler.stopRunning(-1)
                assembler.outPut("Invalid system trap on line %d. Invalid number of arguments with _PRINTF." % i)

def xchg(command, i):
    """ xchg, swaps two registers contents """
    if command[1] in assembler.registers and command[2] in assembler.registers:
        assembler.registers[command[1]], assembler.registers[command[2]] = assembler.registers[command[2]], assembler.registers[command[1]]
    else:
        assembler.outPut("Error on line " + str(i) + ". XCHG expects both its arguments to be registers.")
