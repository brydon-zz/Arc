'''
Created on 2013-10-01

@author: Brydon Eastman
'''
import unittest, as88


class Test(unittest.TestCase):
    """ Unittest calls setUp before each test method (a test method is any method that starts with "test" - they all "assert" something. """

    def setUp(self):
        """ Just reset the basic properties of an assembler between tests """
        global functionTable
        functionTable = as88.getFunctionTable()
        self.LIST_TYPE = type([])
        self.lookupTable = {}
        self.localVars = {}
        self.stackData = []
        self.DATA = {}
        self.BSS = {}

        self.jumpLocation = -1

        self.addressSpace = []

        for i in range(1024):
            self.addressSpace.append(str(0))

        self.registers = as88.getRegisters()
        self.flags = as88.getFlags()
        as88.newAssembler(self)

    # TODO: pop push mov and add with negative numbers, pop push move and add with digits, pop push move and add with overflow numbers,

    def testMovPositiveSmallNumbers(self):
        """ Moving small positive integers - the easiest case """
        for x in self.registers.keys():
            functionTable["MOV"](['MOV', x, '10'], 0)
            self.assertEqual(self.registers[x], 16, x + ' failed mov')

    def testMovSmallHexNumbers(self):
        """ moving hexy small numbers, things with letters"""
        for x in self.registers.keys():
            functionTable["MOV"](['MOV', x, '1f'], 0)
            self.assertEqual(self.registers[x], 31, x + ' failed mov')

    def testAddPositiveSmallNumbers(self):
        """ Adding small positive integers - the easiest case """
        for x in self.registers.keys():
            self.registers[x] = 10
            functionTable["ADD"](['ADD', x, '10'], 0)
            self.assertEqual(self.registers[x], 26, x + ' failed add')

    def testAddSmallHexNumbers(self):
        """ Adding hexy small numbers, things with letters"""
        for x in self.registers.keys():
            self.registers[x] = 10
            functionTable["ADD"](['ADD', x, '1f'], 0)
            self.assertEqual(self.registers[x], 41, x + ' failed add')

    def testStc(self):
        """ Testing the stc - set carry flag - method """
        self.flags['C'] = False
        functionTable["STC"]([], 0)
        self.assertEqual(self.flags['C'], True)

    def testClc(self):
        """ Testing the clc - clear carry flag - method """
        self.flags['C'] = True
        functionTable["CLC"]([], 0)
        self.assertEqual(self.flags['C'], False)

    def testJmp(self):
        """ Testing the jump method """
        self.lookupTable = {"test":25}
        functionTable["JMP"](['jmp', 'test'], 0)
        self.assertEqual(self.jumpLocation, 25)

    def testJeTrue(self):
        """ testing the jump if equal method, if passed a true condition """
        self.flags['Z'] = True
        self.lookupTable = {"test":25}
        functionTable["JE"](['je', 'test'], 0)
        self.assertEqual(self.jumpLocation, 25)

    def testJeFalse(self):
        """ testing the jump if equal method, if passed a false condition """
        self.flags['Z'] = False
        self.lookupTable = {"test":25}
        functionTable["JE"](['je', 'test'], 0)
        self.assertNotEqual(self.jumpLocation, 25)

    def testPopInRegister(self):
        """ testing popping into a register """
        for x in self.registers.keys():
            self.stackData = [10]
            functionTable["POP"](['pop', x], 0)
            self.assertEqual(self.registers[x], 10, x + " failed to Pop")

    def testPushRegister(self):
        """ testing pushing FROM a register """
        for x in self.registers.keys():
            self.stackData = []
            self.registers[x] = 10
            functionTable["PUSH"](['push', x], 0)
            self.assertEqual(self.stackData, [10])

    def testPushLocalvar(self):
        """ Teting pushing a LOCAL variable (i.e. an assembler level var) """
        self.localVars = {"test":25}
        functionTable["PUSH"](['push', 'test'], 0)
        self.assertEqual(self.stackData, [25])

    def testPushInt(self):
        """ Testing pushing a raw number """
        functionTable["PUSH"](['push', '11'], 0)
        self.assertEqual(self.stackData, [17])

    def testPushHex(self):
        """ testing pushing a hex number, with letters in it """
        functionTable["PUSH"](['push', '1f'], 0)
        self.assertEqual(self.stackData, [31])

    def testStosb(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.registers['AX'] = 102  # ord(f)=102 in dec
        self.registers['DI'] = 0
        functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.addressSpace[0], 'f')

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

if __name__ == "__main__":
    unittest.main()
