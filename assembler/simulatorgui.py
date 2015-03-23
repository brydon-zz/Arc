"""
The Simulator's GUI
Uses the GTK3 library. Features include

    - Development Environment with Syntax Highlighting
    - Simulates the execution of 8088 Assembly Code
    - Provides Graphical Representation of Registers, Memory, and Stack
    - Helpful Documentation of the Instruction Set.

The interface loads in the basic structure from an XML file and styles
it according to a CSS file. It then creates an Intel 8088 Machine.
You can load in assembly language files and edit them in place then
simulate them. Stepping through code one line at a time or executing
the whole lot. You can set breakpoints for ease of debugging.

The simulator passes the command to the Intel 8088 Machine.
The GUI displays the values of the registers, stack, and memory.

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

from gi.repository import Gdk, GdkPixbuf, GObject, Gtk, Pango
from CodeStates import TextStates
import intel8088
import readliner
import entrydialog
import sys
import os
import tokenize
import time
sys.setrecursionlimit(50)

""""Simulator Class for Intel 8088 Architecture"""
# TODO: when pasting syntax highlighting is ignored, probs not the best.
# TODO: when running code it should open the side bar if not already.
# TODO: Do i wanna refactor the parser into it's own class?


class Simulator(object):
    _PROGRAMNAME = "Arc"
    _VERSION = "0.5"
    _DESCRIPTION = "A Program for Writing and Simulating\
 Intel 8088 Assembly Code"
    _WEBSITE = "http://www.beastman.ca/"
    _LICENSE = Gtk.License.GPL_2_0
    _PATHDELIM = os.path.sep
    _CSSFILENAME = "default.css"
    _INTERFACEXMLFILENAME = "defaultInterface.xml"
    _DOUBLECLICKTIME = 0.2
    _MAXSTACKLINES = 29
    _SAVE_STATE_TIME = 0.5
    # the time, in seconds, between clicks that determines a double click

    def __init__(self):
        localDir = os.path.dirname(os.path.realpath(__file__))
        self._PATH = self._PATHDELIM.join(localDir.split(self._PATHDELIM)[:-1])
        print self._PATH

        """ Begin GUI """
        cssFile = self._PATHDELIM.join([self._PATHDELIM + "styles",
                                        self._CSSFILENAME])

        styles = open(self._PATH + cssFile, 'r').read()

        self.codeStates = TextStates()
        self.timer = time.time()
        self.updateAll = False
        self.fileIconTable = {};

        """Handlers for the actions in the interface."""

        self.fileName = None
        self.shrunk = False
        self.breakpointDClickTime = 0
        # Make stuff from the GLADE file and setup events
        self.builder = Gtk.Builder()
        xmlPath = [self._PATHDELIM + "xml", self._INTERFACEXMLFILENAME]
        self.builder.add_from_file(self._PATH + self._PATHDELIM.join(xmlPath))

        self.win = self.builder.get_object("window")
        self.win.set_name('As88Window')

        # Set Up the CSS
        # Creating local vars for gui elements
        self.assignGuiElementsToVariables()

        # Text buffers for the big text-views
        self.setupTextBuffers()
        self.makeFileButtons()

        self.connectSignals()

        self.nameGuiElementsForCSS()
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_data(styles)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
                                    self.style_provider,
                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Window Icon -> what shows up in unity bar/toolbar/etc.
        iconPath = [self._PATHDELIM + "images", "icon.png"]
        self.win.set_icon_from_file(self._PATH +
                                    self._PATHDELIM.join(iconPath))

        self.setUpTextTags()

        self.memory.props.has_tooltip = True

        self.memory.connect('query-tooltip', self.stackToolTip, self.stackColour)
        # self.notebook.set_visible(False)
        for x in self.memoryColours:
            self.memory.connect("query-tooltip", self.memoryToolTipOption, x)

        self.updateLineCounter()

        """ End GUI """

        self.downFile = ""

        self.machine = intel8088.Intel8088()

        self.new()

        self.updateStatusLabel()

        self.ESCAPE_CHARS = ['\b', '\n', '\v', '\t',
                             '\f', "'", '"', '\a', '\r']

        self.displayInHex = True

        self.LIST_TYPE = type([1, 1])

        # Two Final GUI elements
        self.win.show_all()

        # This GUI element needs the as88 defined
        self.makeHelpBox()

        self.clickSeperator(None, None)

    def setBreakpoint(self, widget, event):
        if self.breakpointDClickTime == 0:
            self.breakpointDClickTime = time.time()
        else:
            if time.time() - self.breakpointDClickTime > self._DOUBLECLICKTIME:
                self.breakpointDClickTime = time.time()
                return

            self.breakpointDClickTime = 0
            breakPoint = self.lineNumberTV.get_iter_at_location(event.x,
                                                            event.y).get_line()

            start = self.linesBuffer.get_iter_at_line(breakPoint)

            if breakPoint + 1 == self.linesBuffer.get_line_count():
                end = self.linesBuffer.get_end_iter()
            else:
                end = self.linesBuffer.get_iter_at_line_offset(breakPoint + 1,
                                                               0)

            if self.machine.isBreakPoint(breakPoint):
                self.machine.removeBreakPoint(breakPoint)
                self.linesBuffer.remove_tag(self.textTagBreakpoint, start, end)
            else:
                self.machine.addBreakPoint(breakPoint)
                self.linesBuffer.apply_tag(self.textTagBreakpoint, start, end)

    def openFileDialog(self):
        """Opens up a file dialog to select a file
        then reads that file in to the assembler. """

        fileChooser = Gtk.FileChooserDialog(title="Choose A File",
                                            parent=self.win,
                                            buttons=(Gtk.STOCK_CANCEL,
                                                     Gtk.ResponseType.CANCEL,
                                                     Gtk.STOCK_OPEN,
                                                     Gtk.ResponseType.OK))
        response = fileChooser.run()

        fileName = None
        if response == Gtk.ResponseType.OK:
            fileName = fileChooser.get_filename()

        fileChooser.destroy()

        if fileName is None:
            return

        self.openFile(fileName)

    def openFile(self, fileName):
        """ Opens and reads in the file fileName """

        try:
            self.new()
            self.fileName = None

            f = open(fileName, 'r')

            self.codeString = f.read()

            self.codeBuffer.set_text(self.codeString)

            f.seek(0)

            self.syntaxHighlight(f)

            f.close()

            self.outBuffer.set_text("")
            self.fileName = fileName
            self.updateWindowTitle()

        except IOError:
            self.outPut("There was a fatal issue opening " + fileName
                        + ". Are you sure it's a file?")

    def clickSeperator(self, *_):
        """When the separator label is clicked, expand the viewport."""
        if self.shrunk:
            self.notebook.set_visible(True)
            self.separatorLabel.set_angle(90)
            self.separatorLabel.set_text("^ hide ^")
            self.shrunk = False
        else:
            self.notebook.set_visible(False)
            self.separatorLabel.set_angle(270)
            self.separatorLabel.set_text("^ show ^")
            self.shrunk = True

    def syntaxHighlight(self, f, lineOffset=0):
        """Highlight the syntax of the text in the codeBuffer."""
        self.commentLine = -1

        def handleSyntaxHighlightingToken(typeOfToken, token, (srow, scol),
                                          (erow, ecol), line):
            """Get's called by tokenizer to handle each token."""

            tokenStart = self.codeBuffer.get_iter_at_line_offset(lineOffset
                                                           + srow - 1, scol)

            if lineOffset + srow == self.codeBuffer.get_line_count():
                endOfLine = self.codeBuffer.get_end_iter()
            else:
                endOfLine = self.codeBuffer.get_iter_at_line_offset(lineOffset
                                                                    + srow, 0)

            tokenRep = repr(token).strip("'")

            if tokenize.tok_name[typeOfToken] == "ENDMARKER":
                self.updateLineCounter()
            elif repr(token) == "'!'":
                self.commentLine = line

                self.codeBuffer.apply_tag(self.textTagLightGreyText,
                                          tokenStart, endOfLine)

            comment = self.commentLine == line

            if tokenize.tok_name[typeOfToken] == "NAME":
                tokenEnd = self.codeBuffer.get_iter_at_line_offset(lineOffset +
                                                               erow - 1, ecol)
                if not comment:
                    self.codeBuffer.remove_all_tags(tokenStart, tokenEnd)
                    if tokenRep in self.functions:
                        self.codeBuffer.apply_tag(self.textTagBold,
                                                  tokenStart, tokenEnd)

                    elif tokenRep in self.machine.getRegisterNames():
                        self.codeBuffer.apply_tag(self.textTagBold,
                                                  tokenStart, tokenEnd)
                        self.codeBuffer.apply_tag(self.textTagBlueText,
                                                  tokenStart, tokenEnd)

                    elif tokenRep in self.machine.getEightBitRegisterNames():
                        self.codeBuffer.apply_tag(self.textTagBlueText,
                                                  tokenStart, tokenEnd)

                    elif tokenRep in ["SECT", "DATA", "BSS", "TEXT"]:
                        self.codeBuffer.apply_tag(self.textTagBold,
                                                  tokenStart, tokenEnd)
                        self.codeBuffer.apply_tag(self.textTagGreyText,
                                                  tokenStart, tokenEnd)

                    else:
                        self.codeBuffer.apply_tag(self.textTagRedText,
                                                  tokenStart, tokenEnd)
            elif tokenize.tok_name[typeOfToken] == "NUMBER":
                tokenEnd = self.codeBuffer.get_iter_at_line_offset(
                                                lineOffset + erow - 1, ecol)
                if not comment:
                    self.codeBuffer.remove_all_tags(tokenStart, tokenEnd)
                    self.codeBuffer.apply_tag(self.textTagGreenText,
                                          tokenStart, tokenEnd)

        try:
            tokenize.tokenize(f.readline, handleSyntaxHighlightingToken)
        except Exception:
            """ Let slide.
            This is called if there is incorrect indentation, etc,
            in the source being read """

    def hoverOverSeperator(self, a, b):
        """Change the style of the separator label when hovered on."""
        self.separatorLabel.set_name("separatorLabelOver" + str(self.shrunk))

    def hoverOffSeperator(self, a, b):
        """Change the style of the separator label when hovered off."""
        self.separatorLabel.set_name("separatorLabel" + str(self.shrunk))

    def updateLineCounter(self):
        """Updates the line number label on the left of the code block.
        get's called whenever the lines change."""
        lines = [" " + str(x) for x in range(self.codeBuffer.get_line_count())]
        self.linesBuffer.set_text("\n".join(lines))

    def updateRegisters(self):
        """ Simply put, updates the register, flags, and memory gui elements
        with their respective values. """
        if self.machine.isRunningAll():
            return
        # if the user's clicked the runAll button, then theres no
        # point updating every iter. it's inefficient

        self.oFlagOutMachine.set_text(str(int(self.machine.getFlag('O'))))
        self.dFlagOutMachine.set_text(str(int(self.machine.getFlag('D'))))
        self.iFlagOutMachine.set_text(str(int(self.machine.getFlag('I'))))
        self.sFlagOutMachine.set_text(str(int(self.machine.getFlag('S'))))
        self.zFlagOutMachine.set_text(str(int(self.machine.getFlag('Z'))))
        self.aFlagOutMachine.set_text(str(int(self.machine.getFlag('A'))))
        self.pFlagOutMachine.set_text(str(int(self.machine.getFlag('P'))))
        self.cFlagOutMachine.set_text(str(int(self.machine.getFlag('C'))))

        if self.displayInHex:
            hexA = self.machine.intToHex(self.machine.getRegister('AX'))
            regAText = "0" * (4 - len(hexA)) + hexA
            regALText = self.machine.intToHex(
                                      self.machine.getEightBitRegister('AL'))
            regAHText = self.machine.intToHex(
                                      self.machine.getEightBitRegister('AH'))

            hexB = self.machine.intToHex(self.machine.getRegister('BX'))
            regBText = "0" * (4 - len(hexB)) + hexB
            regBLText = self.machine.intToHex(
                                      self.machine.getEightBitRegister('BL'))
            regBHText = self.machine.intToHex(
                                      self.machine.getEightBitRegister('BH'))

            hexC = self.machine.intToHex(self.machine.getRegister('CX'))
            regCText = "0" * (4 - len(hexC)) + hexC
            regCLText = self.machine.intToHex(
                                      self.machine.getEightBitRegister('CL'))
            regCHText = self.machine.intToHex(
                                      self.machine.getEightBitRegister('CH'))

            hexD = self.machine.intToHex(self.machine.getRegister('DX'))
            regDText = "0" * (4 - len(hexD)) + hexD
            regDLText = self.machine.intToHex(
                                      self.machine.getEightBitRegister('DL'))
            regDHText = self.machine.intToHex(
                                      self.machine.getEightBitRegister('DH'))

            hexBP = self.machine.intToHex(self.machine.getRegister('BP'))
            regBPText = "0" * (4 - len(hexBP)) + hexBP
            hexSP = self.machine.intToHex(self.machine.getRegister('SP'))
            regSPText = "0" * (4 - len(hexSP)) + hexSP
            hexDI = self.machine.intToHex(self.machine.getRegister('DI'))
            regDIText = "0" * (4 - len(hexDI)) + hexDI
            hexSI = self.machine.intToHex(self.machine.getRegister('SI'))
            regSIText = "0" * (4 - len(hexSI)) + hexSI
            hexPC = self.machine.intToHex(self.machine.getRegister('PC'))
            regPCText = "0" * (4 - len(hexPC)) + hexPC

            memToDisplay = [self.machine.intToHex(ord(x))
                            for x in self.machine.getFromMemoryAddress(0, 1024)]

            self.memoryBuffer.set_text("".join(memToDisplay))

            self.colourMemory()
        else:
            regAText = str(self.machine.getRegister('AX'))
            regAHText = str(self.machine.getEightBitRegister('AH'))
            regALText = str(self.machine.getEightBitRegister('AL'))

            regBText = str(self.machine.getRegister('BX'))
            regBHText = str(self.machine.getEightBitRegister('BH'))
            regBLText = str(self.machine.getEightBitRegister('BL'))

            regCText = str(self.machine.getRegister('CX'))
            regCHText = str(self.machine.getEightBitRegister('CH'))
            regCLText = str(self.machine.getEightBitRegister('CL'))

            regDText = str(self.machine.getRegister('DX'))
            regDHText = str(self.machine.getEightBitRegister('DH'))
            regDLText = str(self.machine.getEightBitRegister('DL'))

            regBPText = str(self.machine.getRegister('BP'))
            regSPText = str(self.machine.getRegister('SP'))
            regPCText = str(self.machine.getRegister('PC'))
            regDIText = str(self.machine.getRegister('DI'))
            regSIText = str(self.machine.getRegister('SI'))

            memToDisplay = self.machine.getFromMemoryAddress(0, 1024)

            escapedMem = [self.machine.escapeSequences(
                           self.makeCharPrintable(x)) for x in memToDisplay]

            self.memoryBuffer.set_text("".join(escapedMem))

        self.regA.set_text(regAText)
        self.regAL.set_text(regALText)
        self.regAH.set_text(regAHText)
        self.regB.set_text(regBText)
        self.regBL.set_text(regBLText)
        self.regBH.set_text(regBHText)
        self.regC.set_text(regCText)
        self.regCL.set_text(regCLText)
        self.regCH.set_text(regCHText)
        self.regD.set_text(regDText)
        self.regDL.set_text(regDLText)
        self.regDH.set_text(regDHText)

        self.regDI.set_text(regDIText)
        self.regSI.set_text(regSIText)
        self.regSP.set_text(regSPText)
        self.regBP.set_text(regBPText)
        self.regPC.set_text(regPCText)

        self.colourMemory()

    def makeHelpBox(self):
        """Called at construction, creates the help box including a TreeView to
        display assembly instructions and a text view to display the selected
        instructions documentation."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        box = self.builder.get_object("displayHelp")
        store = Gtk.ListStore(str)

        for x in self.functions:
            store.append([x])

        tree = Gtk.TreeView(store)
        tree.set_name("helpTree")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Command", renderer, text=0)

        tree.append_column(column)

        def onHelpTreeSelectionChanged(selection):
            """Called whenever the selected item in the TreeView."""
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                doc = self.machine.getFunctionDescriptions(model[treeiter][0])
                rawHelpText = str(doc).split("\n")

                instructionName = rawHelpText[0].split(":")[1]
                instructionTitle = rawHelpText[1].split(":")[1]
                instructionDescription = rawHelpText[3].split(":")[1]

                self.reg16Arg.set_name("reg16Off")
                self.reg8Arg.set_name("reg8Off")
                self.memArg.set_name("memOff")
                self.labelArg.set_name("labelOff")
                self.immedArg.set_name("immedOff")
                self.varArg.set_name("varOff")

                if "None" in rawHelpText[2]:
                    self.noArgsLabel.set_text("No Arguments")
                    self.noArgsLabel.set_visible(True)
                    self.argumentsFrame2.set_visible(False)
                    self.argumentsFrame.set_visible(False)
                else:
                    self.noArgsLabel.set_visible(False)
                    self.argumentsFrame2.set_visible(True)
                    self.argumentsFrame.set_visible(True)
                    instructionArgs = rawHelpText[2].split(",")

                    args1 = instructionArgs[0].split(":")[1:]

                    for arg in args1:
                        arg = arg.strip("[]")
                        if arg == "reg":
                            self.reg16Arg.set_name("reg16On")
                        elif arg == "reg16":
                            self.reg16Arg.set_name("reg16On")
                        elif arg == "reg8":
                            self.reg8Arg.set_name("reg8On")
                        elif arg == "mem":
                            self.memArg.set_name("memOn")
                        elif arg == "immed":
                            self.immedArg.set_name("immedOn")
                            self.varArg.set_name("varOn")
                        elif arg == "label":
                            self.labelArg.set_name("labelOn")

                    if len(instructionArgs) > 1:
                        self.argumentsFrame2.set_visible(True)

                        args2 = instructionArgs[1].split(":")
                        self.reg16Arg2.set_name("reg16Off")
                        self.reg8Arg2.set_name("reg8Off")
                        self.memArg2.set_name("memOff")
                        self.labelArg2.set_name("labelOff")
                        self.immedArg2.set_name("immedOff")
                        self.varArg2.set_name("varOff")

                        for arg in args2:
                            arg = arg.strip("[]")
                            if arg == "reg":
                                self.reg16Arg2.set_name("reg16On")
                            elif arg == "reg16":
                                self.reg16Arg2.set_name("reg16On")
                            elif arg == "reg8":
                                self.reg8Arg2.set_name("reg8On")
                            elif arg == "mem":
                                self.memArg2.set_name("memOn")
                            elif arg == "immed":
                                self.immedArg2.set_name("immedOn")
                                self.varArg2.set_name("varOn")
                            elif arg == "label":
                                self.labelArg2.set_name("labelOn")
                    else:
                        self.argumentsFrame2.set_visible(False)

                flags = rawHelpText[4].split(":")[1].split(",")

                flagsOut = (self.oFlagOut, self.dFlagOut, self.iFlagOut,
                            self.sFlagOut, self.zFlagOut, self.aFlagOut,
                            self.pFlagOut, self.cFlagOut)
                for index, flag in enumerate(flags):
                    flagsOut[index].set_text(flag)

                self.instructionName.set_text(instructionName)
                self.instructionTitle.set_text(instructionTitle)
                self.instructionDescription.get_buffer().set_text(
                                                        instructionDescription)

        tree.get_selection().connect("changed", onHelpTreeSelectionChanged)
        tree.get_selection().select_iter(tree.get_model().get_iter_first())

        scroll.add(tree)
        box.pack_start(scroll, True, True, 0)
        scroll.show_all()

    def nameGuiElementsForCSS(self):
        """ Names need set for CSS reasons only """
        self.machineInfoWrapper.set_name("machineInfoWrapper")
        self.outText.set_name("outText")
        self.code.set_name("code")
        self.lineNumberTV.set_name("lines")
        self.stack.set_name("stack")
        self.regA.set_name("regA")
        self.regAH.set_name("regAH")
        self.regAL.set_name("regAL")
        self.regB.set_name("regB")
        self.regBH.set_name("regBH")
        self.regBL.set_name("regBL")
        self.regC.set_name("regC")
        self.regCH.set_name("regCH")
        self.regCL.set_name("regCL")
        self.regD.set_name("regD")
        self.regDH.set_name("regDH")
        self.regDL.set_name("regDL")
        self.regBP.set_name("regBP")
        self.regSP.set_name("regSP")
        self.regSI.set_name("regSI")
        self.regDI.set_name("regDI")
        self.regPC.set_name("regPC")
        self.builder.get_object("registersLabel").set_name("registersLabel")
        self.builder.get_object("registersEndLabel").set_name("registersEnd")

        self.memory.set_name("memory")
        self.notebook.set_name("notebook")
        self.separatorLabel.set_name("separatorLabel" + str(self.shrunk))
        self.builder.get_object("codeScrolled").set_name("codeScrolled")
        self.builder.get_object("outScrolled").set_name("outScrolled")
        self.builder.get_object("memorySW").set_name("memorySW")
        self.builder.get_object("stackSW").set_name("stackSW")

        self.builder.get_object("flagsGrid").set_name("flagsGrid")
        self.oFlagOutMachine.set_name('o')
        self.dFlagOutMachine.set_name('d')
        self.iFlagOutMachine.set_name('i')
        self.sFlagOutMachine.set_name('s')
        self.zFlagOutMachine.set_name('z')
        self.aFlagOutMachine.set_name('a')
        self.pFlagOutMachine.set_name('p')
        self.cFlagOutMachine.set_name('c')
        self.builder.get_object('cFlagLabel1').set_name('cFlagLabel1')

        self.oFlagOut.set_name("oFlagOut")
        self.dFlagOut.set_name("dFlagOut")
        self.iFlagOut.set_name("iFlagOut")
        self.sFlagOut.set_name("sFlagOut")
        self.zFlagOut.set_name("zFlagOut")
        self.aFlagOut.set_name("aFlagOut")
        self.pFlagOut.set_name("pFlagOut")
        self.cFlagOut.set_name("cFlagOut")

        self.builder.get_object("instructionHelpBox").set_name(
                                                        "instructionHelpBox")

    def connectSignals(self):
        """ Connects handler signals to GUI elements """
        # GUI elements
        self.win.connect("delete-event", self.exit)
        self.hexSwitch.connect('notify::active', self.hexSwitchClicked)

        # Key events!
        self.win.connect('key_press_event', self.onKeyPressEvent)

        self.separatorLabelEB.connect('button_press_event',
                                      self.clickSeperator)
        self.separatorLabelEB.connect('enter-notify-event',
                                      self.hoverOverSeperator)
        self.separatorLabelEB.connect('leave-notify-event',
                                      self.hoverOffSeperator)

        self.builder.get_object("new").connect("activate",
                                      lambda *args: self.new())

        self.builder.get_object("open").connect("activate",
                                      lambda *args: self.openFileDialog())

        self.builder.get_object("save").connect("activate",
                                      lambda *args: self.saveFile())

        self.builder.get_object("saveas").connect("activate",
                                      lambda *args: self.saveFile(saveAs=True))

        self.builder.get_object("quit").connect("activate", self.exit)

        self.builder.get_object("step").connect("activate",
                                      lambda *args: self.stepButtonClicked())

        self.builder.get_object("all").connect("activate",
                                      lambda *args: self.runAll())

        self.builder.get_object("stopRunning").connect("activate",
                                      lambda *args: self.stopRunning(-1))

        self.builder.get_object("about").connect("activate",
                                      lambda *args: self.makeAboutDialogue())

        self.codeBuffer.connect("notify::cursor-position",
                                      lambda *args: self.updateStatusLabel())

        self.codeBuffer.connect("changed", self.textChanged)
        self.lineNumberTV.connect("button-press-event", self.setBreakpoint)

    def assignGuiElementsToVariables(self):
        """ Binds critical GUI elements from the builder object
            to variable names. """
        self.outText = self.builder.get_object("outText")
        self.code = self.builder.get_object("code")
        self.stack = self.builder.get_object("stack")
        self.machineInfoWrapper = self.builder.get_object("machineInfoWrapper")

        self.regA = self.builder.get_object("regA")
        self.regAH = self.builder.get_object("regAh")
        self.regAL = self.builder.get_object("regAl")
        self.regB = self.builder.get_object("regB")
        self.regBH = self.builder.get_object("regBh")
        self.regBL = self.builder.get_object("regBl")
        self.regC = self.builder.get_object("regC")
        self.regCH = self.builder.get_object("regCh")
        self.regCL = self.builder.get_object("regCl")
        self.regD = self.builder.get_object("regD")
        self.regDH = self.builder.get_object("regDh")
        self.regDL = self.builder.get_object("regDl")
        self.regBP = self.builder.get_object("regBP")
        self.regSP = self.builder.get_object("regSP")
        self.regSI = self.builder.get_object("regSI")
        self.regDI = self.builder.get_object("regDI")
        self.regPC = self.builder.get_object("regPC")

        # self.regFlags = self.builder.get_object("regFlags")
        self.memory = self.builder.get_object("memory")

        self.hexSwitch = self.builder.get_object("hexSwitch")

        self.notebook = self.builder.get_object("notebook")

        self.separatorLabelEB = self.builder.get_object("separatorLabelEB")
        self.separatorLabel = self.builder.get_object("separatorLabel")

        self.buttonBox = self.builder.get_object("buttonBox")

        self.statusLabel = self.builder.get_object("statusLabel")

        self.lineNumberTV = self.builder.get_object("lines")

        self.oFlagOut = self.builder.get_object("oFlagOut")
        self.dFlagOut = self.builder.get_object("dFlagOut")
        self.iFlagOut = self.builder.get_object("iFlagOut")
        self.sFlagOut = self.builder.get_object("sFlagOut")
        self.zFlagOut = self.builder.get_object("zFlagOut")
        self.aFlagOut = self.builder.get_object("aFlagOut")
        self.pFlagOut = self.builder.get_object("pFlagOut")
        self.cFlagOut = self.builder.get_object("cFlagOut")

        self.oFlagOutMachine = self.builder.get_object("oFlagOutMachine")
        self.dFlagOutMachine = self.builder.get_object("dFlagOutMachine")
        self.iFlagOutMachine = self.builder.get_object("iFlagOutMachine")
        self.sFlagOutMachine = self.builder.get_object("sFlagOutMachine")
        self.zFlagOutMachine = self.builder.get_object("zFlagOutMachine")
        self.aFlagOutMachine = self.builder.get_object("aFlagOutMachine")
        self.pFlagOutMachine = self.builder.get_object("pFlagOutMachine")
        self.cFlagOutMachine = self.builder.get_object("cFlagOutMachine")

        self.reg8Arg = self.builder.get_object("reg8")
        self.reg16Arg = self.builder.get_object("reg16")
        self.memArg = self.builder.get_object("mem")
        self.varArg = self.builder.get_object("variable")
        self.immedArg = self.builder.get_object("immed")
        self.labelArg = self.builder.get_object("label")

        self.reg8Arg = self.builder.get_object("reg8")
        self.reg16Arg = self.builder.get_object("reg16")
        self.memArg = self.builder.get_object("mem")
        self.varArg = self.builder.get_object("variable")
        self.immedArg = self.builder.get_object("immed")
        self.labelArg = self.builder.get_object("label")

        self.argumentsFrame = self.builder.get_object("argumentsFrame")
        self.argumentsFrame2 = self.builder.get_object("argumentsFrame2")

        self.reg8Arg2 = self.builder.get_object("reg82")
        self.reg16Arg2 = self.builder.get_object("reg162")
        self.memArg2 = self.builder.get_object("mem2")
        self.varArg2 = self.builder.get_object("variable2")
        self.immedArg2 = self.builder.get_object("immed2")
        self.labelArg2 = self.builder.get_object("label2")

        self.noArgsLabel = self.builder.get_object("noArgsLabel")

        self.instructionDescription = self.builder.get_object(
                                                    "instructionDescription")
        self.instructionName = self.builder.get_object("instructionName")
        self.instructionTitle = self.builder.get_object("instructionTitle")

    def setUpTextTags(self):
        """ Constructs the various text tags used
            to style text within textviews. """

        self.textTagBold = Gtk.TextTag()
        self.textTagBold.set_property("weight", Pango.Weight.BOLD)
        self.textTagGreenText = Gtk.TextTag()
        self.textTagGreenText.set_property("foreground", "green")
        self.textTagBlueText = Gtk.TextTag()
        self.textTagBlueText.set_property("foreground", "blue")
        self.textTagRedText = Gtk.TextTag()
        self.textTagRedText.set_property("foreground", "red")
        self.textTagGreyText = Gtk.TextTag()
        self.textTagGreyText.set_property("foreground", "grey")
        self.textTagLightGreyText = Gtk.TextTag()
        self.textTagLightGreyText.set_property("foreground", "lightgrey")

        self.codeBuffer.get_tag_table().add(self.textTagBold)
        self.codeBuffer.get_tag_table().add(self.textTagGreenText)
        self.codeBuffer.get_tag_table().add(self.textTagBlueText)
        self.codeBuffer.get_tag_table().add(self.textTagRedText)
        self.codeBuffer.get_tag_table().add(self.textTagGreyText)
        self.codeBuffer.get_tag_table().add(self.textTagLightGreyText)

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
        self.textTagBlack = Gtk.TextTag()
        self.textTagBlack.set_property("background", "black")
        self.textTagBlack.set_property("foreground", "white")

        self.memoryBuffer.get_tag_table().add(self.textTagGrey)
        self.memoryBuffer.get_tag_table().add(self.textTagRed)
        self.memoryBuffer.get_tag_table().add(self.textTagOrange)
        self.memoryBuffer.get_tag_table().add(self.textTagMagenta)
        self.memoryBuffer.get_tag_table().add(self.textTagGreen)
        self.memoryBuffer.get_tag_table().add(self.textTagBlue)
        self.memoryBuffer.get_tag_table().add(self.textTagPurple)
        self.memoryBuffer.get_tag_table().add(self.textTagBlack)
        self.memoryColours = [self.textTagRed, self.textTagOrange,
                              self.textTagMagenta, self.textTagGreen,
                              self.textTagBlue, self.textTagPurple,
                              self.textTagGrey]
        self.stackColour = self.textTagBlack

        self.textTagBreakpoint = Gtk.TextTag()
        self.textTagBreakpoint.set_property("background", "red")
        self.linesBuffer.get_tag_table().add(self.textTagBreakpoint)

    def updateStatusLabel(self, *args):
        """ Updates the status label at the bottom of the screen,
            including current line number, status of the simulation, etc. """

        lineNum = self.codeBuffer.get_iter_at_offset(
                            self.codeBuffer.props.cursor_position).get_line()

        self.statusLabel.set_text(" Line: " + str(lineNum) +
                                  "\t" + self.machine.isRunning() * "Running")

    def updateStack(self):
        """ Updates the stack gui element """

        if self.machine.isRunningAll():
            return
        if self.displayInHex:
            stackText = ["0" * (4 - len(hex(int(x)).split("x")[1])) +
                    hex(int(x)).split("x")[1] for x in self.machine.getStack()]
        else:
            stackText = ["0" * (4 - len(str(x))) +
                    str(x) for x in self.machine.getStack()]

        stackText.reverse()

        self.stackBuffer.set_text("\n" * (self._MAXSTACKLINES - len(stackText))
                                   + "\n".join(stackText))

    def setupTextBuffers(self):
        """ Binds various textBuffers to local variables """
        self.outBuffer = self.outText.get_buffer()
        self.codeBuffer = self.code.get_buffer()
        self.stackBuffer = self.stack.get_buffer()
        self.memoryBuffer = self.memory.get_buffer()
        self.linesBuffer = self.lineNumberTV.get_buffer()
        # Set up the text behaviour
        self.outText.set_wrap_mode(Gtk.WrapMode.WORD)
        self.memory.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.stack.set_justification(Gtk.Justification.CENTER)
        # self.code.set_wrap_mode(Gtk.WrapMode.WORD)

    def hoverOverFileButton(self, widget, event):
        fn = self.fileIconTable[hash(widget.get_child())]

        newPath = [self._PATHDELIM + "images", fn + "Over.png"]
        newFileName = self._PATH + self._PATHDELIM.join(newPath)

        widget.get_child().set_from_file(newFileName)

    def hoverOffFileButton(self, widget, event):
        fn = self.fileIconTable[hash(widget.get_child())]

        newPath = [self._PATHDELIM + "images", fn + ".png"]
        newFileName = self._PATH + self._PATHDELIM.join(newPath)

        widget.get_child().set_from_file(newFileName)

    def makeFileButtons(self):
        """ Creates the file buttons on the bottom of the screen: includes
        New, Open, Save, Run All, Step Once, Stop Stimulation """

        new = Gtk.Image()
        newPath = [self._PATHDELIM + "images", "newFileIcon.png"]
        new.set_from_file(self._PATH + self._PATHDELIM.join(newPath))

        self.fileIconTable[hash(new)] = "newFileIcon"

        newEB = Gtk.EventBox()
        newEB.add(new)
        newEB.set_tooltip_text("New - Ctrl + N")

        self.buttonBox.pack_start(newEB, False, False, 1)

        openImage = Gtk.Image()
        openPath = [self._PATHDELIM + "images", "openIcon.png"]
        openImage.set_from_file(self._PATH + self._PATHDELIM.join(openPath))

        self.fileIconTable[hash(openImage)] = "openIcon"

        openEB = Gtk.EventBox()
        openEB.add(openImage)
        openEB.set_tooltip_text("Open - Ctrl + O")

        self.buttonBox.pack_start(openEB, False, False, 1)

        save = Gtk.Image()
        savePath = [self._PATHDELIM + "images", "saveIcon.png"]
        save.set_from_file(self._PATH + self._PATHDELIM.join(savePath))

        self.fileIconTable[hash(save)] = "saveIcon"

        saveEB = Gtk.EventBox()
        saveEB.add(save)
        saveEB.set_tooltip_text("Save - Ctrl + S")

        self.buttonBox.pack_start(saveEB, False, False, 1)

        allIcon = Gtk.Image()
        allPath = [self._PATHDELIM + "images", "allIcon.png"]
        allIcon.set_from_file(self._PATH + self._PATHDELIM.join(allPath))

        self.fileIconTable[hash(allIcon)] = "allIcon"

        allEB = Gtk.EventBox()
        allEB.add(allIcon)
        allEB.set_tooltip_text("Run All - Ctrl + Enter")

        self.buttonBox.pack_start(allEB, False, False, 1)

        step = Gtk.Image()
        stepPath = [self._PATHDELIM + "images", "stepIcon.png"]
        step.set_from_file(self._PATH + self._PATHDELIM.join(stepPath))

        self.fileIconTable[hash(step)] = "stepIcon"

        stepEB = Gtk.EventBox()
        stepEB.add(step)
        stepEB.set_tooltip_text("Run One Line - Enter")

        self.buttonBox.pack_start(stepEB, False, False, 1)

        stop = Gtk.Image()
        stopPath = [self._PATHDELIM + "images", "stopIcon.png"]
        stop.set_from_file(self._PATH + self._PATHDELIM.join(stopPath))

        self.fileIconTable[hash(stop)] = "stopIcon"

        stopEB = Gtk.EventBox()
        stopEB.add(stop)
        stopEB.set_tooltip_text("Stop Running - Ctrl + X")
        self.buttonBox.pack_start(stopEB, False, False, 1)

        for x in [newEB, openEB, saveEB, allEB, stepEB, stopEB]:
            x.connect('button_release_event', self.hoverOffFileButton)
            x.connect('enter-notify-event', self.hoverOverFileButton)
            x.connect('leave-notify-event', self.hoverOffFileButton)

        newEB.connect('button_press_event', self.pressNewButton)
        openEB.connect('button_press_event', self.pressOpenButton)
        saveEB.connect('button_press_event', self.pressSaveButton)
        stepEB.connect('button_press_event', self.pressStepButton)
        allEB.connect('button_press_event', self.pressAllButton)
        stopEB.connect('button_press_event', self.pressStopButton)

    def clearIcon(self, widget):
        emptyPath = [self._PATHDELIM + "images", "empty.png"]
        widget.get_child().set_from_file(
                                self._PATH + self._PATHDELIM.join(emptyPath))

    def pressNewButton(self, widget, event):
        self.clearIcon(widget)
        self.new()

    def pressOpenButton(self, widget, event):
        self.clearIcon(widget)
        self.openFileDialog()

    def pressStepButton(self, widget, event):
        self.clearIcon(widget)
        self.stepButtonClicked()

    def pressAllButton(self, widget, event):
        self.clearIcon(widget)
        self.runAll()

    def pressSaveButton(self, widget, event):
        self.clearIcon(widget)
        self.saveFile()

    def pressStopButton(self, widget, event):
        self.clearIcon(widget)

        if self.machine.isRunning():
            self.stopRunning(1)
        self.updateStatusLabel()

    def saveFile(self, saveAs=False):
        """ Saves the fileToSave.  If the fileToSave hans't been previously
        saved or if saveAs == True then a dialog propmts the user for a
        location else it'll save in the same place it has been historically
        saved. """

        if self.fileName is None or saveAs:
            fileChooser = Gtk.FileChooserDialog("Save your fileToSave",
                                                self.win,
                                                Gtk.FileChooserAction.SAVE,
                                                (Gtk.STOCK_CANCEL,
                                                 Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_SAVE,
                                                 Gtk.ResponseType.ACCEPT))
            response = fileChooser.run()

            fileName = None
            if response == Gtk.ResponseType.ACCEPT:
                fileName = fileChooser.get_filename()

            fileChooser.destroy()
            self.fileName = fileName
            if fileName is not None:
                self.saveFile()
        else:
            try:
                codeStart = self.codeBuffer.get_start_iter()
                codeEnd = self.codeBuffer.get_end_iter()

                codeText = self.codeBuffer.get_text(codeStart, codeEnd, False)
                fileToSave = open(self.fileName, "w")
                fileToSave.write(codeText)
                fileToSave.close()

                self.codeBuffer.set_modified(False)
                self.updateWindowTitle()
            except IOError:
                """ Fatal error popup """
                print "Fatal Error"

    def new(self):
        """ Resets the simulation and code """
        self.clearGui()

        self.backSlashCount = 0
        self.updateWindowTitle()
        self.fileName = None

        self.outBuffer.set_text("")
        self.codeBuffer.set_modified(False)
        self.codeBuffer.remove_all_tags(self.codeBuffer.get_start_iter(),
                                        self.codeBuffer.get_end_iter())
        self.codeBuffer.set_text("")

        self.machine.restart()

        self.functions = self.machine.getFunctions()
        self.functions.sort()
        # self.sysCodes = as88.getSysCodes()

    def runAll(self):
        """ If the simulation isn't running, then it is started and run in full
            with the GUI only being updated afterwards.

            If the simulation is running, then it runs until completion from
            it's current state, with GUI only being updated after.

            If the simulation has already run, then it prompts the user if he
            wishes to restart, and does so. """

        if not self.machine.hasRun():  # If we aren't waiting on a restart
            if not self.machine.isRunning():  # if We're not running, start
                self.startRunning()
            else:
                # If we are running, we got an arrow to get rid of
                startOfArrow = self.codeBuffer.get_iter_at_line_offset(
                                               self.machine.getLastLine(), 0)

                if not startOfArrow.ends_line():
                    endOfArrow = self.codeBuffer.get_iter_at_line_offset(
                                                self.machine.getLastLine(), 1)

                    arrowText = self.codeBuffer.get_text(startOfArrow,
                                                         endOfArrow, False)
                    if arrowText == ">":
                        self.codeBuffer.delete(startOfArrow, endOfArrow)

            self.outPutFromMachine(self.machine.runAll())

            self.updateRegisters()
            self.updateStack()
        else:
            if self.restartPrompt():
                self.runAll()

    def restartPrompt(self):
        """ Presents a dialog asking the user if they wish to restart the
            simulation """
        dialog = Gtk.MessageDialog(self.win, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO,
                                   "Do You Wish to Restart?",
                                   title="Restart the simulation?")

        response = dialog.run()

        if response == Gtk.ResponseType.NO:
            dialog.destroy()
            return False
        elif response == Gtk.ResponseType.YES:
            dialog.destroy()
            self.startRunning()
            return True
        else:
            dialog.destroy()
            return False

    def startRunning(self):
        """Loads in the code to run, intialises all local variables and labels
        as set up in the code. First pass for forward references, and setting
        up local vars, etc. The self.running flag is set so the user can step
        thru accordingly. """

        self.clearGui()

        self.updateRegisters()
        self.updateStack()
        self.code.set_editable(False)

        self.notebook.set_visible(True)
        self.separatorLabel.set_angle(90)
        self.separatorLabel.set_text("^ hide ^")
        self.shrunk = False

        self.lines = self.codeBuffer.get_text(self.codeBuffer.get_start_iter(),
                                              self.codeBuffer.get_end_iter(),
                                              False).split("\n")

        errorMessage = self.machine.loadCode(self.lines)

        self.outPut(errorMessage)

        if errorMessage != "":
            return -1

    def stepButtonClicked(self):
        """ Defines what happens if the step button is clicked.
        This is fired if the user interacts with the GUI to step in anyway
        (i.e. key combos, menu items, buttons, etc.)
        This calls the step() function to execute a line of code
        and performs all graphical duties before and after executing the code.
        If the code has already been run to completion this prompts the user
        asking if they wish to restart.
        """
        if self.machine.isRunning():
            # Scroll to view the line
            currentLine = self.code.get_buffer().get_iter_at_line(
                                                self.machine.getRegister('PC'))

            self.code.scroll_to_iter(currentLine, 0.25, True, .5, .5)
            self.codeBuffer.place_cursor(currentLine)

            # insert a >
            self.codeBuffer.insert(currentLine, ">")

            # remove the > from the previous line, -1 means first line
            if self.machine.lastLine != -1:
                startOfArrow = self.codeBuffer.get_iter_at_line_offset(
                                                self.machine.getLastLine(), 0)
                if not startOfArrow.ends_line():
                    endOfArrow = self.codeBuffer.get_iter_at_line_offset(
                                                self.machine.getLastLine(), 1)

                    self.codeBuffer.delete(startOfArrow, endOfArrow)

            self.outPutFromMachine(self.machine.step())
            self.updateRegisters()
            self.updateStack()

        elif self.machine.hasRun():
            """ Prompt the user to restart """
            if self.restartPrompt():
                self.stepButtonClicked()

        else:
            if self.startRunning() == -1:
                self.stopRunning()
                return
            else:
                self.stepButtonClicked()

    def resetTimer(self):
        self.timer = time.time()

    def timeToUndo(self):
        return (time.time() - self.timer > self._SAVE_STATE_TIME)

    def onKeyPressEvent(self, widget, event):
        """ Handles Key Down events checks for key combinations.
            Enter -> Step
            Ctrl+Enter -> Run All
            Shift+Enter -> Run All
            Ctrl+N -> New File
            Ctrl+S -> Save
            Ctrl+O -> Open File
            Ctrl+Q -> Quit File
            Ctrl+Shift+N -> Save As
            Ctrl+X -> Stop Running
        """

        if self.timeToUndo():
            codeStart = self.codeBuffer.get_start_iter()
            codeEnd = self.codeBuffer.get_end_iter()
            tempState = self.codeBuffer.get_text(codeStart, codeEnd, False)
            self.codeStates.saveState(tempState)
            self.resetTimer()

        keyval = event.keyval

        keyname = Gdk.keyval_name(keyval)

        keysDown = Gtk.accelerator_get_label(keyval, event.state).split("+")

        if "Mod2" in keysDown:
            keysDown.remove("Mod2")  # This is when numLock is on

        if len(keysDown) == 1:
            if keyname == 'Return' or keyname == 'KP_Enter':
                if not  self.code.has_focus():
                    self.stepButtonClicked()
                return

        elif len(keysDown) == 2:
            if "Ctrl" in keysDown:
                if "O" in keysDown:
                    self.openFileDialog()
                elif "N" in keysDown:
                    self.new()
                elif "S" in keysDown:
                    self.saveFile()
                elif "Q" in keysDown:
                    self.exit()
                elif "Return" in keysDown or "Enter (keypad)" in keysDown:
                    self.runAll()
                elif "X" in keysDown:
                    self.stopRunning(-1)
                elif "Z" in keysDown:
                    self.undo()
                elif "Y" in keysDown:
                    self.redo()
                elif "V" in keysDown:
                    self.updateAll = True
            elif "Shift" in keysDown:
                if "Return" in keysDown or "Enter (keypad)" in keysDown:
                    self.runAll()

        elif len(keysDown) == 3:
            if "Ctrl" in keysDown:
                if "Shift" in keysDown:
                    if "S" in keysDown:
                        self.saveFile(saveAs=True)
                    elif "Z" in keysDown:
                        self.redo()

    def undo(self):
        """ Undoes actions only in the text field """
        if self.codeStates.canUndo():
            codeStart = self.codeBuffer.get_start_iter()
            codeEnd = self.codeBuffer.get_end_iter()
            tempState = self.codeBuffer.get_text(codeStart, codeEnd, False)
            self.updateAll = 2
            self.codeBuffer.set_text(self.codeStates.undo(tempState))

    def redo(self):
        """ Redoes actions only in the text field """
        if self.codeStates.canRedo():
            self.codeBuffer.set_text(self.codeStates.redo())

    def outPutFromMachine(self, string):
        """ Outputs the result of a machine query.
        Different then regular output since we have to do a few simple checks
        before we print."""

        if string == self.machine._OVER:
            self.stopRunning()
        else:
            if string is not None:
                self.outPut(string)

            if self.machine.requestsGetChar():
                self.machine.respondGetChar(self.getChar())
                if self.machine.isRunningAll():
                    self.runAll()

            if not self.machine.isRunning():
                # The machine shut down without signalling
                # an error must've occurred
                self.stopRunning(-1)

    def outPut(self, string):
        """ Outputs the message "string" to the designated textview
            in the GUI """
        outEnd = self.outBuffer.get_end_iter()
        self.outText.get_buffer().insert(outEnd, string)
        self.outText.scroll_to_iter(outEnd, 0.1, True, .5, .5)

    def clearGui(self):
        """ Empties the text components of all relevant GUI elements"""
        self.outText.get_buffer().set_text("")
        self.regA.set_text("")
        self.regB.set_text("")
        self.regC.set_text("")
        self.regD.set_text("")
        self.regBP.set_text("")
        self.regSP.set_text("")
        self.regDI.set_text("")
        self.regSI.set_text("")
        self.regPC.set_text("")
        self.memory.get_buffer().set_text("")
        self.aFlagOutMachine.set_text("")
        self.cFlagOutMachine.set_text("")
        self.oFlagOutMachine.set_text("")
        self.dFlagOutMachine.set_text("")
        self.iFlagOutMachine.set_text("")
        self.pFlagOutMachine.set_text("")
        self.sFlagOutMachine.set_text("")
        self.zFlagOutMachine.set_text("")

    def updateWindowTitle(self):
        modStar = "*" * self.codeBuffer.get_modified()
        if self.fileName is None:
            fileName = "Untitled"
        else:
            fileName = self.fileName.split(self._PATHDELIM)[-1]

        self.win.set_title(self._PROGRAMNAME + " - " + modStar + fileName)

    def textChanged(self, widget):
        """ This function gets called everytime the 'code' text changes.
        Syntax Highglighting is applied on the changed line appropriately. """
        if not self.machine.isRunning():
            self.updateWindowTitle()
            if self.updateAll:
                """ So this is to updateAll the text, specifically when a
                paste or undo action occurs. but for whatever reason, in an
                undo action the text is cleared, and then put in. So this
                fires this function twice. Thus, for undo's updateAll
                is set to 2. Hence it evals as true, and we can rip off
                two function calls in quick succession. """
                lineNumbers = range(self.codeBuffer.get_line_count() + 1)
                self.updateAll -= 1
            else:
                lineNumbers = [self.codeBuffer.get_iter_at_offset(
                            self.codeBuffer.props.cursor_position).get_line()]
            for lineNumber in lineNumbers:
                startOfLineIter = self.codeBuffer.get_iter_at_line_offset(
                                                        lineNumber, 0)

                if lineNumber + 1 >= self.codeBuffer.get_line_count():
                    endOfLineIter = self.codeBuffer.get_end_iter()
                else:
                    endOfLineIter = self.codeBuffer.get_iter_at_line_offset(
                                                        lineNumber + 1, 0)

                lineText = self.codeBuffer.get_text(startOfLineIter,
                                                    endOfLineIter, False)

                self.syntaxHighlight(readliner.ReadLiner(lineText),
                                     lineOffset=lineNumber)

    def makeAboutDialogue(self):
        """ Makes an About Dialog displaying basic info about the program
        (Name, Copyright, version, logo, website, license) """
        about = Gtk.AboutDialog()
        about.set_name("AboutDialog")
        about.set_program_name(self._PROGRAMNAME)
        about.set_version(self._VERSION)
        about.set_copyright("(c) Brydon Eastman")
        about.set_comments(self._DESCRIPTION)
        # TODO: Credit "\nIcons Courtesy of
        # http://gentleface.com/free_icon_set.html" for the icons
        about.set_website(self._WEBSITE)
        about.set_license_type(self._LICENSE)
        logoPath = self._PATH + self._PATHDELIM.join([self._PATHDELIM +
                                                      "images", "logo.png"])

        about.set_logo(GdkPixbuf.Pixbuf.new_from_file(logoPath))
        about.run()
        about.destroy()

    def stackToolTip(self, widget, x, y, keyboard_tip, tooltip, data):
        if keyboard_tip:
            offset = widget.props.buffer.cursor_position
            ret = widget.props.buffer.get_iter_at_offset(offset)
        else:  # else get the bounds by the cursor
            coords = widget.window_to_buffer_coords(Gtk.TextWindowType.TEXT,
                                            x, y)
            ret = widget.get_iter_at_position(coords[0], coords[1])

        if ret[0].has_tag(data):
            tooltip.set_text("Stack")
        else:
            return False

        return True

    def memoryToolTipOption(self, widget, x, y, keyboard_tip, tooltip, data):
        """ For printing the tooltips in the memory textview """

        # if the tooltip is focus from the keyboard, get those bounds
        if keyboard_tip:
            offset = widget.props.buffer.cursor_position
            ret = widget.props.buffer.get_iter_at_offset(offset)
        else:  # else get the bounds by the cursor
            coords = widget.window_to_buffer_coords(Gtk.TextWindowType.TEXT,
                                                    x, y)
            ret = widget.get_iter_at_position(coords[0], coords[1])

        if ret[0].has_tag(data):
            offset = ret[0].get_offset()
            for element in self.machine.effectiveBSSandDATALocation:
                memStart = self.machine.effectiveBSSandDATALocation[element][0]
                memEnd = self.machine.effectiveBSSandDATALocation[element][1]
                if memStart <= offset <= memEnd:
                    start = self.machine.getFromBSSorDATA(element, 0)
                    end = self.machine.getFromBSSorDATA(element, 1)

                    if self.displayInHex:
                        start = self.machine.intToHex(start)
                        end = self.machine.intToHex(end)

                    tooltip.set_text("%s (from %s to %s)" % (element,
                                                        str(start), str(end)))
                    break
        else:
            return False

        return True

    def hexSwitchClicked(self, button=None, data=None):
        """ Gets called when the hex switch is toggled,
        this switch changes it so the registers, stack, and memory all display
        in either hex or ascii """
        self.displayInHex = not self.displayInHex
        self.updateRegisters()
        self.updateStack()

    def stopRunning(self, i=1):
        """ Ends the current simulation, if i=1 then succesfully, otherwise
        there was an issue """

        if self.machine.isRunning():
            # Stop the machine if it isn't already stopped.
            # Normally the machine stops first, but sometimes the gui
            # get's the signal first.
            # For instance, if the stop button is clicked
            self.machine.stopRunning()

        self.code.set_editable(True)

        curLine = self.machine.getRegister('PC')
        lastLine = self.machine.getLastLine()

        startOfArrow = self.codeBuffer.get_iter_at_line_offset(curLine, 0)
        if not startOfArrow.ends_line():
            endOfArrow = self.codeBuffer.get_iter_at_line_offset(curLine, 1)

            if self.codeBuffer.get_text(startOfArrow,
                                        endOfArrow, False) == ">":

                self.codeBuffer.delete(startOfArrow, endOfArrow)
            else:
                startOfArrow = self.codeBuffer.get_iter_at_line_offset(
                                                                   lastLine, 0)
                if not startOfArrow.ends_line():
                    endOfArrow = self.codeBuffer.get_iter_at_line_offset(
                                                                lastLine, 1)
                    if self.codeBuffer.get_text(startOfArrow, endOfArrow,
                                                False) == ">":
                        self.codeBuffer.delete(startOfArrow, endOfArrow)
        else:
            startOfArrow = self.codeBuffer.get_iter_at_line_offset(lastLine, 0)
            if not startOfArrow.ends_line():
                endOfArrow = self.codeBuffer.get_iter_at_line_offset(lastLine,
                                                                    1)
                if self.codeBuffer.get_text(startOfArrow, endOfArrow,
                                            False) == ">":

                    self.codeBuffer.delete(startOfArrow, endOfArrow)

        if i == 1:
            self.outPut("\n----\nCode executed succesfully.\n")
        else:
            self.outPut("\n----\nCode execution terminated.\n")

    def getChar(self):
        """ Get's input by creating an entrydialog.
            Interfaces with GetChar system trap """

        entry = entrydialog.EntryDialog(title="Waiting for input",
                                        label="Waiting for input",
                                        buttons=(Gtk.STOCK_CANCEL,
                                                 Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_OK,
                                                 Gtk.ResponseType.OK),
                                        modal=True, parent=self.win)
        result = entry.run()

        if result is None:
            result = ""

        entry.destroy()

        return result + "\n"

    def colourMemory(self):
        """ Colour codes the items in the memory for easy identification """
        backSlashOffsetBeforeTag = 0
        backSlashOffsetAfterTag = 0
        self.backSlashCount = 0
        sortedBSSandDATAList = []

        for index, name in enumerate(self.machine.getDATAKeys() +
                                     self.machine.getBSSKeys()):

            if name in self.machine.getDATAKeys():
                location = self.machine.getFromDATA(name)
            else:
                location = self.machine.getFromBSS(name)

            if len(sortedBSSandDATAList) == 0:
                sortedBSSandDATAList.append([location[0], location[1], name])
            else:
                for index, element in enumerate(sortedBSSandDATAList):
                    if location[0] < element[1]:
                        sortedBSSandDATAList.insert(index, [location[0],
                                                            location[1], name])
                        break
                else:
                    sortedBSSandDATAList.append([location[0], location[1],
                                                 name])

        for index, location in enumerate(sortedBSSandDATAList):
            backSlashOffsetBeforeTag = backSlashOffsetAfterTag
            for x in self.machine.getFromMemoryAddress(location[0],
                                                       location[1]):
                if x in self.ESCAPE_CHARS:
                    backSlashOffsetAfterTag += 1
                    self.backSlashCount += 1
            before = location[0] * (self.displayInHex + 1) + \
                     backSlashOffsetBeforeTag * (not self.displayInHex)
            after = (location[1] + 1) * (self.displayInHex + 1) + \
                    backSlashOffsetAfterTag * (not self.displayInHex)

            self.machine.effectiveBSSandDATALocation[location[2]] = [before,
                                                                     after]

            self.memoryBuffer.apply_tag(
                        self.memoryColours[index % len(self.memoryColours)],
                        self.memoryBuffer.get_iter_at_offset(before),
                        self.memoryBuffer.get_iter_at_offset(after))
        self.memoryBuffer.apply_tag(
          self.stackColour,
          self.memoryBuffer.get_iter_at_offset(self.machine.getRegister("SP") * (self.displayInHex + 1)),
          self.memoryBuffer.get_end_iter()
          )

    def exit(self, *args):
        """ Determines whether or not to exit, if there is an unsaved file or
        active simulation it prompts the user. Then decides whether to exit
        the program or not based on the users response. """

        if self.machine.isRunning():
            dialog = Gtk.MessageDialog(self.win, 0, Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.YES_NO,
                                       "Do you want to quit?",
                                       title="Are you sure?")

            warning = "There is a simulation currently in progress."
            dialog.format_secondary_text(warning)

            response = dialog.run()

            if response == Gtk.ResponseType.NO:
                dialog.destroy()
                return True  # Returning true tells GTK to not kill this win

            dialog.destroy()
        if self.codeBuffer.get_modified():
            dialog = Gtk.MessageDialog(self.win, 0, Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.YES_NO,
                                       "Do you want to quit?",
                                       title="Are you sure?")

            dialog.format_secondary_text("There are unsaved changes.")

            response = dialog.run()

            if response == Gtk.ResponseType.NO:
                dialog.destroy()
                return True  # Returning true tells GTK to not kill this win

            dialog.destroy()

        Gtk.main_quit(args)

    def makeCharPrintable(self, string):
        """ Char's "below" " " in the ascii table or above "~" do not have nice
            printable forms. So we replace them with zeros. """

        _ESCAPESEQUENCES = ["\n", "'", '"', "\a", "\b", "\f", "\r", "\t", "\v"]

        if string in _ESCAPESEQUENCES:
            return string
        if ord(string) == 0:
            return "0"
        if ord(string) < ord(" ") or ord(string) > ord("~"):
            return "?"
        return string


def main():
    """ The entry point. """
    GObject.threads_init()

    A = Simulator()

    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            A.openFile(sys.argv[1])

    Gtk.main()

if __name__ == "__main__":
    main()
