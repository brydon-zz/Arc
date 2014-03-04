'''
Created on 2013-10-01

@author: Brydon Eastman
'''
import unittest
import CommandInterpreter, Intel8088


class Test(unittest.TestCase):
    """ Unittest calls setUp before each test method (a test method is any method that starts with "test" - they all "assert" something. """

    def setUp(self):
        """ Just reset the basic properties of an assembler between tests """
        self.machine = Intel8088.Intel8088()

        as88 = CommandInterpreter.CommandInterpreter(self, self.machine)
        self.functionTable = as88.getFunctionTable()

    # TODO: pop push mov and add with negative numbers, pop push move and add with digits, pop push move and add with overflow numbers,

    def testMovPositiveSmallNumbers(self):
        """ Moving small positive integers - the easiest case """
        for x in self.machine.registers.keys():
            self.functionTable["MOV"](['MOV', x, '10'], 0)
            self.assertEqual(self.machine.registers[x], 16, x + ' failed mov')

    def testMovSmallHexNumbers(self):
        """ moving hexy small numbers, things with letters"""
        for x in self.machine.registers.keys():
            self.functionTable["MOV"](['MOV', x, '1f'], 0)
            self.assertEqual(self.machine.registers[x], 31, x + ' failed mov')

    def testAddPositiveSmallNumbers(self):
        """ Adding small positive integers - the easiest case """
        for x in self.machine.registers.keys():
            self.machine.registers[x] = 10
            self.functionTable["ADD"](['ADD', x, '10'], 0)
            self.assertEqual(self.machine.registers[x], 26, x + ' failed add')

    def testAddSmallHexNumbers(self):
        """ Adding hexy small numbers, things with letters"""
        for x in self.machine.registers.keys():
            self.machine.registers[x] = 10
            self.functionTable["ADD"](['ADD', x, '1f'], 0)
            self.assertEqual(self.machine.registers[x], 41, x + ' failed add')

    def testStc(self):
        """ Testing the stc - set carry flag - method """
        self.machine.flags['C'] = False
        self.functionTable["STC"]([], 0)
        self.assertEqual(self.machine.flags['C'], True)

    def testClc(self):
        """ Testing the clc - clear carry flag - method """
        self.machine.flags['C'] = True
        self.functionTable["CLC"]([], 0)
        self.assertEqual(self.machine.flags['C'], False)

    """ 
    ******* Jump Tests ********
        Kind of jumps
        JMP, JCXZ, JE-JNE, JG-JNG, JL-JNL, JGE-JNGE, JLE-JNLE, JC-JNC, JO-JNO, JP-JNP, JZ-JNZ, JS-JNS, JPE, JPO   
    """

    def testJmp(self):
        """ Testing the jump method """
        self.machine.lookupTable = {"test":25}
        self.functionTable["JMP"](['jmp', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJcxzTrue(self):
        """ Testing the CXZ method when passed a true condition"""
        self.machine.registers['CX'] = 0
        self.machine.lookupTable = {"test":25}
        self.functionTable['JCXZ'](['jcxz', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJcxzFalse(self):
        """ Testing the CXZ method when passed a false condition"""
        self.machine.registers['CX'] = 1
        self.machine.lookupTable = {"test":25}
        self.functionTable['JCXZ'](['jcxz', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJeTrue(self):
        """ testing the jump if equal method, if passed a true condition """
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JE"](['je', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJeFalse(self):
        """ testing the jump if equal method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JE"](['je', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJneTrue(self):
        """ testing the jump if not equal method, if passed a true condition """
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNE"](['jne', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJneFalse(self):
        """ testing the jump if not equal method, if passed a false condition """
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNE"](['jne', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJgTrue(self):
        """ testing the jump if greater than method, if passed a true condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JG"](['jg', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJgFalse(self):
        """ testing the jump if greater than method, if passed a false condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JG"](['jg', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJngTrue(self):
        """ testing the jump if not greater than method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNG"](['jng', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJngFalse(self):
        """ testing the jump if not greater than method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.flags['S'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNG"](['jnG', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJlTrue(self):
        """ testing the jump if les than method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JL"](['jl', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJlFalse(self):
        """ testing the jump if less than method, if passed a false condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JL"](['jl', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnlTrue(self):
        """ testing the jump if not less than method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNL"](['jnl', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnlFalse(self):
        """ testing the jump if not less than method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.flags['S'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNL"](['jnl', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJgeTrue(self):
        """ testing the jump if greater than equal method, if passed a true condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JGE"](['jge', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJgeFalse(self):
        """ testing the jump if greater than equal method, if passed a false condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JGE"](['jge', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJngeTrue(self):
        """ testing the jump if not greater than equal method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNGE"](['jng', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJngeFalse(self):
        """ testing the jump if not greater than equal method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.flags['S'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNGE"](['jnG', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJleTrue(self):
        """ testing the jump if less than equal method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JLE"](['jge', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJleFalse(self):
        """ testing the jump if less than equal method, if passed a false condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JLE"](['jge', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnleTrue(self):
        """ testing the jump if not less than equal method, if passed a true condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNLE"](['jng', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnleFalse(self):
        """ testing the jump if not less than equal method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.flags['S'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNLE"](['jnG', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)


    def testJcTrue(self):
        """ testing the jump if carry method, if passed a true condition """
        self.machine.flags['C'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JC"](['jc', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJcFalse(self):
        """ testing the jump if carry method, if passed a false condition """
        self.machine.flags['C'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JC"](['jc', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJncTrue(self):
        """ testing the jump if not carry method, if passed a true condition """
        self.machine.flags['C'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNC"](['jnc', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJncFalse(self):
        """ testing the jump if not carry method, if passed a false condition """
        self.machine.flags['C'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNC"](['jnc', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJoTrue(self):
        """ testing the jump if overflow method, if passed a true condition """
        self.machine.flags['O'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JO"](['jo', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJoFalse(self):
        """ testing the jump if overflow method, if passed a false condition """
        self.machine.flags['O'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JO"](['jo', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnoTrue(self):
        """ testing the jump if not overflow method, if passed a true condition """
        self.machine.flags['O'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNO"](['jno', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnoFalse(self):
        """ testing the jump if not overflow method, if passed a false condition """
        self.machine.flags['O'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNO"](['jno', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJpTrue(self):
        """ testing the jump if parity method, if passed a true condition """
        self.machine.flags['P'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JP"](['jp', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJpFalse(self):
        """ testing the jump if parity method, if passed a false condition """
        self.machine.flags['P'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JP"](['jp', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnpTrue(self):
        """ testing the jump if not parity method, if passed a true condition """
        self.machine.flags['P'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNP"](['jnp', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnpFalse(self):
        """ testing the jump if not parity method, if passed a false condition """
        self.machine.flags['P'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNP"](['jnp', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJzTrue(self):
        """ testing the jump if zero method, if passed a true condition """
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JZ"](['jz', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJzFalse(self):
        """ testing the jump if zero method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JZ"](['jz', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnzTrue(self):
        """ testing the jump if not zero method, if passed a true condition """
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNZ"](['jnz', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnzFalse(self):
        """ testing the jump if not zero method, if passed a false condition """
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNZ"](['jnZ', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJsTrue(self):
        """ testing the jump if sign method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JS"](['js', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJsFalse(self):
        """ testing the jump if sign method, if passed a false condition """
        self.machine.flags['S'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JS"](['js', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnsTrue(self):
        """ testing the jump if not sign method, if passed a true condition """
        self.machine.flags['S'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNS"](['jns', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnsFalse(self):
        """ testing the jump if not sign method, if passed a false condition """
        self.machine.flags['S'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNS"](['jns', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJpeTrue(self):
        """ testing the jump if parity/equal method, if passed a true condition """
        self.machine.flags['P'] = False
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JPE"](['jpe', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJpeFalse(self):
        """ testing the jump if parity/equal method, if passed a false condition """
        self.machine.flags['P'] = False
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JPE"](['jpe', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJpoTrue(self):
        """ testing the jump if parity/overflow method, if passed a true condition """
        self.machine.flags['P'] = False
        self.machine.flags['O'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JPO"](['jpo', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJpoFalse(self):
        """ testing the jump if parity/overflow method, if passed a false condition """
        self.machine.flags['P'] = False
        self.machine.flags['O'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JPO"](['jpo', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testPopInRegister(self):
        """ testing popping into a register """
        for x in self.machine.registers.keys():
            self.machine.stackData = [10]
            self.functionTable["POP"](['pop', x], 0)
            self.assertEqual(self.machine.registers[x], 10, x + " failed to Pop")

    def testPushRegister(self):
        """ testing pushing FROM a register """
        for x in self.machine.registers.keys():
            self.machine.stackData = []
            self.machine.registers[x] = 10
            self.functionTable["PUSH"](['push', x], 0)
            self.assertEqual(self.machine.stackData, [10])

    def testPushLocalvar(self):
        """ Teting pushing a LOCAL variable (i.e. an assembler level var) """
        self.machine.localVars = {"test":25}
        self.functionTable["PUSH"](['push', 'test'], 0)
        self.assertEqual(self.machine.stackData, [25])

    def testPushInt(self):
        """ Testing pushing a raw number """
        self.functionTable["PUSH"](['push', '11'], 0)
        self.assertEqual(self.machine.stackData, [17])

    def testPushHex(self):
        """ testing pushing a hex number, with letters in it """
        self.functionTable["PUSH"](['push', '1f'], 0)
        self.assertEqual(self.machine.stackData, [31])

    def testStosb(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbd7(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbd8(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbd0(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbd1(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbd4(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbd3(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbdddd(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbssss(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbsdf(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbnab(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbhan(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbha(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbhh(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb8888(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbg(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbf(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbe(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbd(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosbc(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbb(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosba(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosbff(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb44444(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb555(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb444(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb08(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb99(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb98(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb92(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb4242(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb2323(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb22222(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb1111(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb111(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb11f1(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb19(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb15(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb21(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb25(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb24(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb33(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb22(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb11(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb00(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb9(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb8(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb7(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb6(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb5(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb4(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb3(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
    def testStosb2(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def testStosb1(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')

    def outPut(self, s):
        """ Necessary - the as88 interpreter calls the assemblers output methods when errors happen """
        print s

    def stopRunning(self, x=1):
        """ If stoprunning is passed, then something was broken! """
        self.fail("Stop running called")
        print "Fatal error"

    def updateStack(self):
        """ Necessary - the as88 interpreter calls this method to inform the GUI stack guis need changing """
        1 + 1

    def testRcrWithCarry(self):
        self.machine.registers['AX'] = 103
        self.machine.flags['C'] = 1
        self.functionTable["RCR"](['rcr', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -32717)
        self.assertTrue(self.machine.flags['C'])

    def testRcrWithoutCarry(self):
        self.machine.registers['AX'] = 102
        self.machine.flags['C'] = 0
        self.functionTable["RCR"](['rcr', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 51)
        self.assertFalse(self.machine.flags['C'])

    def testPushf(self):
        self.machine.flags = {"Z":True, "S":True, "O":True, "C":True, "A":True, "P":True, "D":True, "I":True}
        self.functionTable['PUSHF'](['PUSHF'], 0)
        self.assertEqual(self.machine.stackData[-1], 255)

if __name__ == "__main__":
    unittest.main()
