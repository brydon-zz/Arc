'''
Created on 2013-11-20

@author: beewhy
'''
def newAssembler(A):
    global assembler
    assembler = A

def getRegisters():
    return {"AX":0, "BX":0, "CX":0, "DX":0, "SP":0, "BP":0, "SI":0, "DI":0, "PC":0}

def getFlags():
    return {"Z":False, "S":False, "V":False, "C":False, "A":False, "P":False}

def getCommandArgs():
    return {"ADD":2,
            "PUSH":1,
            "JMP":1,
            "JE":1,
            "JG":1,
            "JL":1,
            "JLE":1,
            "JGE":1,
            "MOV":2,
            "SYS":0,
            "POP":1,
            "CMPB":2,
            "STOSB":0
            }

def getFunctionTable():
    return {
            "ADD":lambda x, i: add(x, i),
            "PUSH":lambda x, i: push(x, i),
            "JMP":lambda x, i: jmp(x, i),
            "MOV":lambda x, i: mov(x, i),
            "JE":lambda x, i: je(x, i),
            "JG":lambda x, i: jg(x, i),
            "JL":lambda x, i: jl(x, i),
            "JLE":lambda x, i: jle(x, i),
            "JGE":lambda x, i: jge(x, i)
            }

def add(command, i):
    if command[1] == "SP" and command[2].isdigit():
        for j in range(int(command[2]) / 2):
            if len(assembler.stackData) > 0:
                assembler.stackData.pop()
                assembler.stackPush("")
    elif command[1].isdigit():
        print "Error on line " + str(i) + ". Add cannot have a numerical first argument."
    elif command[1] in assembler.registers.keys():
        if command[2].isdigit():
            assembler.registers[command[1]] += int(command[2])
        elif command[2] in assembler.localVars.keys():
            assembler.registers[command[1]] += int(assembler.localVars[command[2]])

def push(command, i):
    if command[1].isdigit():  # pushing a number to the stack
        assembler.stackPush(command[1])
    elif command[1] in assembler.DATA.keys():  # pushing a string from .SECT .DATA to the stack
        assembler.stackPush("foo")
    elif command[1] in assembler.localVars.keys():  # pushing a local int to the stack
        assembler.stackPush(assembler.localVars[command[1]])
    elif command[1] in assembler.BSS.keys():
        assembler.stackPush(assembler.BSS[command[1]][0])
    elif "(" in command[1] and ")" in command[1]:
        temp = command[1][command[1].find("(") + 1:command[1].find(")")]
        if temp in assembler.BSS.keys():
            # TODO memory
            1 + 1
        else:
            print("Error on line " + str(i) + ". I don't understand what (" + temp + ") is")
    else:
        print(command)
        print("Unknown error on line " + str(i) + ".")

def jmp(command, i):
    if command[1] in assembler.lookupTable.keys():
        if type(assembler.lookupTable[command[1]]) == assembler.LIST_TYPE:
            1 + 1
        else:
            assembler.jumpLocation = assembler.lookupTable[command[1]]

def mov(command, i):
    if command[1] in assembler.registers.keys():
        if command[2].isdigit():
            assembler.registers[command[1]] += int(command[2])
        elif command[2] in assembler.localVars.keys():
            assembler.registers[command[1]] += int(assembler.localVars[command[2]])

def je(command, i):
    if 1 + 1:
        jmp(command, i)

def jg(command, i):
    if 1 + 1:
        jmp(command, i)

def jge(command, i):
    if 1 + 1:
        jmp(command, i)

def jle(command, i):
    if 1 + 1:
        jmp(command, i)

def jl(command, i):
    if 1 + 1:
        jmp(command, i)
