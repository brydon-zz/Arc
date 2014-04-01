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

import unittest
import assembler.CommandInterpreter, assembler.Intel8088

class Test(unittest.TestCase):
    """ Unittest calls setUp before each test method (a test method is any method that starts with "test" - they all "assert" something. """

    def setUp(self):
        """ Just reset the basic properties of an assembler between tests """
        self.machine = assembler.Intel8088.Intel8088()

        as88 = assembler.CommandInterpreter.CommandInterpreter(self.machine)
        self.functionTable = as88.getFunctionTable()

    # TODO: pop push mov and add with negative numbers, pop push move and add with digits, pop push move and add with overflow numbers,

    def testAdc(self):
        self.machine.flags['C'] = 1
        self.machine.registers['AX'] = 2
        self.functionTable['ADC'](['ADC', 'AX', '1'], 0)
        self.assertEqual(self.machine.registers["AX"], 4)
        self.machine.flags['C'] = 0
        self.machine.registers['AX'] = 2
        self.functionTable['ADC'](['ADC', 'AX', '1'], 0)
        self.assertEqual(self.machine.registers["AX"], 3)

    def testAddBigOverflow(self):
        """ Adding small positive integers - the easiest case """
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = 2 ** 15 - 1
            self.functionTable["ADD"](['ADD', x, 'FFh'], 0)
            self.assertEqual(self.machine.registers[x], -32514)

    def testAddLetter(self):
        self.machine.registers['AX'] = 1
        self.functionTable['ADD'](['ADD', 'AX', "'g'"], 0)
        self.assertEqual(self.machine.registers['AX'], 104)

    def testAddNegativeLargeNumbers(self):
        """ Adding small positive integers - the easiest case """
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = -200
            self.functionTable["ADD"](['ADD', x, '98304'], 42)
            self.assertEqual(self.machine.registers[x], 32568)

    def testAddNegativeSmallHexNumbers(self):
        """ Adding small positive integers - the easiest case """
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = -200
            self.functionTable["ADD"](['ADD', x, 'fh'], 0)
            self.assertEqual(self.machine.registers[x], -185)

    def testAddNegativeSmallNumbers(self):
        """ Adding small positive integers - the easiest case """
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = -200
            self.functionTable["ADD"](['ADD', x, '1'], 0)
            self.assertEqual(self.machine.registers[x], -199)

    def testAddOverflow(self):
        """ Adding small positive integers - the easiest case """
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = 2 ** 15 - 1
            self.functionTable["ADD"](['ADD', x, '1'], 0)
            self.assertEqual(self.machine.registers[x], -2 ** 15)

    def testAddPositiveSmallNumbers(self):
        """ Adding small positive integers - the easiest case """
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = 10
            self.functionTable["ADD"](['ADD', x, '10'], 0)
            self.assertEqual(self.machine.registers[x], 20)

    def testAddSmallHexNumbers(self):
        """ Adding hexy small numbers, things with letters"""
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = 10
            self.functionTable["ADD"](['ADD', x, '1fh'], 0)
            self.assertEqual(self.machine.registers[x], 41)

    def testAnd(self):
        self.machine.registers['AX'] = int('1101101', 2)
        self.machine.registers['BX'] = int('0110101', 2)
        self.functionTable["AND"](["AND", "AX", "BX"], 0)
        self.assertEqual(self.machine.registers["AX"], int("0100101", 2))

    def testClc(self):
        """ Testing the clc - clear carry flag - method """
        self.machine.flags['C'] = True
        self.functionTable["CLC"]([], 0)
        self.assertEqual(self.machine.flags['C'], False)

    def testCld(self):
        """ Testing the clc - clear carry flag - method """
        self.machine.flags['D'] = True
        self.functionTable["CLD"]([], 0)
        self.assertEqual(self.machine.flags['D'], False)

    def testCmpb(self):
        """ Testing CMPB"""
        self.machine.registers['BX'] = 8
        self.functionTable['CMPB'](['CMPB', 'BL', '8'], 0)
        self.assertTrue(self.machine.flags['Z'])

    def testCmpbWithLetters(self):
        """ Testing CMPB"""
        self.machine.registers['BX'] = 76
        self.functionTable['CMPB'](['CMPB', 'BL', "'L'"], 0)
        self.assertTrue(self.machine.flags['Z'])

    """ 
    ******* Jump Tests ********
        Kind of jumps
        JMP, JCXZ, JE-JNE, JG-JNG, JL-JNL, JGE-JNGE, JLE-JNLE, JC-JNC, JO-JNO, JP-JNP, JZ-JNZ, JS-JNS, JPE, JPO   
    """

    def testCli(self):
        """ Testing the clc - clear carry flag - method """
        self.machine.flags['I'] = True
        self.functionTable["CLI"]([], 0)
        self.assertEqual(self.machine.flags['I'], False)

    def testJcFalse(self):
        """ testing the jump if carry method, if passed a false condition """
        self.machine.flags['C'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JC"](['jc', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJcTrue(self):
        """ testing the jump if carry method, if passed a true condition """
        self.machine.flags['C'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JC"](['jc', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJcxzFalse(self):
        """ Testing the CXZ method when passed a false condition"""
        self.machine.registers['CX'] = 1
        self.machine.lookupTable = {"test":25}
        self.functionTable['JCXZ'](['jcxz', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJcxzTrue(self):
        """ Testing the CXZ method when passed a true condition"""
        self.machine.registers['CX'] = 0
        self.machine.lookupTable = {"test":25}
        self.functionTable['JCXZ'](['jcxz', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJeFalse(self):
        """ testing the jump if equal method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JE"](['je', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJeTrue(self):
        """ testing the jump if equal method, if passed a true condition """
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JE"](['je', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJgFalse(self):
        """ testing the jump if greater than method, if passed a false condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JG"](['jg', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJgTrue(self):
        """ testing the jump if greater than method, if passed a true condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JG"](['jg', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJgeFalse(self):
        """ testing the jump if greater than equal method, if passed a false condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JGE"](['jge', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJgeTrue(self):
        """ testing the jump if greater than equal method, if passed a true condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JGE"](['jge', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJlFalse(self):
        """ testing the jump if less than method, if passed a false condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JL"](['jl', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJlTrue(self):
        """ testing the jump if les than method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JL"](['jl', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJleFalse(self):
        """ testing the jump if less than equal method, if passed a false condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JLE"](['jge', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJleTrue(self):
        """ testing the jump if less than equal method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JLE"](['jge', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJmp(self):
        """ Testing the jump method """
        self.machine.lookupTable = {"test":25}
        self.functionTable["JMP"](['jmp', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJncFalse(self):
        """ testing the jump if not carry method, if passed a false condition """
        self.machine.flags['C'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNC"](['jnc', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJncTrue(self):
        """ testing the jump if not carry method, if passed a true condition """
        self.machine.flags['C'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNC"](['jnc', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJneFalse(self):
        """ testing the jump if not equal method, if passed a false condition """
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNE"](['jne', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJneTrue(self):
        """ testing the jump if not equal method, if passed a true condition """
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNE"](['jne', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJngFalse(self):
        """ testing the jump if not greater than method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.flags['S'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNG"](['jnG', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJngTrue(self):
        """ testing the jump if not greater than method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNG"](['jng', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJngeFalse(self):
        """ testing the jump if not greater than equal method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.flags['S'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNGE"](['jnG', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJngeTrue(self):
        """ testing the jump if not greater than equal method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNGE"](['jng', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnlFalse(self):
        """ testing the jump if not less than method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.flags['S'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNL"](['jnl', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnlTrue(self):
        """ testing the jump if not less than method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNL"](['jnl', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnleFalse(self):
        """ testing the jump if not less than equal method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.flags['S'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNLE"](['jnG', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)


    def testJnleTrue(self):
        """ testing the jump if not less than equal method, if passed a true condition """
        self.machine.flags['S'] = False
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNLE"](['jng', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnoFalse(self):
        """ testing the jump if not overflow method, if passed a false condition """
        self.machine.flags['O'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNO"](['jno', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnoTrue(self):
        """ testing the jump if not overflow method, if passed a true condition """
        self.machine.flags['O'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNO"](['jno', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnpFalse(self):
        """ testing the jump if not parity method, if passed a false condition """
        self.machine.flags['P'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNP"](['jnp', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnpTrue(self):
        """ testing the jump if not parity method, if passed a true condition """
        self.machine.flags['P'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNP"](['jnp', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnsFalse(self):
        """ testing the jump if not sign method, if passed a false condition """
        self.machine.flags['S'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNS"](['jns', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnsTrue(self):
        """ testing the jump if not sign method, if passed a true condition """
        self.machine.flags['S'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNS"](['jns', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJnzFalse(self):
        """ testing the jump if not zero method, if passed a false condition """
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNZ"](['jnZ', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJnzTrue(self):
        """ testing the jump if not zero method, if passed a true condition """
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JNZ"](['jnz', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJoFalse(self):
        """ testing the jump if overflow method, if passed a false condition """
        self.machine.flags['O'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JO"](['jo', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJoTrue(self):
        """ testing the jump if overflow method, if passed a true condition """
        self.machine.flags['O'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JO"](['jo', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJpFalse(self):
        """ testing the jump if parity method, if passed a false condition """
        self.machine.flags['P'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JP"](['jp', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJpTrue(self):
        """ testing the jump if parity method, if passed a true condition """
        self.machine.flags['P'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JP"](['jp', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJpeFalse(self):
        """ testing the jump if parity/equal method, if passed a false condition """
        self.machine.flags['P'] = False
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JPE"](['jpe', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJpeTrue(self):
        """ testing the jump if parity/equal method, if passed a true condition """
        self.machine.flags['P'] = False
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JPE"](['jpe', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJpoFalse(self):
        """ testing the jump if parity/overflow method, if passed a false condition """
        self.machine.flags['P'] = False
        self.machine.flags['O'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JPO"](['jpo', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJpoTrue(self):
        """ testing the jump if parity/overflow method, if passed a true condition """
        self.machine.flags['P'] = False
        self.machine.flags['O'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JPO"](['jpo', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJsFalse(self):
        """ testing the jump if sign method, if passed a false condition """
        self.machine.flags['S'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JS"](['js', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJsTrue(self):
        """ testing the jump if sign method, if passed a true condition """
        self.machine.flags['S'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JS"](['js', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testJumpFarNear(self):
        self.machine.lookupTable = {"1":[10, 20, 30, 40], "2":35}
        self.machine.registers["PC"] = 11
        self.functionTable["JMP"](["JMP", "1f"], 0)
        self.assertEqual(self.machine.jumpLocation, 20)
        self.functionTable["JMP"](["JMP", "1b"], 0)
        self.assertEqual(self.machine.jumpLocation, 10)
        self.functionTable["JMP"](["JMP", "2"], 0)
        self.assertEqual(self.machine.jumpLocation, 35)

    def testJumpImmed(self):
        self.functionTable["JMP"](['JMP', '10'], 0)
        self.assertEqual(self.machine.jumpLocation, 10)

    def testJzFalse(self):
        """ testing the jump if zero method, if passed a false condition """
        self.machine.flags['Z'] = False
        self.machine.lookupTable = {"test":25}
        self.functionTable["JZ"](['jz', 'test'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 25)

    def testJzTrue(self):
        """ testing the jump if zero method, if passed a true condition """
        self.machine.flags['Z'] = True
        self.machine.lookupTable = {"test":25}
        self.functionTable["JZ"](['jz', 'test'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)

    def testLodsb(self):
        self.machine.addressSpace[70] = 24
        self.machine.registers['SI'] = 70
        self.functionTable["LODSB"](['LODSB'], 0)
        self.assertEqual(self.machine.getEightBitRegister('AL'), 24)
        self.assertEqual(self.machine.registers['SI'], 71)

    def testLodsw(self):
        self.machine.addressSpace[70] = 24
        self.machine.addressSpace[71] = 31

        self.functionTable["STD"](['STD'], 0)
        self.machine.registers['SI'] = 70
        self.functionTable["LODSW"](['LODSW'], 0)

        self.assertEqual(self.machine.getEightBitRegister('AL'), 24)
        self.assertEqual(self.machine.getEightBitRegister('AH'), 31)

        self.assertEqual(self.machine.registers['SI'], 68)

    def testLoop(self):
        self.machine.registers["CX"] = 2
        self.machine.lookupTable = {"test":25, "test2":20}
        self.functionTable["LOOP"](["LOOP", "test2"], 0)
        self.assertEqual(self.machine.registers['CX'], 1)
        self.assertEqual(self.machine.jumpLocation, 20)
        self.functionTable["LOOP"](["LOOP", "test"], 0)
        self.assertEqual(self.machine.registers['CX'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)
        self.functionTable["LOOP"](["LOOP", "test2"], 0)
        self.assertEqual(self.machine.registers['CX'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 20)

    def testLoopEFalse(self):
        self.machine.flags['Z'] = False
        self.machine.registers["CX"] = 2
        self.machine.lookupTable = {"test":25, "test2":20}
        self.functionTable["LOOPE"](["LOOPE", "test2"], 0)
        self.assertNotEqual(self.machine.registers['CX'], 1)
        self.assertNotEqual(self.machine.jumpLocation, 20)

    def testLoopETrue(self):
        self.machine.flags['Z'] = True
        self.machine.registers["CX"] = 2
        self.machine.lookupTable = {"test":25, "test2":20}
        self.functionTable["LOOPE"](["LOOPE", "test2"], 0)
        self.assertEqual(self.machine.registers['CX'], 1)
        self.assertEqual(self.machine.jumpLocation, 20)
        self.functionTable["LOOPE"](["LOOPE", "test"], 0)
        self.assertEqual(self.machine.registers['CX'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)
        self.functionTable["LOOPE"](["LOOPE", "test2"], 0)
        self.assertEqual(self.machine.registers['CX'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 20)

    def testLoopNEFalse(self):
        self.machine.flags['Z'] = True
        self.machine.registers["CX"] = 2
        self.machine.lookupTable = {"test":25, "test2":20}
        self.functionTable["LOOPNE"](["LOOPNE", "test2"], 0)
        self.assertNotEqual(self.machine.registers['CX'], 1)
        self.assertNotEqual(self.machine.jumpLocation, 20)

    def testLoopNETrue(self):
        self.machine.flags['Z'] = False
        self.machine.registers["CX"] = 2
        self.machine.lookupTable = {"test":25, "test2":20}
        self.functionTable["LOOPNE"](["LOOPNE", "test2"], 0)
        self.assertEqual(self.machine.registers['CX'], 1)
        self.assertEqual(self.machine.jumpLocation, 20)
        self.functionTable["LOOPNE"](["LOOPNE", "test"], 0)
        self.assertEqual(self.machine.registers['CX'], 0)
        self.assertEqual(self.machine.jumpLocation, 25)
        self.functionTable["LOOPNE"](["LOOPNE", "test2"], 0)
        self.assertEqual(self.machine.registers['CX'], 0)
        self.assertNotEqual(self.machine.jumpLocation, 20)

    def testMovLetter(self):
        self.machine.registers['AX'] = 3
        self.functionTable['MOV'](['MOV', 'AX', "'\n'"], 0)
        self.assertEqual(self.machine.registers['AX'], 10)

    def testMovPositiveSmallNumbers(self):
        """ Moving small positive integers - the easiest case """
        for x in self.machine.registers.keys():
            self.functionTable["MOV"](['MOV', x, '10'], 0)
            self.assertEqual(self.machine.registers[x], 10, x + ' failed mov')

    def testMovSmallHexNumbers(self):
        """ moving hexy small numbers, things with letters"""
        for x in self.machine.registers.keys():
            self.functionTable["MOV"](['MOV', x, '1fh'], 0)
            self.assertEqual(self.machine.registers[x], 31, x + ' failed mov')

    def testNot(self):
        self.machine.registers['AX'] = int('1101101101010101', 2) - 2 ** 16
        self.functionTable["NOT"](["NOT", "AX"], 0)
        self.assertEqual(self.machine.registers["AX"], int("0010010010101010", 2))
        self.machine.registers['AX'] = int('0101101101010101', 2)
        self.functionTable["NOT"](["NOT", "AX"], 0)
        self.assertEqual(self.machine.registers["AX"], int("0010010010101010", 2) - 2 ** 15)

    def testOr(self):
        self.machine.registers['AX'] = int('1101101', 2)
        self.machine.registers['BX'] = int('0110101', 2)
        self.functionTable["OR"](["OR", "AX", "BX"], 0)
        self.assertEqual(self.machine.registers["AX"], int("1111101", 2))

    def testPopInRegister(self):
        """ testing popping into a register """
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.stack = [10]
            self.functionTable["POP"](['pop', x], 0)
            self.assertEqual(self.machine.registers[x], 10, x + " failed to Pop")

    def testPopf(self):
        self.machine.stack.append(1 + 4 + 64)
        self.functionTable['POPF'](['POPF'], 0)
        self.assertTrue(self.machine.flags['C'])
        self.assertTrue(self.machine.flags['P'])
        self.assertTrue(self.machine.flags['Z'])

        self.machine.stack.append(1 + 4 + 16 + 64 + 128)
        self.functionTable['POPF'](['POPF'], 0)
        self.assertTrue(self.machine.flags['C'])
        self.assertTrue(self.machine.flags['P'])
        self.assertTrue(self.machine.flags['Z'])
        self.assertTrue(self.machine.flags['S'])
        self.assertTrue(self.machine.flags['A'])

    def testPushHex(self):
        """ testing pushing a hex number, with letters in it """
        self.functionTable["PUSH"](['push', '1fh'], 0)
        self.assertEqual(self.machine.stack, [31])

    def testPushInt(self):
        """ Testing pushing a raw number """
        self.functionTable["PUSH"](['push', '11'], 0)
        self.assertEqual(self.machine.stack, [11])

    def testPushLocalvar(self):
        """ Teting pushing a LOCAL variable (i.e. an assembler level var) """
        self.machine.localVars = {"test":25}
        self.functionTable["PUSH"](['push', 'test'], 0)
        self.assertEqual(self.machine.stack, [25])

    def testPushRegister(self):
        """ testing pushing FROM a register """
        for x in self.machine.registers.keys():
            self.machine.stack = []
            self.machine.registers[x] = 10
            self.functionTable["PUSH"](['push', x], 0)
            self.assertEqual(self.machine.stack, [10])

    def testPushf(self):
        self.machine.flags = {"Z":True, "S":True, "C":True, "A":True, "P":True}
        self.functionTable['PUSHF'](['PUSHF'], 0)
        self.assertEqual(self.machine.stack[-1], 1 + 4 + 16 + 64 + 128)
        self.machine.flags = {"Z":False, "S":True, "C":False, "A":True, "P":False}
        self.functionTable['PUSHF'](['PUSHF'], 0)
        self.assertEqual(self.machine.stack[-1], 16 + 128)

    def testRcl(self):
        self.machine.registers['AX'] = 2 ** 13 + 1 + 2 ** 12
        self.assertFalse(self.machine.flags['C'])
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14 + 2 + 2 ** 13)
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15 + 4 + 2 ** 14)
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertTrue(self.machine.flags['C'])
        self.assertEqual(self.machine.registers['AX'], 8 - 2 ** 15)
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertTrue(self.machine.flags['C'])
        self.assertEqual(self.machine.registers['AX'], 1 + 16)
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertFalse(self.machine.flags['C'])
        self.assertEqual(self.machine.registers['AX'], 1 + 2 + 32)

    def testRclPowerOf2(self):
        self.machine.registers['AX'] = 2 ** 13
        self.assertFalse(self.machine.flags['C'])
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14)
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15)
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 0)
        self.assertTrue(self.machine.flags['C'])
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertFalse(self.machine.flags['C'])
        self.assertEqual(self.machine.registers['AX'], 1)
        self.functionTable["RCL"](['rcl', 'AX'], 0)
        self.assertFalse(self.machine.flags['C'])
        self.assertEqual(self.machine.registers['AX'], 2)

    def testRcrPowerOf2(self):
        self.machine.registers['AX'] = 4
        self.assertFalse(self.machine.flags['C'])
        self.functionTable["RCR"](['rcr', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2)
        self.assertFalse(self.machine.flags['C'])
        self.functionTable["RCR"](['rcr', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1)
        self.assertFalse(self.machine.flags['C'])
        self.functionTable["RCR"](['rcr', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 0)
        self.assertTrue(self.machine.flags['C'])
        self.functionTable["RCR"](['rcr', 'AX'], 0)
        self.assertFalse(self.machine.flags['C'])
        self.assertEqual(self.machine.registers['AX'], -2 ** 15)
        self.functionTable["RCR"](['rcr', 'AX'], 0)
        self.assertFalse(self.machine.flags['C'])
        self.assertEqual(self.machine.registers['AX'], 2 ** 14)

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

    def testRolWithWraparound(self):
        self.machine.registers['AX'] = 2 ** 13 + 3
        self.machine.flags['C'] = 1
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14 + 6)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15 + 12)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1 + 24)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 + 48)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 4 + 96)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 200)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 400)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 800)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1600)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 3200)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 6400)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 12800)

    def testRolWithWraparoundPowerOf2(self):
        self.machine.registers['AX'] = 2 ** 13
        self.machine.flags['C'] = 1
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 4)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 8)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 16)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 32)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 64)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 128)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 256)
        self.functionTable["ROL"](['rol', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 512)

    def testRorWithWrapAround(self):
        self.machine.registers['AX'] = 16 + 64
        self.machine.flags['C'] = 1
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 8 + 32)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 4 + 16)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 + 8)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1 + 4)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15 + 2)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14 + 1)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 13 - 2 ** 15)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 12 + 2 ** 14)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 11 + 2 ** 13)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 10 + 2 ** 12)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 9 + 2 ** 11)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 8 + 2 ** 10)

    def testRorWithWrapAroundPowerOf2(self):
        self.machine.registers['AX'] = 16
        self.machine.flags['C'] = 1
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 8)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 4)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 13)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 12)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 11)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 10)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 9)
        self.functionTable["ROR"](['ror', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 8)

    def testSARWithSignBit(self):
        self.machine.registers['AX'] = -2 ** 15 + 2 ** 14 + 1
        self.functionTable["SAR"](['SAR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15 + 2 ** 14 + 2 ** 13)
        self.assertTrue(self.machine.flags['C'])
        self.functionTable["SAR"](['SAR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15 + 2 ** 14 + 2 ** 13 + 2 ** 12)

    def testSARWithoutSignBit(self):
        self.machine.registers['AX'] = 4 + 2 ** 10
        self.functionTable["SAR"](['SAR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 + 2 ** 9)
        self.functionTable["SAR"](['SAR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1 + 2 ** 8)
        self.functionTable["SAR"](['SAR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 7)
        self.assertTrue(self.machine.flags['C'])

    def testSbb(self):
        self.machine.flags['C'] = 1
        self.machine.registers['AX'] = 2
        self.functionTable['SBB'](['SBB', 'AX', '1'], 0)
        self.assertEqual(self.machine.registers["AX"], 0)
        self.machine.flags['C'] = 0
        self.machine.registers['AX'] = 2
        self.functionTable['SBB'](['SBB', 'AX', '1'], 0)
        self.assertEqual(self.machine.registers["AX"], 1)

    def testShl(self):
        self.machine.registers['AX'] = 1 + 2 ** 13
        self.functionTable["SHL"](['SHL', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 + 2 ** 14)
        self.functionTable["SHL"](['SHL', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 4 - 2 ** 15)
        self.functionTable["SHL"](['SHL', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 8)
        self.assertTrue(self.machine.flags['C'])

    def testShlPowerOf2(self):
        self.machine.registers['AX'] = 2 ** 13
        self.functionTable["SHL"](['SHL', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14)
        self.functionTable["SHL"](['SHL', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], -2 ** 15)

    def testShr(self):
        self.machine.registers['AX'] = 4 + 2
        self.functionTable["SHR"](['SHR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 + 1)
        self.functionTable["SHR"](['SHR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1)
        self.assertTrue(self.machine.flags['C'])

    def testShrNegative(self):
        self.machine.registers['AX'] = -2 ** 15 + 2 ** 14
        self.functionTable["SHR"](['SHR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14 + 2 ** 13)

    def testShrNegativePowerOf2(self):
        self.machine.registers['AX'] = -2 ** 15
        self.functionTable["SHR"](['SHR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 2 ** 14)

    def testShrPowerOf2(self):
        self.machine.registers['AX'] = 2
        self.functionTable["SHR"](['SHR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 1)
        self.functionTable["SHR"](['SHR', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 0)
        self.assertTrue(self.machine.flags['C'])

    def testShrlNegativePowerOf2(self):
        self.machine.registers['AX'] = -2 ** 15
        self.functionTable["SHL"](['SHL', 'AX'], 0)
        self.assertEqual(self.machine.registers['AX'], 0)
        self.assertTrue(self.machine.flags['C'])

    def testStc(self):
        """ Testing the stc - set carry flag - method """
        self.machine.flags['C'] = False
        self.functionTable["STC"]([], 0)
        self.assertEqual(self.machine.flags['C'], True)

    def testStd(self):
        """ Testing the stc - set carry flag - method """
        self.machine.flags['D'] = False
        self.functionTable["STD"]([], 0)
        self.assertEqual(self.machine.flags['D'], True)

    def testSti(self):
        """ Testing the stc - set carry flag - method """
        self.machine.flags['I'] = False
        self.functionTable["STI"]([], 0)
        self.assertEqual(self.machine.flags['I'], True)

    def testStosbInc(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.machine.flags['D'] = 0
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
        self.assertEqual(self.machine.registers['DI'], 1)

    def testStosbDec(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 102  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.machine.flags['D'] = 1
        self.functionTable["STOSB"](['stosb'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'f')
        self.assertEqual(self.machine.registers['DI'], -1)

    def testStoswInc(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 26729  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.machine.flags['D'] = 0
        self.functionTable["STOSW"](['stosw'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'h')
        self.assertEqual(self.machine.addressSpace[1], 'i')
        self.assertEqual(self.machine.registers['DI'], 2)

    def testStoswDec(self):
        """ Testing the STOSB command - store byte in string in memory """
        self.machine.registers['AX'] = 26729  # ord(f)=102 in dec
        self.machine.registers['DI'] = 0
        self.machine.flags['D'] = 1
        self.functionTable["STOSW"](['stosw'], 0)
        self.assertEqual(self.machine.addressSpace[0], 'h')
        self.assertEqual(self.machine.addressSpace[1], 'i')
        self.assertEqual(self.machine.registers['DI'], -2)

    def testSubSmallNumbers(self):
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = 2 ** 15 - 1
            self.functionTable["SUB"](['SUB', x, '1'], 0)
            self.assertEqual(self.machine.registers[x], 2 ** 15 - 2)

    def testSubSmallOverflow(self):
        for x in ['AX', 'BX', 'CX', 'DX']:
            self.machine.registers[x] = -2 ** 15
            self.functionTable["SUB"](['SUB', x, '1'], 43)
            self.assertEqual(self.machine.registers[x], 2 ** 15 - 1)

    def testXchg(self):
        self.machine.registers['AX'] = 23
        self.machine.registers['BX'] = -13

        self.functionTable['XCHG'](["XCHG", "AX", "BX"], 0)
        self.assertEqual(self.machine.registers['BX'], 23)
        self.assertEqual(self.machine.registers['AX'], -13)

    def testXor(self):
        self.machine.registers['AX'] = int('1101101', 2)
        self.machine.registers['BX'] = int('0110101', 2)
        self.functionTable["XOR"](["XOR", "AX", "BX"], 0)
        self.assertEqual(self.machine.registers["AX"], int("1011000", 2))

    def testInc(self):
        self.machine.registers['AX'] = 1
        self.functionTable['INC'](["INC", "AX"], 0)
        self.assertEqual(self.machine.registers['AX'], 2)

    def testDec(self):
        self.machine.registers['AX'] = 2
        self.functionTable['DEC'](["DEC", "AX"], 0)
        self.assertEqual(self.machine.registers['AX'], 1)

    def testIncMem(self):
        self.machine.BSS = {'test':[0, 2]}
        self.machine.addressSpace[0] = 0
        self.functionTable['INC'](["INC", 'test'], 0)
        self.assertEqual(self.machine.addressSpace[0], 1)

    def outPut(self, s):
        """ Necessary - the as88 interpreter calls the assemblers output methods when errors happen """
        print s

    def stopRunning(self, x=1):
        """ If stoprunning is passed, then something was broken! """
        self.fail("Stop running called")
        print "Fatal error"

if __name__ == "__main__":
    unittest.main()
