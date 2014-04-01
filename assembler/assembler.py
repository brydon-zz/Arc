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

from gi.repository import Gtk, Gdk, GObject, Pango
import CommandInterpreter, Intel8088

# TODO: issues with restarting
# TODO: Implement the WHOLE reg set
# TODO: ASSEMBLE? (i.e. opcodes)
# TODO: Run all and run untils with input
# TODO: Optimise the number of GUI interface calls. i.e. UpdateGUI should only update the gui parts who need updates
# TODO: (possibly related to prev) have the parts of the gui updated

""""Simulator Class for Intel 8088 Architecture"""
class Simulator(object):

    def __init__(self):

        """ Begin GUI """
        styles = """
#As88Window {
    background:#000;
}

#As88Window #code, #As88Window #outText, #As88Window #stack, #As88Window #regA, #As88Window #regB, #As88Window #regC, #As88Window #regD, #As88Window #regSP, #As88Window #regBP, #As88Window #regSI,#As88Window #regDI, #As88Window #regPC, #As88Window #regFlags, #As88Window #memory {
    background-color:#2F0B24;
    font-family:mono;
    color:#FFF;
}
"""
        """Handlers for the actions in the interface."""
        class Handler:
            def onDeleteWindow(self, *args):
                Gtk.main_quit(*args)

            def onOpen(self, button):
                Simulator.openFile()

            def onButtonClicked(self, button):
                Simulator.stepButtonClicked()

        # Make stuff from the GLADE file and setup events
        self.builder = Gtk.Builder()
        self.builder.add_from_file("xml/As88_Mockup.glade")
        self.builder.connect_signals(Handler())

        self.win = self.builder.get_object("window1")
        self.win.set_name('As88Window')

        # Set Up the CSS
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_data(styles)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Creating local vars for gui elements
        self.outText = self.builder.get_object("outText")
        self.code = self.builder.get_object("code")
        self.entry = self.builder.get_object("entry")
        self.stack = self.builder.get_object("stack")
        self.button = self.builder.get_object("button1")
        self.regA = self.builder.get_object("regA")
        self.regB = self.builder.get_object("regB")
        self.regC = self.builder.get_object("regC")
        self.regD = self.builder.get_object("regD")
        self.regBP = self.builder.get_object("regBP")
        self.regSP = self.builder.get_object("regSP")
        self.regSI = self.builder.get_object("regSI")
        self.regDI = self.builder.get_object("regDI")
        self.regPC = self.builder.get_object("regPC")
        self.regFlags = self.builder.get_object("regFlags")
        self.memory = self.builder.get_object("memory")
        self.hexSwitch = self.builder.get_object("hexSwitch")

        # Text buffers for the big text-views
        self.outBuffer = self.outText.get_buffer()
        self.codeBuffer = self.code.get_buffer()
        self.stackBuffer = self.stack.get_buffer()
        self.memoryBuffer = self.memory.get_buffer()

        # Names need set for CSS reasons only
        self.outText.set_name("outText")
        self.code.set_name("code")
        self.entry.set_name("entry")
        self.stack.set_name("stack")
        self.regA.set_name("regA")
        self.regB.set_name("regB")
        self.regC.set_name("regC")
        self.regD.set_name("regD")
        self.regBP.set_name("regBP")
        self.regSP.set_name("regSP")
        self.regSI.set_name("regSI")
        self.regDI.set_name("regDI")
        self.regPC.set_name("regPC")
        self.regFlags.set_name("regFlags")
        self.memory.set_name("memory")

        # Set up the text behaviour
        self.outText.set_wrap_mode(Gtk.WrapMode.WORD)
        self.code.set_wrap_mode(Gtk.WrapMode.WORD)
        self.memory.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.stack.set_justification(Gtk.Justification.CENTER)

        # Hex Switch needs a special trigger signal that glade cannot understand
        self.hexSwitch.connect('notify::active', self.hexSwitchClicked)
        # Key events!
        self.win.connect('key_press_event', self.onKeyPressEvent)
        self.win.connect('key_release_event', self.onKeyReleaseEvent)
        # Window Icon -> what shows up in unity bar/toolbar/etc.
        self.win.set_icon_from_file("images/icon.png")

        self.win.show_all()

        self.textTagBold = Gtk.TextTag()
        self.textTagBold.set_property("weight", Pango.Weight.BOLD)
        self.codeBuffer.get_tag_table().add(self.textTagBold)

        self.textTagMagenta = Gtk.TextTag()
        self.textTagMagenta.set_property("background", "magenta")
        self.textTagOrange = Gtk.TextTag()
        self.textTagOrange.set_property("background", "orange")
        self.textTagRed = Gtk.TextTag()
        self.textTagRed.set_property("background", "red")
        self.textTagBlue = Gtk.TextTag()
        self.textTagBlue.set_property("background", "blue")
        self.textTagPurple = Gtk.TextTag()
        self.textTagPurple.set_property("background", "purple")
        self.textTagGreen = Gtk.TextTag()
        self.textTagGreen.set_property("background", "green")
        self.textTagGrey = Gtk.TextTag()
        self.textTagGrey.set_property("background", "grey")

        self.memoryBuffer.get_tag_table().add(self.textTagGrey)
        self.memoryBuffer.get_tag_table().add(self.textTagRed)
        self.memoryBuffer.get_tag_table().add(self.textTagOrange)
        self.memoryBuffer.get_tag_table().add(self.textTagMagenta)
        self.memoryBuffer.get_tag_table().add(self.textTagGreen)
        self.memoryBuffer.get_tag_table().add(self.textTagBlue)
        self.memoryBuffer.get_tag_table().add(self.textTagPurple)

        self.memoryColours = [self.textTagRed, self.textTagOrange, self.textTagMagenta, self.textTagGreen, self.textTagBlue, self.textTagPurple, self.textTagGrey]

        self.memory.props.has_tooltip = True

        for x in self.memoryColours:
            self.memory.connect("query-tooltip", self.memoryToolTipOption, x)

        """ End GUI """
        # return string.replace("\n", "\\n").replace("\'", "\\'").replace('\"', '\\"').replace("\a", "\\a").replace("\b", "\\b").replace("\f", "\\f").replace("\r", "\\r").replace("\t", "\\t").replace("\v", "\\v")
        self.ESCAPE_CHARS = ['\b', '\n', '\v', '\t', '\f', "'", '"', '\a', '\r']
        self.inBuffer = ""
        self.fileName = None
        self.displayInHex = True
        self.getCharFlag = False

        self.machine = Intel8088.Intel8088()

        as88 = CommandInterpreter.CommandInterpreter(self, self.machine)

        self.commandArgs = as88.getCommandArgs()
        self.do = as88.getFunctionTable()
        # self.sysCodes = as88.getSysCodes()

        self.LIST_TYPE = type([1, 1])

        self.lineCount = 0

        self.mode = "head"
        self.running = False
        self.ran = False
        self.restartPrompt = False

        self.keysDown = []

    def memoryToolTipOption(self, widget, x, y, keyboard_tip, tooltip, data):
        """ For printing the tooltips in the memory textview """
        if keyboard_tip:  # if the tooltip is focus from the keyboard, get those bounds
            offset = widget.props.buffer.cursor_position
            ret = widget.props.buffer.get_iter_at_offset(offset)
        else:  # else get the bounds by the cursor
            coords = widget.window_to_buffer_coords(Gtk.TextWindowType.TEXT, x, y)
            ret = widget.get_iter_at_position(coords[0], coords[1])

        if ret[0].has_tag(data):
            offset = ret[0].get_offset()
            for element in self.machine.effectiveBSSandDATALocation:
                if self.machine.effectiveBSSandDATALocation[element][0] <= offset <= self.machine.effectiveBSSandDATALocation[element][1]:
                    if element in self.machine.BSS.keys(): tooltip.set_text("%s (from %s to %s)" % (element, self.machine.intToHex(self.machine.BSS[element][0]) if self.displayInHex else str(self.machine.BSS[element][0]), self.machine.intToHex(self.machine.BSS[element][1]) if self.displayInHex else str(self.machine.BSS[element][1])))
                    else: tooltip.set_text("%s (from %s to %s)" % (element, self.machine.intToHex(self.machine.DATA[element][0]) if self.displayInHex else str(self.machine.DATA[element][0]), self.machine.intToHex(self.machine.DATA[element][1]) if self.displayInHex else str(self.machine.DATA[element][1])))
                    break
        else:
            return False

        return True

    def onKeyPressEvent(self, widget, event):
        """ Handles Key Down events, puts the corresponding keyval into a list self.keysDown.
        Also checks for key combinations. """
        keyname = Gdk.keyval_name(event.keyval)

        if keyname == 'Return' or keyname == 'KP_Enter':
            if not self.getCharFlag:
                if "Shift_R" in self.keysDown or "Shift_L" in self.keysDown:
                    self.stepButtonClicked(self.entry.get_text())
                    self.entry.set_text("")
                else:
                    self.stepButtonClicked()
            else:
                self.inBuffer = self.entry.get_text() + "\n"
                self.machine.registers["AX"] = ord(self.inBuffer[0])
                self.outPut(self.inBuffer + "\n")
                self.inBuffer = self.inBuffer[1:]
                self.getCharFlag = False
            return

        if not keyname in self.keysDown: self.keysDown.append(keyname)

        if ('O' in self.keysDown or 'o' in self.keysDown) and ('Control_L' in self.keysDown or 'Control_R' in self.keysDown):
            self.keysDown = []
            self.openFile()

    def onKeyReleaseEvent(self, widget, event):
        """ Handes Key Up events, removes the corresponding keyval from the list self.keysDown. """
        keyname = Gdk.keyval_name(event.keyval)

        if keyname in self.keysDown: self.keysDown.remove(keyname)

    def openFile(self):
        """Opens up a file dialog to select a file then reads that file in to the assembler. """

        self.fileName = None
        self.ran = False

        self.fileChooser = Gtk.FileChooserDialog(title="Choose A File", parent=self.win, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = self.fileChooser.run()

        if response == Gtk.ResponseType.OK:
            self.fileName = self.fileChooser.get_filename()

        self.fileChooser.destroy()

        if self.fileName == None:
            return None

        try:
            f = open(self.fileName, 'r')

            self.codeBuffer.set_text(f.read())

            f.seek(0)

            self.syntaxHighlight(f)

            f.close()

        except IOError:
            self.outPut("There was a fatal issue opening " + self.fileName + ". Are you sure it's a file?")

    def syntaxHighlight(self, f):
        return

    def startRunning(self):
        """Starts the whole sha-bang.
        First pass for forward references, and setting up local vars, etc.
        The self.running flag is set so the user can step thru accordingly. """

        self.ran = False

        # self.clearGui()
        # GObject.idle_add(lambda: self.codeBuffer.set_text(self.codeString))

        self.updateRegisters()
        self.code.set_editable(False)

        self.lines = self.codeBuffer.get_text(self.codeBuffer.get_start_iter(), self.codeBuffer.get_end_iter(), False).split("\n")

        self.lineCount = 0

        self.mode = "head"
        self.machine.restart()

        errorCount = 0

        BSScount = 0

        # This for Loop is gonna go thru the lines, set up a nice lookUp table for jumps
        # and record program start and end. and set up some memory stuff.

        """ FIRST PASS """

        for line in self.lines:
            # Looping thru every line
            # we will go thru, at most, 4 modes
            # a "head" mode - where constants are defined
            #      eg _EXIT = 1 etc.
            # a "text" mode (".SECT .TEXT") where the code is located
            #      on the first loop thru we just keep track of where this is, and set up a jump table
            # a "data" mode (".SECT .DATA") where variables are defined
            #      str: .ASCIZ "%s f"
            # a "bss" mode (".SECT .BSS") where memory chunks are defined
            #      fdes: .SPACE 2
            line = line.strip()

            if "!" in line:
                line = line[:line.find("!")].strip()  # ignore comments

            self.lineCount += 1

            if self.mode == "head" and "=" in line:
                line = line.split('=')
                line[0] = line[0].strip()
                line[1] = line[1].strip()
                if line[0] in self.machine.localVars.keys():
                    self.outPut("Error on line " + str(self.lineCount) + ", cannot define \''" + line[0] + "\' more than once.")
                    errorCount += 1
                else: self.machine.localVars[line[0]] = line[1]
                continue

            if ".SECT" in line:

                # record where the .SECT .TEXT section starts, and ends
                if self.mode == ".SECT .TEXT":  # ends, we've gone one too far, but we count from zero
                    self.machine.codeBounds[1] = self.lineCount - 1
                elif line == ".SECT .TEXT":  # starts, we're one too short, and we count from zero
                    self.machine.codeBounds[0] = self.lineCount

                self.mode = line
                continue

            if ":" in line:  # Spliting on a colon, for defining vars, or jump locations, etc.
                temp = line.split(":")[0]
                if self.mode == ".SECT .TEXT":
                    # a : in .SECT .TEXT means a jump location
                    # we can define multiple jump locations by digits
                    # but only one by ascii per each ascii name

                    if temp not in self.machine.lookupTable.keys():
                        self.machine.lookupTable[temp] = self.lineCount
                    else:
                        if temp.isdigit():  # If we're defining multiple jump locations for one digit, keep a list
                            if type(self.machine.lookupTable[temp]) == self.LIST_TYPE:
                                self.machine.lookupTable[temp].append(self.lineCount)
                            else:
                                self.machine.lookupTable[temp] = [self.machine.lookupTable[temp], self.lineCount]
                        else:
                            self.outPut("Duplicate entry: \"" + temp + "\" on line " + str(self.lineCount) + " and line " + str(self.machine.lookupTable[temp]))
                            errorCount += 1
                elif self.mode == ".SECT .DATA":
                    # info in .SECT .DATA follows the format
                    # str: .ASCIZ "hello world"
                    # where .ASCIZ means an ascii string with a zero at the end
                    # and .ASCII means an ascii string

                    if ".ASCIZ" in line or ".ASCII" in line:  # If we're dealing with a string
                        if line.count("\"") < 2:  # each string to be defined should be in quotes, raise error if quotes are messed
                            self.outPut("fatal error on line " + str(self.lineCount))
                            errorCount += 1
                            return None
                        temp2 = self.replaceEscapedSequences(line[line.find("\"") + 1:line.rfind("\"")])  # otherwise grab the stuff in quotes
                        self.machine.DATA[temp] = [BSScount, BSScount + len(temp2) + (".ASCIZ" in line) - 1]  # and set temp equal to a list of hex vals of each char
                        self.machine.addressSpace[BSScount:BSScount + len(temp2)] = temp2 + "0"*(".ASCIZ" in line)
                        BSScount += len(temp2) + (".ASCIZ" in line)

                elif self.mode == ".SECT .BSS":
                    # info in .SECT .BSS follows the format
                    # fdes: .SPACE 2
                    # Where essentially .BSS just defines memory space

                    temp2 = line.split(".SPACE")[1]  # let's find the size of the mem chunk to def
                    self.machine.BSS[temp.strip()] = [BSScount, BSScount + int(temp2.strip()) - 1]  # and def it in bss as it's start and end pos
                    BSScount += int(temp2.strip())

        # TODO: error check before second pass
        """ SECOND PASS """
        if errorCount == 0:
            self.machine.registers['PC'] = self.machine.codeBounds[0]
            self.running = True
        else:
            self.outPut("Your code cannot be run, it contains %d errors" % errorCount)

    def updateStack(self, data=""):
        """ Updates the stack gui element """
        # self.outBuffer.apply_tag(self.textTagBold, self.outBuffer.get_start_iter(), self.outBuffer.get_end_iter())
        if data != "": self.machine.stackData.append(str(data))
        if self.displayInHex:
            GObject.idle_add(lambda: self.stackBuffer.set_text("\n".join(["0"*(4 - len(hex(int(x)).split("x")[1])) + hex(int(x)).split("x")[1] for x in self.machine.stackData])))
        else:
            GObject.idle_add(lambda: self.stackBuffer.set_text("\n".join(["0"*(4 - len(str(x))) + str(x) for x in self.machine.stackData])))

    def outPut(self, string, i=""):
        """ Outputs the arguments, in the fashion i: string"""
        if i == "":
            GObject.idle_add(lambda: (self.outText.get_buffer().insert(self.outText.get_buffer().get_end_iter(), ">> " + string),
                    self.outText.scroll_to_iter(self.outText.get_buffer().get_end_iter(), 0.1, True, .5, .5)))

    def clearGui(self):
        """ Empties the text buffers of all relevant GUI elements"""
        GObject.idle_add(lambda: (self.outText.get_buffer().set_text(""),
                            self.code.get_buffer().set_text(""),
                            self.regA.get_buffer().set_text(""),
                            self.regB.get_buffer().set_text(""),
                            self.regC.get_buffer().set_text(""),
                            self.regD.get_buffer().set_text(""),
                            self.regBP.get_buffer().set_text(""),
                            self.regSP.get_buffer().set_text(""),
                            self.regDI.get_buffer().set_text(""),
                            self.regSI.get_buffer().set_text(""),
                            self.regPC.get_buffer().set_text(""),
                            self.regFlags.get_buffer().set_text(""),
                            self.memory.get_buffer().set_text("")))

    def getChar(self):
        """ Get's chars from the entry element. Interfaces with as88 system trap """
        if self.inBuffer == "":
            self.getCharFlag = True
            self.outPut("Waiting for input:")
        else:
            self.outPut(self.inBuffer + "\n")
            self.machine.registers['AX'] = ord(self.inBuffer[0])
            self.inBuffer = self.inBuffer[1:]

    def colourMemory(self):
        """ Colour codes the items in the memory for easy identification """
        # TODO: Optimize this so that it doesn't highlight things way off in memory that aren't displayed?
        backSlashOffsetBeforeTag = 0
        backSlashOffsetAfterTag = 0
        sortedBSSandDATAList = []

        for index, name in enumerate(self.machine.DATA.keys() + self.machine.BSS.keys()):

            if name in self.machine.DATA.keys(): location = self.machine.DATA[name]
            else: location = self.machine.BSS[name]

            if len(sortedBSSandDATAList) == 0:
                sortedBSSandDATAList.append([location[0], location[1], name])
            else:
                for index, element in enumerate(sortedBSSandDATAList):
                    if location[0] < element[1]:
                        sortedBSSandDATAList.insert(index, [location[0], location[1], name])
                        break
                else:
                    sortedBSSandDATAList.append([location[0], location[1], name])

        for index, location in enumerate(sortedBSSandDATAList):
            backSlashOffsetBeforeTag = backSlashOffsetAfterTag
            for x in self.machine.addressSpace[location[0]:location[1]]:
                if x in self.ESCAPE_CHARS:
                    backSlashOffsetAfterTag += 1
            before = location[0] * (self.displayInHex + 1) + backSlashOffsetBeforeTag
            after = (location[1] + 1) * (self.displayInHex + 1) + backSlashOffsetAfterTag

            self.machine.effectiveBSSandDATALocation[location[2]] = [before, after]

            self.memoryBuffer.apply_tag(self.memoryColours[index % len(self.memoryColours)], self.memoryBuffer.get_iter_at_offset(before), self.memoryBuffer.get_iter_at_offset(after))

    def updateRegisters(self):
        """ Simply put, updates the register gui elements with the values of the registers. """

        flagStr = "  %-5s %-5s %-5s %-5s %-5s %-1s\n  %-6d%-6d%-6d%-6d%-6d%-1d" % (self.machine.flags.keys()[0], self.machine.flags.keys()[1], self.machine.flags.keys()[2], self.machine.flags.keys()[3], self.machine.flags.keys()[4], self.machine.flags.keys()[5], int(self.machine.flags.values()[0]), int(self.machine.flags.values()[1]), int(self.machine.flags.values()[2]), int(self.machine.flags.values()[3]), int(self.machine.flags.values()[4]), int(self.machine.flags.values()[5]))

        if self.displayInHex:
            GObject.idle_add(lambda: (self.regA.get_buffer().set_text("AX: %s\n AH: %s\n AL: %s" % ("0"*(4 - len(self.machine.intToHex(self.machine.registers['AX']))) + self.machine.intToHex(self.machine.registers['AX']), "0"*(2 - len(self.machine.intToHex(self.machine.getEightBitRegister('AH')))) + self.machine.intToHex(self.machine.getEightBitRegister("AH")), "0"*(2 - len(self.machine.intToHex(self.machine.getEightBitRegister('AL')))) + self.machine.intToHex(self.machine.getEightBitRegister('AL')))),
                                self.regB.get_buffer().set_text("BX: %s\n BH: %s\n BL: %s" % ("0"*(4 - len(self.machine.intToHex(self.machine.registers['BX']))) + self.machine.intToHex(self.machine.registers['BX']), "0"*(2 - len(self.machine.intToHex(self.machine.getEightBitRegister('BH')))) + self.machine.intToHex(self.machine.getEightBitRegister("BH")), "0"*(2 - len(self.machine.intToHex(self.machine.getEightBitRegister('BL')))) + self.machine.intToHex(self.machine.getEightBitRegister("BL")))),
                                self.regC.get_buffer().set_text("CX: %s\n CH: %s\n CL: %s" % ("0"*(4 - len(self.machine.intToHex(self.machine.registers['CX']))) + self.machine.intToHex(self.machine.registers['CX']), "0"*(2 - len(self.machine.intToHex(self.machine.getEightBitRegister('CH')))) + self.machine.intToHex(self.machine.getEightBitRegister("CH")), "0"*(2 - len(self.machine.intToHex(self.machine.getEightBitRegister('CL')))) + self.machine.intToHex(self.machine.getEightBitRegister("CL")))),
                                self.regD.get_buffer().set_text("DX: %s\n DH: %s\n DL: %s" % ("0"*(4 - len(self.machine.intToHex(self.machine.registers['DX']))) + self.machine.intToHex(self.machine.registers['DX']), "0"*(2 - len(self.machine.intToHex(self.machine.getEightBitRegister('DH')))) + self.machine.intToHex(self.machine.getEightBitRegister("DH")), "0"*(2 - len(self.machine.intToHex(self.machine.getEightBitRegister('DL')))) + self.machine.intToHex(self.machine.getEightBitRegister("DL")))),
                                self.regBP.get_buffer().set_text("BP: " + str(hex(self.machine.registers['BP']).split("x")[1])),
                                self.regSP.get_buffer().set_text("SP: " + str(hex(self.machine.registers['SP']).split("x")[1])),
                                self.regDI.get_buffer().set_text("DI: " + str(hex(self.machine.registers['DI']).split("x")[1])),
                                self.regSI.get_buffer().set_text("SI: " + str(hex(self.machine.registers['SI']).split("x")[1])),
                                self.regPC.get_buffer().set_text("PC: " + str(hex(self.machine.registers['PC']).split("x")[1])),
                                self.regFlags.get_buffer().set_text(flagStr),
                                self.memoryBuffer.set_text("".join([self.machine.intToHex(ord(x)) for x in self.machine.addressSpace[:144]])),
                                self.colourMemory()
                                ))
        else:
            GObject.idle_add(lambda: (self.regA.get_buffer().set_text("AX: %d\n AH: %d\n AL: %d" % (self.machine.registers['AX'], self.machine.getEightBitRegister("AH"), self.machine.getEightBitRegister('AL'))),
                                self.regB.get_buffer().set_text("BX: %d\n BH: %d\n BL: %d" % (self.machine.registers['BX'], self.machine.getEightBitRegister("BH"), self.machine.getEightBitRegister("BL"))),
                                self.regC.get_buffer().set_text("CX: %d\n CH: %d\n CL: %d" % (self.machine.registers['CX'], self.machine.getEightBitRegister("CH"), self.machine.getEightBitRegister("CL"))),
                                self.regD.get_buffer().set_text("DX: %d\n DH: %d\n DL: %d" % (self.machine.registers['DX'], self.machine.getEightBitRegister("DH"), self.machine.getEightBitRegister("DL"))),
                                self.regBP.get_buffer().set_text("BP: " + str(self.machine.registers['BP'])),
                                self.regSP.get_buffer().set_text("SP: " + str(self.machine.registers['SP'])),
                                self.regDI.get_buffer().set_text("DI: " + str(self.machine.registers['DI'])),
                                self.regSI.get_buffer().set_text("SI: " + str(self.machine.registers['SI'])),
                                self.regPC.get_buffer().set_text("PC: " + str(self.machine.registers['PC'])),
                                self.regFlags.get_buffer().set_text(flagStr),
                                self.memory.get_buffer().set_text("".join([self.escapeSequences(x) for x in self.machine.addressSpace[:287]])),
                                self.colourMemory()
                                ))

    def stepButtonClicked(self, injectedLine=""):
        print "no MY stbc"
        """ Defines what happens if the step button is clicked.
        If the entry text field is empty, step like normal.
        If the entry text field has a command in it execute accordingly
        If the entry text field has characters in it, that aren't recognised as a command, clear the entry and do nothing.
        """
        # Scroll to view the line
        self.code.scroll_to_iter(self.code.get_buffer().get_iter_at_line(self.machine.registers['PC']), 0.25, True, .5, .5)

        # Inject Line stuff, up for Del??
        text = self.entry.get_text().lower().strip()
        if injectedLine != "" or text == "":
            if self.ran:
                if not self.restartPrompt:
                    self.outPut("Do you wish to restart? (y/n)")
                    self.restartPrompt = True
            elif self.running:
                self.step(injectedLine)
        else:
            if text == "restart":
                if self.running or self.ran: self.startRunning()
            elif text == "y":
                if self.restartPrompt:
                    self.startRunning()
                    self.restartPrompt = False
            elif text == "clear":
                self.clearGui()
            elif self.running:
                tempList = text.split()
                if tempList[0] == "run" and tempList[1] == "until" and tempList[2].isdigit():
                    n = int(tempList[2])
                    if n >= self.machine.codeBounds[0] and n < self.machine.codeBounds[1]:
                        while self.running:
                            if self.machine.registers['PC'] == int(tempList[2]):
                                self.step()
                                break
                            self.step()

                        if self.machine.registers['PC'] != int(tempList[2]) + 1:
                            self.outPut("The program exited before it ever reached line " + tempList[2])
                    else:
                        self.outPut("That line number is not within the bounds of the program.")
                elif tempList[0] == "run" and tempList[1] == "all":
                    while self.running:
                        self.step()

            GObject.idle_add(lambda: self.entry.set_text(""))

        # insert a >
        iter = self.codeBuffer.get_iter_at_line(self.machine.registers['PC'])
        self.codeBuffer.insert(iter, ">")

        # remove the > from the previous line, -1 means we're at the first line
        if self.machine.lastLine != -1:
            start = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 0)
            end = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 1)
            self.codeBuffer.delete(start, end)

    def step(self, injectedLine=""):
        print "no MY step"
        """ The guts of the second pass. Where the magic happens! """
        if self.running:

            if self.machine.registers['PC'] >= self.machine.codeBounds[1]:
                self.stopRunning()
                return

            if injectedLine == "":
                line = self.lines[self.machine.registers['PC']].replace("\t", "")  # clear out tabs
            else:
                line = injectedLine

            if "!" in line:  # exclamations mean comments
                line = line[:line.find("!")].strip()  # ignore comments

            if ":" in line:  # colons mean labels, we dealt with those already.
                line = line[line.find(":") + 1:].strip()  # ignore jump points

            if injectedLine == "":
                self.outPut(line, self.machine.registers['PC'])  # Now the line is ready to work with
            else:
                self.outPut(line + "\n")


            if line.count(",") > 1:  # any command can have at most 2 arguments.
                self.outPut("What's up with all the commas on line " + str(self.machine.registers['PC']) + "?")
                self.running = False
                self.ran = True
                return -1

            command = [x.strip() for x in line.replace(" ", ",").split(",")]

            for x in range(command.count("")):
                command.remove("")

            if command == None or command == []:
                if injectedLine == "":
                    self.machine.lastLine = self.machine.registers['PC']
                    self.machine.registers['PC'] += 1
                return  # skip nothing lines, yo.

            if command[0] not in self.commandArgs.keys():
                print "Missing " + command[0] + " from self.commandArgs"
                self.machine.lastLine = self.machine.registers['PC']
                self.machine.registers['PC'] += 1
                return

            if len(command) - 1 != self.commandArgs[command[0]]:
                self.outPut("Invalid number of arguments on line " + str(self.machine.registers['PC']) + ". " + command[0] + " expects " + str(self.commandArgs[command[0]]) + " argument" + "s"*(self.commandArgs[command[0]] > 1) + " and " + str(len(command) - 1) + (" were " if len(command) - 1 > 1 else " was ") + "given.")
                print command[:]
                self.running = False
                self.ran = True
                return -1

            if command[0] in self.do.keys():
                self.do[command[0]](command, self.machine.registers['PC'])
                self.updateRegisters()
            else:
                1 + 1  # TODO: we do nothing right now, once all are implemented we'll throw errors for this sorta thing TODO

            if self.machine.jumpLocation != -1:
                self.machine.registers['PC'] = self.machine.jumpLocation
                self.machine.jumpLocation = -1
            elif injectedLine == "":
                self.machine.lastLine = self.machine.registers['PC']
                self.machine.registers['PC'] += 1

            if self.machine.registers['PC'] >= self.machine.codeBounds[1]:
                self.stopRunning()
                return

    def stopRunning(self, i=1):
        """ Ends the current simulation, if i=1 then succesfully, otherwise there was an issue """
        self.running = False
        self.ran = True
        self.code.set_editable(True)

        if i == 1:
            self.outPut("\n----\nCode executed succesfully.")
        else:
            self.outPut("\n----\nCode execution terminated.")
        # TODO: EOF, anything important like that should go here.

    def hexSwitchClicked(self, button=None, data=None):
        """ gets called when the hex switch is toggled """
        self.displayInHex = not self.displayInHex
        self.updateRegisters()
        self.updateStack()

    def replaceEscapedSequences(self, string):
        """ Replaces all escaped sequences with their unescaped counterparts """
        return string.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"').replace("\\a", "\a").replace("\\b", "\b").replace("\\f", "\f").replace("\\r", "\r").replace("\\t", "\t").replace("\\v", "\v")

    def escapeSequences(self, string):
        """ Escapes all things that may need escaped. """
        return string.replace("\n", "\\n").replace("\'", "\\'").replace('\"', '\\"').replace("\a", "\\a").replace("\b", "\\b").replace("\f", "\\f").replace("\r", "\\r").replace("\t", "\\t").replace("\v", "\\v")
