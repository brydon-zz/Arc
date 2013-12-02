'''
Created on 2013-12-01

@author: beewhy
'''
import unittest, as88


class Test(unittest.TestCase):

    def setUp(self):
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
        for x in self.registers.keys():
            as88.mov(['MOV', x, '10'], 0)
            self.assertEqual(self.registers[x], 10, x + ' failed mov')

    def testAddPositiveSmallNumbers(self):
        for x in self.registers.keys():
            self.registers[x] = 10
            as88.add(['ADD', x, '5'], 0)
            self.assertEqual(self.registers[x], 15, x + ' failed add')

    def testStc(self):
        self.flags['C'] = False
        as88.stc([], 0)
        self.assertEqual(self.flags['C'], True)

    def testClc(self):
        self.flags['C'] = True
        as88.clc([], 0)
        self.assertEqual(self.flags['C'], False)

    def testJmp(self):
        self.lookupTable = {"test":25}
        as88.jmp(['jmp', 'test'], 0)
        self.assertEqual(self.jumpLocation, 25)

    def testJeTrue(self):
        self.flags['Z'] = True
        self.lookupTable = {"test":25}
        as88.je(['je', 'test'], 0)
        self.assertEqual(self.jumpLocation, 25)

    def testJeFalse(self):
        self.flags['Z'] = False
        self.lookupTable = {"test":25}
        as88.je(['je', 'test'], 0)
        self.assertNotEqual(self.jumpLocation, 25)

    def testPopInRegister(self):
        for x in self.registers.keys():
            self.stackData = [10]
            as88.pop(['pop', x], 0)
            self.assertEqual(self.registers[x], 10, x + " failed to Pop")

    def testPushRegister(self):
        for x in self.registers.keys():
            self.stackData = []
            self.registers[x] = 10
            as88.push(['push', x], 0)
            self.assertEqual(self.stackData, [10])

    def testPushLocalvar(self):
        self.localVars = {"test":25}
        as88.push(['push', 'test'], 0)
        self.assertEqual(self.stackData, [25])

    def testPushInt(self):
        as88.push(['push', '11'], 0)
        self.assertEqual(self.stackData, [17])

    def testPushHex(self):
        as88.push(['push', '1f'], 0)
        self.assertEqual(self.stackData, [31])

    def testStosb(self):
        self.registers['AX'] = 102  # ord(f)=102 in dec
        self.registers['DI'] = 0
        as88.stosb(['stosb'], 0)
        self.assertEqual(self.addressSpace[0], 'f')

    def outPut(self, s):
        print s

    def stopRunning(self, x=1):
        print "Fatal error"

    def updateStack(self):
        1 + 1

if __name__ == "__main__":
    unittest.main()
