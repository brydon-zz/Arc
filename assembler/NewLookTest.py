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

from gi.repository import Gtk, Gdk, GObject, Pango, GdkPixbuf

import CommandInterpreter, Intel8088, ReadLiner, sys, os, tokenize, time

""""Simulator Class for Intel 8088 Architecture"""
class Simulator(object):
    _PROGRAMNAME = "The Best 8088 Simulator"
    _VERSION = "0.5"
    _DESCRIPTION = "A Program for Writing and Simulating Intel 8088 Assembly Code"
    _WEBSITE = "http://www.beastman.ca/"
    _LICENSE = Gtk.License.GPL_2_0

    def __init__(self):
        self._PATH = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-1])
        self._KEYTIMEOUT = 4  # TODO: maybe replace this with focus lost?

        """ Begin GUI """
        styles = """
#As88Window #helpTree {
    color:#000;
    background-color:#F5F5F5;
}

#As88Window #registersLabel {
    border-bottom:3px solid #000;
}

#As88Window #registersEndLabel {
    border-top:3px solid #000;
}

#As88Window #machineInfoWrapper {
    background-color:#F5F5F5;
}


#As88Window #flagsGrid GtkLabel {
    border-left:1px solid #000;
    border-top:1px solid #000;
    background-color:#E5E5E5;
}

#As88Window #c {
    border-bottom: 1px solid #000;
    border-right: 1px solid #000;
}

#As88Window #cFlagLabel1 {
    border-right: 1px solid #000;
}

#As88Window #a, #As88Window #z, #As88Window #p, #As88Window #s, #As88Window #i, #As88Window #d, #As88Window #o {
    border-bottom: 1px solid #000;
}

#As88Window #machineInfoWrapper GtkLabel {
    color:#000;
}

#As88Window #machineInfoWrapper GtkTextView {
    color:#000;
    border:1px solid #000;
}

#As88Window #instructionHelpBox, #As88Window #instructionHelpBox *, #As88Window #instructionHelpBox * * {
    color:#000;
    background-color:#E5E5E5;
}

GtkAboutDialog, GtkAboutDialog * {
    color: #000;
}

#As88Window #lines {
    color:#999;
    border-right:1px solid #333;
    border-left:1px solid #333;
    font-family:mono;
}

#As88Window #codeScrolled {
    border-bottom: 3px solid #000;
    border-top:0;
    border-left:0;
    border-right:0;
}

#As88Window #seperatorLabelTrue {
    background-color:#522;
    border-right:1px solid #000;
    border-left:1px solid #000;
    border-top:0;
    border-bottom:0;
}

#As88Window #seperatorLabelFalse {
    background-color:#225;
    border-right:1px solid #000;
    border-left:1px solid #000;
    border-top:0;
    border-bottom:0;
}

#As88Window #seperatorLabelOverTrue {
    background-color:#666;
    border-right:1px solid #000;
    border-left:1px solid #000;
    border-top:0;
    border-bottom:0;
}

#As88Window #seperatorLabelOverFalse {
    background-color:#666;
    border-right:1px solid #000;
    border-left:1px solid #000;
    border-top:0;
    border-bottom:0;
}

#As88Window {
    background-color:#000;
}

#As88Window #notebook {
    color:#fff;
    margin-top:0;
    padding-top:0;
    margin-right:0;
    padding-right:0;
    margin-left:0;
    padding-left:0;
    background-color:#000;
    border: 1px solid #333;
}

#As88Window #stack, #As88Window #memory {
    background-color:#E5E5E5;
    font-family:mono;
    color:#000;
    border:0;
}

#As88Window #regA, #As88Window #regB, #As88Window #regC, #As88Window #regD, #As88Window #regSP, #As88Window #regBP, #As88Window #regSI,#As88Window #regDI, #As88Window #regPC {
    background-color:#E5E5E5;
    border:1px solid #000;
    font-family:mono;
    color:#000;
}

#As88Window #regAH, #As88Window #regAL, #As88Window #regBH, #As88Window #regBL, #As88Window #regCH, #As88Window #regCL, #As88Window #regDH, #As88Window #regDL {
    background-color:#E5E5E5;
    border-left:1px solid #000;
    border-right:1px solid #000;
    border-bottom:1px solid #000;
    font-family:mono;
    color:#000;
}

#As88Window #outText {
    background-color:#333;
    font-family:mono;
    color:#FFF;
    border:0;
}

#As88Window #code {
    font-family: mono;
}

#As88Window #stackSW {
    border-right:1px solid black;
}

#As88Window #memorySW {
    border:1px solid black;
}

#As88Window #outScrolled {
    border:0;
}

#As88Window #reg16Off, #As88Window #reg8Off, #As88Window #memOff, #As88Window #labelOff, #As88Window #immedOff, #As88Window #varOff {
    border:1px solid #000;
    color:#666;
    background-color:#E5E5E5;
}

#As88Window #reg16On, #As88Window #reg8On, #As88Window #memOn, #As88Window #labelOn, #As88Window #immedOn, #As88Window #varOn {
    border:1px solid #F00;
    color:#000;
    background-color:#F5F5F5;
}

"""

        """Handlers for the actions in the interface."""

        self.fileName = None
        self.breakpointDClickTime = 0
        # Make stuff from the GLADE file and setup events
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self._PATH + "/xml/GladeMockup3-3.glade")

        self.win = self.builder.get_object("window")
        self.win.set_name('As88Window')
        self.win.connect("delete-event", self.exit)

        # Set Up the CSS
                # Creating local vars for gui elements
        self.assignGuiElementsToVariables()

        # Text buffers for the big text-views
        self.setupTextBuffers()
        self.makeFileButtons()

        self.nameGuiElementsForCSS()
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_data(styles)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Hex Switch needs a special trigger signal that glade cannot understand
        self.hexSwitch.connect('notify::active', self.hexSwitchClicked)

        # Key events!
        self.win.connect('key_press_event', self.onKeyPressEvent)
        self.win.connect('key_release_event', self.onKeyReleaseEvent)

        self.seperatorLabelEB.connect('button_press_event', self.clickSeperator)
        self.seperatorLabelEB.connect('enter-notify-event', self.hoverOverSeperator)
        self.seperatorLabelEB.connect('leave-notify-event', self.hoverOffSeperator)

        self.builder.get_object("new").connect("activate", lambda *args: self.new())
        self.builder.get_object("open").connect("activate", lambda *args: self.openFile())
        self.builder.get_object("save").connect("activate", lambda *args: self.saveFile())
        self.builder.get_object("saveas").connect("activate", lambda *args: self.saveFile(saveAs=True))
        self.builder.get_object("quit").connect("activate", self.exit)

        self.builder.get_object("step").connect("activate", lambda *args: self.stepButtonClicked())
        self.builder.get_object("all").connect("activate", lambda *args: self.runAll())
        self.builder.get_object("stopRunning").connect("activate", lambda *args: self.stopRunning(-1))

        self.builder.get_object("about").connect("activate", lambda *args: self.makeAboutDialogue())

        # Window Icon -> what shows up in unity bar/toolbar/etc.
        self.win.set_icon_from_file(self._PATH + "/images/icon.png")

        self.setUpTextTags()

        self.memory.props.has_tooltip = True

        # self.notebook.set_visible(False)
        for x in self.memoryColours:
            self.memory.connect("query-tooltip", self.memoryToolTipOption, x)

        self.updateLineCounter()

        """ End GUI """

        self.downFile = ""

        self.new()

        # GUI elements
        self.codeBuffer.connect("notify::cursor-position", self.updateStatusLabel)
        self.codeBuffer.connect("changed", self.textChanged)
        self.lineNumberTV.connect("button-press-event", self.setBreakpoint)
        self.updateStatusLabel()

        # return string.replace("\n", "\\n").replace("\'", "\\'").replace('\"', '\\"').replace("\a", "\\a").replace("\b", "\\b").replace("\f", "\\f").replace("\r", "\\r").replace("\t", "\\t").replace("\v", "\\v")
        self.ESCAPE_CHARS = ['\b', '\n', '\v', '\t', '\f', "'", '"', '\a', '\r']
        self.inBuffer = ""
        self.displayInHex = True
        self.getCharFlag = False

        self.LIST_TYPE = type([1, 1])
        self.keysDown = {}
        self.shrunk = True

        # Two Final GUI elements
        self.win.show_all()

        # This GUI element needs the as88 defined
        self.makeHelpBox()
        self.notebook.set_visible(False)

    def setBreakpoint(self, widget, event):
        if self.breakpointDClickTime == 0:
            self.breakpointDClickTime = time.time()
        else:
            if time.time() - self.breakpointDClickTime < 0.2:
                self.breakpointDClickTime = 0
                breakPoint = self.lineNumberTV.get_iter_at_location(event.x, event.y).get_line()
                start = self.linesBuffer.get_iter_at_line(breakPoint)

                if breakPoint + 1 == self.linesBuffer.get_line_count():
                    end = self.linesBuffer.get_end_iter()
                else:
                    end = self.linesBuffer.get_iter_at_line_offset(breakPoint + 1, 0)

                if breakPoint in self.breakPoints:
                    self.breakPoints.remove(breakPoint)
                    self.linesBuffer.remove_tag(self.textTagBreakpoint, start, end)
                else:
                    self.breakPoints.append(breakPoint)
                    self.linesBuffer.apply_tag(self.textTagBreakpoint, start, end)
            else:
                self.breakpointDClickTime = time.time()

    def openFile(self):
        """Opens up a file dialog to select a file then reads that file in to the assembler. """

        fileChooser = Gtk.FileChooserDialog(title="Choose A File", parent=self.win, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = fileChooser.run()

        fileName = None
        if response == Gtk.ResponseType.OK:
            fileName = fileChooser.get_filename()

        fileChooser.destroy()

        if fileName == None:
            return

        self.open(fileName)

    def open(self, fileName):
        """ Opens and reads in the file fileName """
        try:
            self.fileName = None
            self.running = False
            self.ran = False

            f = open(fileName, 'r')

            self.codeString = f.read()

            self.codeBuffer.set_text(self.codeString)

            f.seek(0)

            self.syntaxHighlight(f)

            f.close()

            self.outBuffer.set_text("")
            self.fileName = fileName
            self.updateWindowTitle()
            # self.win.set_title(self._PROGRAMNAME + " - " + "Untitled" if self.fileName == None else self.fileName)

        except IOError:
            self.outPut("There was a fatal issue opening " + fileName + ". Are you sure it's a file?")

    def clickSeperator(self, a, b):
        """When the separator label is clicked, expand the viewport."""
        if self.shrunk:
            self.notebook.set_visible(True)
            self.shrunk = False
        else:
            self.notebook.set_visible(False)
            self.shrunk = True

    def syntaxHighlight(self, f, lineOffset=0):
        """Highlight the syntax of the text in the codeBuffer."""
        self.commentLine = -1

        def handleSyntaxHighlightingToken(typeOfToken, token, (srow, scol), (erow, ecol), line):
            """Get's called by tokenizer to handle each token."""

            # print "%d,%d-%d,%d:\t%s\t%s" % \
            #    (srow, scol, erow, ecol, tokenize.tok_name[typeOfToken], repr(token))

            if tokenize.tok_name[typeOfToken] == "ENDMARKER":
                self.updateLineCounter()
            elif repr(token) == "'!'":
                self.commentLine = line
                # self.codeBuffer.remove_all_tags(self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                self.codeBuffer.apply_tag(self.textTagLightGreyText, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + srow, 0))

            comment = self.commentLine == line

            # print repr(token), tokenize.tok_name[typeOfToken]
            if tokenize.tok_name[typeOfToken] == "NAME":
                if not comment:
                    self.codeBuffer.remove_all_tags(self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                    if repr(token).upper().strip("'") in self.functions:
                        self.codeBuffer.apply_tag(self.textTagBold, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                    elif repr(token).upper().strip("'") in self.machine.registers.keys():
                        self.codeBuffer.apply_tag(self.textTagBold, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                        self.codeBuffer.apply_tag(self.textTagBlueText, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                    elif repr(token).upper().strip("'") in self.machine.eightBitRegisterNames():
                        self.codeBuffer.apply_tag(self.textTagBlueText, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                    elif repr(token).upper().strip("'") in ["SECT", "DATA", "BSS", "TEXT"]:
                        self.codeBuffer.apply_tag(self.textTagBold, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                        self.codeBuffer.apply_tag(self.textTagGreyText, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                    else:
                        self.codeBuffer.apply_tag(self.textTagRedText, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
            elif tokenize.tok_name[typeOfToken] == "NUMBER":
                self.codeBuffer.remove_all_tags(self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
                self.codeBuffer.apply_tag(self.textTagGreenText, self.codeBuffer.get_iter_at_line_offset(lineOffset + srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(lineOffset + erow - 1, ecol))
            else:
                1
                # print "%d,%d-%d,%d:\t%s\t%s" % \
                #    (srow, scol, erow, ecol, tokenize.tok_name[typeOfToken], repr(token))

        tokenize.tokenize(f.readline, handleSyntaxHighlightingToken)

    def hoverOverSeperator(self, a, b):
        """Change the style of the separator label when hovered on."""
        self.seperatorLabel.set_name("seperatorLabelOver" + str(self.shrunk))

    def hoverOffSeperator(self, a, b):
        """Change the style of the separator label when hovered off."""
        self.seperatorLabel.set_name("seperatorLabel" + str(self.shrunk))

    def updateLineCounter(self):
        """Updates the line number label on the left of the code block. get's called whenever the lines change."""
        self.linesBuffer.set_text("\n".join([" " + str(x) for x in range(self.codeBuffer.get_line_count())]))

    def updateRegisters(self):
        """ Simply put, updates the register, flags, and memory gui elements with their respective values. """

        self.oFlagOutMachine.set_text(str(int(self.machine.flags['O'])))
        self.dFlagOutMachine.set_text(str(int(self.machine.flags['D'])))
        self.iFlagOutMachine.set_text(str(int(self.machine.flags['I'])))
        self.sFlagOutMachine.set_text(str(int(self.machine.flags['S'])))
        self.zFlagOutMachine.set_text(str(int(self.machine.flags['Z'])))
        self.aFlagOutMachine.set_text(str(int(self.machine.flags['A'])))
        self.pFlagOutMachine.set_text(str(int(self.machine.flags['P'])))
        self.cFlagOutMachine.set_text(str(int(self.machine.flags['C'])))

        if self.displayInHex:
            self.regA.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['AX']))) + self.machine.intToHex(self.machine.registers['AX']))
            self.regAH.set_text(self.machine.intToHex(self.machine.eightBitRegister('AH')))
            self.regAL.set_text(self.machine.intToHex(self.machine.eightBitRegister('AL')))
            self.regB.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['BX']))) + self.machine.intToHex(self.machine.registers['BX']))
            self.regBH.set_text(self.machine.intToHex(self.machine.eightBitRegister('BH')))
            self.regBL.set_text(self.machine.intToHex(self.machine.eightBitRegister('BL')))
            self.regC.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['CX']))) + self.machine.intToHex(self.machine.registers['CX']))
            self.regCH.set_text(self.machine.intToHex(self.machine.eightBitRegister('CH')))
            self.regCL.set_text(self.machine.intToHex(self.machine.eightBitRegister('CL')))
            self.regD.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['DX']))) + self.machine.intToHex(self.machine.registers['DX']))
            self.regDH.set_text(self.machine.intToHex(self.machine.eightBitRegister('DH')))
            self.regDL.set_text(self.machine.intToHex(self.machine.eightBitRegister('DL')))
            self.regBP.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['BP']))) + self.machine.intToHex(self.machine.registers['BP']))
            self.regSP.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['SP']))) + self.machine.intToHex(self.machine.registers['SP']))
            self.regDI.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['DI']))) + self.machine.intToHex(self.machine.registers['DI']))
            self.regSI.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['SI']))) + self.machine.intToHex(self.machine.registers['SI']))
            self.regPC.set_text("0"*(4 - len(self.machine.intToHex(self.machine.registers['PC']))) + self.machine.intToHex(self.machine.registers['PC']))
            self.memoryBuffer.set_text("".join([self.machine.intToHex(ord(x)) for x in self.machine.addressSpace[:144]]))
            self.colourMemory()
        else:
            self.regA.set_text(str(self.machine.registers['AX']))
            self.regAH.set_text(str(self.machine.eightBitRegister('AH')))
            self.regAL.set_text(str(self.machine.eightBitRegister('AL')))
            self.regB.set_text(str(self.machine.registers['BX']))
            self.regBH.set_text(str(self.machine.eightBitRegister('BH')))
            self.regBL.set_text(str(self.machine.eightBitRegister('BL')))
            self.regC.set_text(str(self.machine.registers['CX']))
            self.regCH.set_text(str(self.machine.eightBitRegister('CH')))
            self.regCL.set_text(str(self.machine.eightBitRegister('CL')))
            self.regD.set_text(str(self.machine.registers['DX']))
            self.regDH.set_text(str(self.machine.eightBitRegister('DH')))
            self.regDL.set_text(str(self.machine.eightBitRegister('DL')))
            self.regBP.set_text(str(self.machine.registers['BP']))
            self.regSP.set_text(str(self.machine.registers['SP']))
            self.regDI.set_text(str(self.machine.registers['DI']))
            self.regSI.set_text(str(self.machine.registers['SI']))
            self.regPC.set_text(str(self.machine.registers['PC']))
            self.memory.get_buffer().set_text("".join([self.escapeSequences(x) for x in self.machine.addressSpace[:288 - self.backSlashCount]]))
            self.colourMemory()

    def makeHelpBox(self):
        """Called at construction, creates the help box including a TreeView to display assembly instructions
        and a text view to display the selected instructions documentation."""
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
            if treeiter != None:
                rawHelpText = str(self.do[model[treeiter][0]].__doc__).split("\n")
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
                            self.reg8Arg.set_name("reg8On")
                        elif arg == "reg16":
                            self.reg16Arg.set_name("reg16On")
                        elif arg == "reg8":
                            self.reg16Arg.set_name("reg8On")
                        elif arg == "mem":
                            self.memArg.set_name("memOn")
                        elif arg == "immed":
                            print 'immed'
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
                                self.reg8Arg2.set_name("reg8On")
                            elif arg == "reg16":
                                self.reg16Arg2.set_name("reg16On")
                            elif arg == "reg8":
                                self.reg16Arg2.set_name("reg8On")
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

                flagsOut = (self.oFlagOut, self.dFlagOut, self.iFlagOut, self.sFlagOut, self.zFlagOut, self.aFlagOut, self.pFlagOut, self.cFlagOut)
                for index, flag in enumerate(flags):
                    flagsOut[index].set_text(flag)

                self.instructionName.set_text(instructionName)
                self.instructionTitle.set_text(instructionTitle)
                self.instructionDescription.get_buffer().set_text(instructionDescription)

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
        # self.entry.set_name("entry")
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
        self.builder.get_object("registersEndLabel").set_name("registersEndLabel")

        self.memory.set_name("memory")
        self.notebook.set_name("notebook")
        self.seperatorLabel.set_name("seperatorLabelTrue")
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

        self.builder.get_object("instructionHelpBox").set_name("instructionHelpBox")

    def assignGuiElementsToVariables(self):
        """ Binds critical GUI elements from the builder object to variable names. """
        self.outText = self.builder.get_object("outText")
        self.code = self.builder.get_object("code")
        # self.entry = self.builder.get_object("entry")
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

        self.seperatorLabelEB = self.builder.get_object("seperatorLabelEB")
        self.seperatorLabel = self.builder.get_object("seperatorLabel")

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

        self.instructionDescription = self.builder.get_object("instructionDescription")
        self.instructionName = self.builder.get_object("instructionName")
        self.instructionTitle = self.builder.get_object("instructionTitle")

    def setUpTextTags(self):
        """ Constructs the various text tags used to style text within textviews. """
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

        self.memoryBuffer.get_tag_table().add(self.textTagGrey)
        self.memoryBuffer.get_tag_table().add(self.textTagRed)
        self.memoryBuffer.get_tag_table().add(self.textTagOrange)
        self.memoryBuffer.get_tag_table().add(self.textTagMagenta)
        self.memoryBuffer.get_tag_table().add(self.textTagGreen)
        self.memoryBuffer.get_tag_table().add(self.textTagBlue)
        self.memoryBuffer.get_tag_table().add(self.textTagPurple)
        self.memoryColours = [self.textTagRed, self.textTagOrange, self.textTagMagenta, self.textTagGreen, self.textTagBlue, self.textTagPurple, self.textTagGrey]


        self.textTagBreakpoint = Gtk.TextTag()
        self.textTagBreakpoint.set_property("background", "red")
        self.linesBuffer.get_tag_table().add(self.textTagBreakpoint)

    def updateStatusLabel(self, *args):
        """ Updates the status label at the bottom of the screen, including current line number,
        status of the simulation, etc. """
        self.statusLabel.set_text(" Line: " + str(self.codeBuffer.get_iter_at_offset(self.codeBuffer.props.cursor_position).get_line()) + "\t" + self.running * "Running")

    def updateStack(self, data=""):
        """ Updates the stack gui element """
        # self.outBuffer.apply_tag(self.textTagBold, self.outBuffer.get_start_iter(), self.outBuffer.get_end_iter())
        if data != "": self.machine.stackData.append(str(data))
        if self.displayInHex:
            GObject.idle_add(lambda: self.stackBuffer.set_text("\n".join(["0"*(4 - len(hex(int(x)).split("x")[1])) + hex(int(x)).split("x")[1] for x in self.machine.stackData])))
        else:
            GObject.idle_add(lambda: self.stackBuffer.set_text("\n".join(["0"*(4 - len(str(x))) + str(x) for x in self.machine.stackData])))

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
        if self.downFile != "":
            newFileName = self.downFile
            self.downFile = ""
        else:
            newFileName = widget.get_child().props.file.replace(".", "Over.")
            newFileName = newFileName.replace("OverOver.", "Over.")

        widget.get_child().set_from_file(newFileName)

    def releaseFileButton(self, widget, event):
        widget.get_child().set_from_file(self.downFile)
        self.downFile = ""

    def hoverOffFileButton(self, widget, event):
        if self.downFile != "":
            newFileName = self.downFile.replace("Over.", ".")
            self.downFile = ""
        else:
            newFileName = widget.get_child().props.file.replace("Over.", ".")

        widget.get_child().set_from_file(newFileName)

    def makeFileButtons(self):
        """ Creates the file buttons on the bottom of the screen: includes
        New, Open, Save, Run All, Step Once, Stop Stimulation """

        new = Gtk.Image()
        new.set_from_file(self._PATH + "/images/newFileIcon.png")

        newEB = Gtk.EventBox()
        newEB.add(new)
        newEB.set_tooltip_text("New")

        self.buttonBox.pack_start(newEB, False, False, 1)

        openImage = Gtk.Image()
        openImage.set_from_file(self._PATH + "/images/openIcon.png")

        openEB = Gtk.EventBox()
        openEB.add(openImage)
        openEB.set_tooltip_text("Open")

        self.buttonBox.pack_start(openEB, False, False, 1)

        save = Gtk.Image()
        save.set_from_file(self._PATH + "/images/saveIcon.png")

        saveEB = Gtk.EventBox()
        saveEB.add(save)
        saveEB.set_tooltip_text("Save")

        self.buttonBox.pack_start(saveEB, False, False, 1)

        allIcon = Gtk.Image()
        allIcon.set_from_file(self._PATH + "/images/allIcon.png")

        allEB = Gtk.EventBox()
        allEB.add(allIcon)
        allEB.set_tooltip_text("Run All")

        self.buttonBox.pack_start(allEB, False, False, 1)

        step = Gtk.Image()
        step.set_from_file(self._PATH + "/images/stepIcon.png")

        stepEB = Gtk.EventBox()
        stepEB.add(step)
        stepEB.set_tooltip_text("Run One Line")

        self.buttonBox.pack_start(stepEB, False, False, 1)

        stop = Gtk.Image()
        stop.set_from_file(self._PATH + "/images/stopIcon.png")

        stopEB = Gtk.EventBox()
        stopEB.add(stop)
        stopEB.set_tooltip_text("Stop Running")
        self.buttonBox.pack_start(stopEB, False, False, 1)

        for x in [newEB, openEB, saveEB, allEB, stepEB, stopEB]:
            x.connect('button_release_event', self.releaseFileButton)
            x.connect('enter-notify-event', self.hoverOverFileButton)
            x.connect('leave-notify-event', self.hoverOffFileButton)

        newEB.connect('button_press_event', self.pressNewButton)
        openEB.connect('button_press_event', self.pressOpenButton)
        saveEB.connect('button_press_event', self.pressSaveButton)
        stepEB.connect('button_press_event', self.pressStepButton)
        allEB.connect('button_press_event', self.pressAllButton)
        stopEB.connect('button_press_event', self.pressStopButton)

    def pressNewButton(self, widget, event):
        if self.downFile == "": self.downFile = widget.get_child().props.file

        widget.get_child().set_from_file(self._PATH + "/images/empty.png")
        self.new()

    def pressOpenButton(self, widget, event):
        if self.downFile == "": self.downFile = widget.get_child().props.file

        widget.get_child().set_from_file(self._PATH + "/images/empty.png")
        self.openFile()

    def pressStepButton(self, widget, event):
        if self.downFile == "": self.downFile = widget.get_child().props.file

        widget.get_child().set_from_file(self._PATH + "/images/empty.png")
        self.stepButtonClicked()

    def pressAllButton(self, widget, event):
        if self.downFile == "": self.downFile = widget.get_child().props.file

        widget.get_child().set_from_file(self._PATH + "/images/empty.png")
        self.runAll()

    def pressSaveButton(self, widget, event):
        if self.downFile == "": self.downFile = widget.get_child().props.file

        widget.get_child().set_from_file(self._PATH + "/images/empty.png")
        self.saveFile()

    def pressStopButton(self, widget, event):
        if self.downFile == "": self.downFile = widget.get_child().props.file

        widget.get_child().set_from_file(self._PATH + "/images/empty.png")

        if self.running: self.stopRunning(1)
        self.updateStatusLabel()

    def saveFile(self, saveAs=False):
        """ Saves the file.  If the file hans't been previously saved or if saveAs == True then a dialog propmts the user for a location
        else it'll save in the same place it has been historically saved. """
        if self.fileName == None or saveAs:
            fileChooser = Gtk.FileChooserDialog("Save your file", self.win, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
            response = fileChooser.run()

            fileName = None
            if response == Gtk.ResponseType.ACCEPT:
                fileName = fileChooser.get_filename()

            fileChooser.destroy()
            self.fileName = fileName
            if fileName != None: self.saveFile()
        else:
            try:
                file = open(self.fileName, "w")
                file.write(self.codeBuffer.get_text(self.codeBuffer.get_start_iter(), self.codeBuffer.get_end_iter(), False))
                file.close()

                self.codeBuffer.set_modified(False)
                self.updateWindowTitle()
            except IOError:
                """ Fatal error popup """
                print "Fatal Error"

    def new(self):
        """ Resets the simulation and code """
        self.backSlashCount = 0
        self.breakPoints = []
        self.updateWindowTitle()
        self.fileName = None

        self.outBuffer.set_text("")
        self.codeBuffer.set_modified(False)
        self.codeBuffer.remove_all_tags(self.codeBuffer.get_start_iter(), self.codeBuffer.get_end_iter())
        self.codeBuffer.set_text("")

        self.machine = Intel8088.Intel8088()

        as88 = CommandInterpreter.CommandInterpreter(self, self.machine)

        self.commandArgs = as88.getCommandArgs()
        self.do = as88.getFunctionTable()
        self.functions = self.do.keys()
        self.functions.sort()
        # self.sysCodes = as88.getSysCodes()

        self.lineCount = 0

        self.mode = "head"
        self.running = False
        self.ran = False

    def runAll(self):
        """ If the simulation isn't running, then it is started and run in full with the GUI only being updated afterwards.
            If the simulation is running, then it runs until completion from it's current state, with GUI only being updated after.
            If the simulation has already run, then it prompts the user if he wishes to restart, and does so. """
        if not self.ran:  # If we aren't waiting on a restart prompt
            if not self.running:  # if We're not running, start
                self.startRunning()
            else:
                startOfArrow = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 0)  # If we are running, we got a arrow to get ridda
                endOfArrow = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 1)
                self.codeBuffer.delete(startOfArrow, endOfArrow)

            while self.running:
                if self.machine.registers['PC'] in self.breakPoints:
                    currentLineIter = self.codeBuffer.get_iter_at_line(self.machine.registers['PC'])
                    self.codeBuffer.insert(currentLineIter, ">")
                    self.step()
                    break
                self.step()

            self.updateRegisters()
        else:
            if self.restartPrompt(): self.runAll()

    def restartPrompt(self):
        """ Presents a dialog asking the user if they wish to restart the simulation """
        dialog = Gtk.MessageDialog(self.win, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, "Do You Wish to Restart?", title="Restart the simulation?")

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
        """Loads in the code to run, intialises all local variables and labels as set up in the code.
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

            if ".SECT" in line.upper():

                # record where the .SECT .TEXT section starts, and ends
                if self.mode == ".SECT .TEXT":  # ends, we've gone one too far, but we count from zero
                    self.machine.codeBounds[1] = self.lineCount - 1
                elif line.upper() == ".SECT .TEXT":  # starts, we're one too short, and we count from zero
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

                    if ".ASCIZ" in line.upper() or ".ASCII" in line.upper():  # If we're dealing with a string
                        if line.count("\"") < 2:  # each string to be defined should be in quotes, raise error if quotes are messed
                            self.outPut("fatal error on line " + str(self.lineCount))
                            errorCount += 1
                            return None
                        temp2 = self.replaceEscapedSequences(line[line.find("\"") + 1:line.rfind("\"")])  # otherwise grab the stuff in quotes
                        self.machine.DATA[temp] = [BSScount, BSScount + len(temp2) + (".ASCIZ" in line.upper()) - 1]  # and set temp equal to a list of hex vals of each char
                        self.machine.addressSpace[BSScount:BSScount + len(temp2)] = temp2 + "0"*(".ASCIZ" in line.upper())
                        BSScount += len(temp2) + (".ASCIZ" in line.upper())

                elif self.mode == ".SECT .BSS":
                    # info in .SECT .BSS follows the format
                    # fdes: .SPACE 2
                    # Where essentially .BSS just defines memory space

                    temp2 = line.split(".SPACE")[1]  # let's find the size of the mem chunk to def
                    self.machine.BSS[temp.strip()] = [BSScount, BSScount + int(temp2.strip()) - 1]  # and def it in bss as it's start and end pos
                    BSScount += int(temp2.strip())

        if self.mode == ".SECT .TEXT" and self.machine.codeBounds[1] == -1:
            self.machine.codeBounds[1] = len(self.lines)

        # TODO: error check before second pass
        """ SECOND PASS """
        if errorCount == 0:
            self.machine.registers['PC'] = self.machine.codeBounds[0]
            self.running = True
        else:
            self.outPut("Your code cannot be run, it contains %d errors" % errorCount)


    def stepButtonClicked(self):
        """ Defines what happens if the step button is clicked.
        This is fired if the user interacts with the GUI to step in anyway (i.e. key combos, menu items, buttons, etc.)
        This calls the step() function to execute a line of code
        and performs all graphical duties before and after executing the code.
        
        If the code has already been run to completion this prompts the user asking if they wish to restart (deprecate?).
        """
        if self.running:
            # Scroll to view the line
            self.code.scroll_to_iter(self.code.get_buffer().get_iter_at_line(self.machine.registers['PC']), 0.25, True, .5, .5)
            self.codeBuffer.place_cursor(self.code.get_buffer().get_iter_at_line(self.machine.registers['PC']))

            # insert a >
            currentLineIter = self.codeBuffer.get_iter_at_line(self.machine.registers['PC'])
            self.codeBuffer.insert(currentLineIter, ">")

            # remove the > from the previous line, -1 means we're at the first line
            if self.machine.lastLine != -1:
                startOfArrow = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 0)
                endOfArrow = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 1)
                self.codeBuffer.delete(startOfArrow, endOfArrow)
            self.step()

        elif self.ran:
            """ Prompt the user to restart """
            if self.restartPrompt(): self.stepButtonClicked()

        else:
            self.startRunning()
            self.stepButtonClicked()

    def step(self):
        """ This executes a single line of code. 
        Parses the command and performs basic error checking 
            (are we done the program? 
            does the command follow proper syntax (i.e. right arguments)?
            is the command recognised?)
        Before passing it off to the command interpreter class."""
        if self.running:

            if self.machine.registers['PC'] >= self.machine.codeBounds[1]:
                self.stopRunning()
                return

            line = self.lines[self.machine.registers['PC']].replace("\t", "")  # clear out tabs

            if "!" in line:  # exclamations mean comments
                line = line[:line.find("!")].strip()  # ignore comments

            if ":" in line:  # colons mean labels, we dealt with those already.
                line = line[line.find(":") + 1:].strip()  # ignore jump points

            if line.count(",") > 1:  # any command can have at most 2 arguments.
                self.outPut("What's up with all the commas on line " + str(self.machine.registers['PC']) + "?")
                self.running = False
                self.ran = True
                return -1

            command = [x.strip() for x in line.replace(" ", ",").split(",")]

            for x in range(command.count("")):
                command.remove("")

            if command == None or command == []:
                self.machine.lastLine = self.machine.registers['PC']
                self.machine.registers['PC'] += 1
                return  # skip the empty lines

            if command[0] not in self.commandArgs.keys():
                print "Fatal error. " + command[0] + " not recognised."
                self.outPut("Fatal error. " + command[0] + " not recognised.")
                self.stopRunning(-1)
                return

            if len(command) - 1 != self.commandArgs[command[0]]:
                self.outPut("Invalid number of arguments on line " + str(self.machine.registers['PC']) + ". " + command[0] + " expects " + str(self.commandArgs[command[0]]) + " argument" + "s"*(self.commandArgs[command[0]] > 1) + " and " + str(len(command) - 1) + (" were " if len(command) - 1 > 1 else " was ") + "given.")
                self.running = False
                self.ran = True
                return -1

            if command[0] in self.do.keys():
                self.do[command[0]](command, self.machine.registers['PC'])
                self.updateRegisters()
            else:
                self.outPut("Fatal error. " + command[0] + " not recognised.")
                self.stopRunning(-1)
                return

            if self.machine.jumpLocation != -1:
                self.machine.lastLine = self.machine.registers['PC']
                self.machine.registers['PC'] = self.machine.jumpLocation
                self.machine.jumpLocation = -1
            else:
                self.machine.lastLine = self.machine.registers['PC']
                self.machine.registers['PC'] += 1

            if self.machine.registers['PC'] >= self.machine.codeBounds[1]:
                self.stopRunning()
                return

    def onKeyPressEvent(self, widget, event):
        """ Handles Key Down events, puts the corresponding keyval into a list self.keysDown.
        Also checks for key combinations. """

        keyval = event.keyval

        keyname = Gdk.keyval_name(keyval)

        mod = Gtk.accelerator_get_label(keyval, event.state)
        # Possibly a better way ^^ weird things with MOD though.
        # label.set_markup('<span size="xx-large">%s\n%d</span>' % (mod, keyval))

        if keyname == 'Return' or keyname == 'KP_Enter':
            if not self.getCharFlag:
                if not self.code.has_focus():
                    self.stepButtonClicked()
            else:
                # self.inBuffer = self.entry.get_text() + "\n"
                self.machine.registers["AX"] = ord(self.inBuffer[0])
                self.outPut(self.inBuffer + "\n")
                self.inBuffer = self.inBuffer[1:]
                self.getCharFlag = False
            return

        self.keysDown[keyname] = time.time()

        for key in self.keysDown.keys():
            if time.time() - self.keysDown[key] > self._KEYTIMEOUT:
                self.keysDown.pop(key)

        if len(self.keysDown) == 2 and (('O' in self.keysDown) ^ ('o' in self.keysDown)) and (('Control_L' in self.keysDown) ^ ('Control_R' in self.keysDown)):
            self.keysDown = {}
            self.openFile()
        elif len(self.keysDown) == 2 and (('S' in self.keysDown) ^ ('s' in self.keysDown)) and (('Control_L' in self.keysDown) ^ ('Control_R' in self.keysDown)):
            self.keysDown = {}
            self.saveFile()
        elif len(self.keysDown) == 2 and (('N' in self.keysDown) ^ ('n' in self.keysDown)) and (('Control_L' in self.keysDown) ^ ('Control_R' in self.keysDown)):
            self.keysDown = {}
            self.new()
        elif len(self.keysDown) == 2 and (('Q' in self.keysDown) ^ ('q' in self.keysDown)) and (('Control_L' in self.keysDown) ^ ('Control_R' in self.keysDown)):
            self.keysDown = {}
            self.exit()

    def outPut(self, string):
        """ Outputs the argument """
        self.outText.get_buffer().insert(self.outText.get_buffer().get_end_iter(), string)
        self.outText.scroll_to_iter(self.outText.get_buffer().get_end_iter(), 0.1, True, .5, .5)

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
                            # self.regFlags.get_buffer().set_text(""),
                            self.memory.get_buffer().set_text("")))

    def updateWindowTitle(self):
        self.win.set_title(self._PROGRAMNAME + " - " + ("*"*self.codeBuffer.get_modified()) + ("Untitled" if self.fileName == None else self.fileName))

    def textChanged(self, widget):
        """ This function gets called everytime the 'code' text changes.
        Syntax Highglighting is applied on the changed line appropriately. """
        if not self.running:
            self.updateWindowTitle()
            lineNumber = self.codeBuffer.get_iter_at_offset(self.codeBuffer.props.cursor_position).get_line()

            startOfLineIter = self.codeBuffer.get_iter_at_line_offset(lineNumber, 0)

            if lineNumber + 1 == self.codeBuffer.get_line_count():
                endOfLineIter = self.codeBuffer.get_end_iter()
            else:
                endOfLineIter = self.codeBuffer.get_iter_at_line_offset(lineNumber + 1, 0)

            lineText = self.codeBuffer.get_text(startOfLineIter, endOfLineIter, False)

            self.syntaxHighlight(ReadLiner.ReadLiner(lineText), lineOffset=lineNumber)

    def makeAboutDialogue(self):
        """ Makes an About Dialog displaying basic info about the program
        (Name, Copyright, version, logo, website, license) """
        about = Gtk.AboutDialog()
        about.set_name("AboutDialog")
        about.set_program_name(self._PROGRAMNAME)
        about.set_version(self._VERSION)
        about.set_copyright("(c) Brydon Eastman")
        about.set_comments(self._DESCRIPTION)
        about.set_website(self._WEBSITE)
        about.set_license_type(self._LICENSE)
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file(self._PATH + "/images/logo.png"))
        about.run()
        about.destroy()

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

    def onKeyReleaseEvent(self, widget, event):
        """ Handles Key Up events, removes the corresponding keyval from the list self.keysDown. """
        keyname = Gdk.keyval_name(event.keyval)

        if keyname in self.keysDown.keys(): self.keysDown.pop(keyname)

    def hexSwitchClicked(self, button=None, data=None):
        """ Gets called when the hex switch is toggled,
        this switch changes it so the registers, stack, and memory all display in either hex or ascii """
        self.displayInHex = not self.displayInHex
        self.updateRegisters()
        self.updateStack()

    def replaceEscapedSequences(self, string):
        """ Replaces all escaped sequences with their unescaped counterparts """
        return string.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"').replace("\\a", "\a").replace("\\b", "\b").replace("\\f", "\f").replace("\\r", "\r").replace("\\t", "\t").replace("\\v", "\v")

    def escapeSequences(self, string):
        """ Escapes all things that may need escaped. """
        return string.replace("\n", "\\n").replace("\'", "\\'").replace('\"', '\\"').replace("\a", "\\a").replace("\b", "\\b").replace("\f", "\\f").replace("\r", "\\r").replace("\t", "\\t").replace("\v", "\\v")

    def stopRunning(self, i=1):
        """ Ends the current simulation, if i=1 then succesfully, otherwise there was an issue """
        self.running = False
        self.ran = True
        self.code.set_editable(True)

        startOfArrow = self.codeBuffer.get_iter_at_line_offset(self.machine.registers['PC'], 0)
        endOfArrow = self.codeBuffer.get_iter_at_line_offset(self.machine.registers['PC'], 1)

        if self.codeBuffer.get_text(startOfArrow, endOfArrow, False) == ">":
            self.codeBuffer.delete(startOfArrow, endOfArrow)
        else:
            startOfArrow = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 0)
            endOfArrow = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 1)
            if self.codeBuffer.get_text(startOfArrow, endOfArrow, False) == ">":
                self.codeBuffer.delete(startOfArrow, endOfArrow)


        if i == 1:
            self.outPut("\n----\nCode executed succesfully.\n")
        else:
            self.outPut("\n----\nCode execution terminated.\n")
        # TODO: EOF, anything important like that should go here.

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
        self.backSlashCount = 0
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
                    self.backSlashCount += 1
            before = location[0] * (self.displayInHex + 1) + backSlashOffsetBeforeTag * (not self.displayInHex)
            after = (location[1] + 1) * (self.displayInHex + 1) + backSlashOffsetAfterTag * (not self.displayInHex)

            self.machine.effectiveBSSandDATALocation[location[2]] = [before, after]

            self.memoryBuffer.apply_tag(self.memoryColours[index % len(self.memoryColours)], self.memoryBuffer.get_iter_at_offset(before), self.memoryBuffer.get_iter_at_offset(after))

    def exit(self, *args):
        """ Determines whether or not to exit, if there is an unsaved file or active simulation it prompts the user.
        Then decides whether to exit the program or not based on the users response. """
        if self.running:
            dialog = Gtk.MessageDialog(self.win, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, "Do you want to quit?", title="Are you sure?")
            dialog.format_secondary_text("There is a simulation currently in progress.")

            response = dialog.run()

            if response == Gtk.ResponseType.NO:
                dialog.destroy()
                return True  # Returning true tells GTK to not kill this win

            dialog.destroy()
        if self.codeBuffer.get_modified():
            dialog = Gtk.MessageDialog(self.win, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, "Do you want to quit?", title="Are you sure?")
            dialog.format_secondary_text("There are unsaved changes.")

            response = dialog.run()

            if response == Gtk.ResponseType.NO:
                dialog.destroy()
                return True  # Returning true tells GTK to not kill this win

            dialog.destroy()

        Gtk.main_quit(args)

def main():
    """ The entry point. """
    GObject.threads_init()

    A = Simulator()

    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            A.open(sys.argv[1])

    Gtk.main()

if __name__ == "__main__":
    main()
