from gi.repository import Gtk, Gdk, GObject, Pango
import CommandInterpreter, Intel8088
from Assembler import Assembler as OldAssembler

""""Assembler Class for Intel 8088 Architecture"""
class Assembler(OldAssembler):

    def __init__(self):

        """ Begin GUI """
        styles = """
* {
    border: 0px;
}        

#As88Window #helpTree {
    color:#000;
    background-color:#F5F5F5;
}

#As88Window #helpDisplayText {
    color:#000;
    background-color:#E5E5E5;
}

GtkNotebook, GtkEntry {
    border: 1px solid #333
}

#As88Window #codeScrolled {
    border-bottom: 3px solid #000;
}

#As88Window #seperatorLabelTrue {
    background-color:#200;
    border-right:1px solid #333;
    border-left:1px solid #333;
}

#As88Window #seperatorLabelFalse {
    background-color:#002;
    border-right:1px solid #333;
    border-left:1px solid #333;
}

#As88Window #seperatorLabelOverTrue {
    background-color:#666;
    border-right:1px solid #000;
    border-left:1px solid #000;
}

#As88Window #seperatorLabelOverFalse {
    background-color:#666;
    border-right:1px solid #000;
    border-left:1px solid #000;
}

#As88Window, GtkNotebook {
    background-color:#000;
}

GtkNotebook {
    color:#fff;
    margin-top:0;
    padding-top:0;
    margin-right:0;
    padding-right:0;
    margin-left:0;
    padding-left:0;
}

#As88Window #code {
    font-family: mono;
    border-bottom: 3px solid black;
}
#As88Window #outText {
    border:5px solid #000;
}

#As88Window #stack, #As88Window #regA, #As88Window #regB, #As88Window #regC, #As88Window #regD, #As88Window #regSP, #As88Window #regBP, #As88Window #regSI,#As88Window #regDI, #As88Window #regPC, #As88Window #regFlags, #As88Window #memory {
    background-color:#E5E5E5;
    font-family:mono;
    color:#000;
}

#fixed1 {
    background-color:#F0F;
}

#As88Window #outText {
    background-color:#333;
    font-family:mono;
    color:#FFF;
}
"""

        """Handlers for the actions in the interface."""
        class Handler:
            def onDeleteWindow(self, *args):
                Gtk.main_quit(*args)

            def onOpen(self, button):
                Assembler.openFile()

            def onButtonClicked(self, button):
                Assembler.stepButtonClicked()

        # Make stuff from the GLADE file and setup events
        self.builder = Gtk.Builder()
        self.builder.add_from_file("xml/GladeMockup3.glade")
        self.builder.connect_signals(Handler())

        self.win = self.builder.get_object("window1")
        self.win.set_name('As88Window')
        self.win.connect("destroy", Gtk.main_quit)

        # Set Up the CSS
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_data(styles)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Creating local vars for gui elements
        self.assignGuiElementsToVariables()

        # Text buffers for the big text-views
        self.setupTextBuffers()

        self.nameGuiElementsForCSS()

        self.makeFileButtons()

        # Hex Switch needs a special trigger signal that glade cannot understand
        self.hexSwitch.connect('notify::active', self.hexSwitchClicked)

        # Key events!
        self.win.connect('key_press_event', self.on_key_press_event)
        self.win.connect('key_release_event', self.on_key_release_event)

        self.eventbox.connect('button_press_event', self.clickSeperator)
        self.eventbox.connect('enter-notify-event', self.hoverOverSeperator)
        self.eventbox.connect('leave-notify-event', self.hoverOffSeperator)

        # Window Icon -> what shows up in unity bar/toolbar/etc.
        self.win.set_icon_from_file("images/icon.png")

        self.setUpTextTags()

        self.memory.props.has_tooltip = True

        # self.notebook.set_visible(False)
        for x in self.memoryColours:
            self.memory.connect("query-tooltip", self.toolTipOption, x)

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
        self.functions = self.do.keys()
        self.functions.sort()
        # self.sysCodes = as88.getSysCodes()

        self.makeHelpBox()

        self.LIST_TYPE = type([1, 1])

        self.lineCount = 0

        self.mode = "head"
        self.running = False
        self.ran = False
        self.restartPrompt = False

        self.keysDown = []
        self.shrunk = True

        self.win.show_all()
        self.notebook.set_visible(False)

    def clickSeperator(self, a, b):
        if self.shrunk:
            self.notebook.set_visible(True)
            self.shrunk = False
        else:
            self.notebook.set_visible(False)
            self.shrunk = True

    def syntaxHighlight(self, f):
        import tokenize

        self.commentLine = -1

        def handle_token(typeOfToken, token, (srow, scol), (erow, ecol), line):

            if repr(token) == "'!'":
                self.commentLine = line
                self.codeBuffer.apply_tag(self.textTagLightGreyText, self.codeBuffer.get_iter_at_line_offset(srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(srow, 0))

            comment = self.commentLine == line

            # print repr(token), tokenize.tok_name[typeOfToken]
            if tokenize.tok_name[typeOfToken] == "NAME":
                if not comment:
                    if repr(token).strip("'") in self.functions:
                        self.codeBuffer.apply_tag(self.textTagBold, self.codeBuffer.get_iter_at_line_offset(srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(erow - 1, ecol))
                    elif repr(token).strip("'") in self.machine.registers.keys():
                        self.codeBuffer.apply_tag(self.textTagBold, self.codeBuffer.get_iter_at_line_offset(srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(erow - 1, ecol))
                        self.codeBuffer.apply_tag(self.textTagBlueText, self.codeBuffer.get_iter_at_line_offset(srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(erow - 1, ecol))
                    elif repr(token).strip("'") in ["SECT", "DATA", "BSS", "TEXT"]:
                        self.codeBuffer.apply_tag(self.textTagBold, self.codeBuffer.get_iter_at_line_offset(srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(erow - 1, ecol))
                        self.codeBuffer.apply_tag(self.textTagGreyText, self.codeBuffer.get_iter_at_line_offset(srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(erow - 1, ecol))
                    else:
                        self.codeBuffer.apply_tag(self.textTagRedText, self.codeBuffer.get_iter_at_line_offset(srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(erow - 1, ecol))
            elif tokenize.tok_name[typeOfToken] == "NUMBER":
                self.codeBuffer.apply_tag(self.textTagGreenText, self.codeBuffer.get_iter_at_line_offset(srow - 1, scol), self.codeBuffer.get_iter_at_line_offset(erow - 1, ecol))
            else:
                1
                # print "%d,%d-%d,%d:\t%s\t%s" % \
                #    (srow, scol, erow, ecol, tokenize.tok_name[typeOfToken], repr(token))

        tokenize.tokenize(f.readline, handle_token)

    def hoverOverSeperator(self, a, b):
        self.seperatorLabel.set_name("seperatorLabelOver" + str(self.shrunk))

    def hoverOffSeperator(self, a, b):
        self.seperatorLabel.set_name("seperatorLabel" + str(self.shrunk))

    def makeHelpBox(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        box = self.builder.get_object("displayHelp")
        store = Gtk.ListStore(str)

        for x in self.functions:
            treeiter = store.append([x])

        tree = Gtk.TreeView(store)
        tree.set_name("helpTree")
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Command", renderer, text=0)

        tree.append_column(column)

        def on_tree_selection_changed(selection):
            model, treeiter = selection.get_selected()
            if treeiter != None:
                helpDisplayText.get_buffer().set_text(str(self.do[model[treeiter][0]].__doc__))

        tree.get_selection().connect("changed", on_tree_selection_changed)

        helpDisplayText = self.builder.get_object("helpDisplayText")
        helpDisplayText.set_name("helpDisplayText")

        scroll.add(tree)
        box.pack_start(scroll, True, True, 0)

    def nameGuiElementsForCSS(self):
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
        self.notebook.set_name("notebook")
        self.builder.get_object("fixed1").set_name("fixed1")
        self.seperatorLabel.set_name("seperatorLabelTrue")
        self.builder.get_object("codeScrolled").set_name("codeScrolled")
        self.builder.get_object("outScrolled").set_name("outScrolled")

    def assignGuiElementsToVariables(self):
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
        self.notebook = self.builder.get_object("notebook")
        self.eventbox = self.builder.get_object("eventbox")
        self.seperatorLabel = self.builder.get_object("seperatorLabel")
        self.buttonBox = self.builder.get_object("buttonBox")

    def setUpTextTags(self):
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

    def setupTextBuffers(self):
        self.outBuffer = self.outText.get_buffer()
        self.codeBuffer = self.code.get_buffer()
        self.stackBuffer = self.stack.get_buffer()
        self.memoryBuffer = self.memory.get_buffer()
        # Set up the text behaviour
        self.outText.set_wrap_mode(Gtk.WrapMode.WORD)
        self.memory.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.stack.set_justification(Gtk.Justification.CENTER)
        # self.code.set_wrap_mode(Gtk.WrapMode.WORD)

    def makeFileButtons(self):
        new = Gtk.Image()
        new.set_from_file("images/newFileIcon.png")

        newEB = Gtk.EventBox()
        newEB.add(new)

        self.buttonBox.pack_start(newEB, False, False, 1)

        open = Gtk.Image()
        open.set_from_file("images/openIcon.png")

        openEB = Gtk.EventBox()
        openEB.add(open)

        self.buttonBox.pack_start(openEB, False, False, 1)

        save = Gtk.Image()
        save.set_from_file("images/saveIcon.png")

        saveEB = Gtk.EventBox()
        saveEB.add(save)

        self.buttonBox.pack_start(saveEB, False, False, 1)

        allIcon = Gtk.Image()
        allIcon.set_from_file("images/allIcon.png")

        allEB = Gtk.EventBox()
        allEB.add(allIcon)

        self.buttonBox.pack_start(allEB, False, False, 1)

        step = Gtk.Image()
        step.set_from_file("images/stepIcon.png")

        stepEB = Gtk.EventBox()
        stepEB.add(step)

        self.buttonBox.pack_start(stepEB, False, False, 1)

        stop = Gtk.Image()
        stop.set_from_file("images/stopIcon.png")

        stopEB = Gtk.EventBox()
        stopEB.add(stop)
        self.buttonBox.pack_start(stopEB, False, False, 1)

        def pressFileButton(widget, event):
            self.downFile = widget.get_child().props.file
            widget.get_child().set_from_file("images/empty.png")

            if widget == stopEB:
                if self.running: self.stopRunning(1)
            elif widget == allEB:
                self.runAll()
            elif widget == stepEB:
                self.stepButtonClicked()
            elif widget == saveEB:
                self.saveFile()
            elif widget == openEB:
                self.openFile()
            elif widget == newEB:
                self.new()

        def hoverOverFileButton(widget, event):
            newFileName = widget.get_child().props.file.replace(".", "Over.")
            widget.get_child().set_from_file(newFileName)

        def releaseFileButton(widget, event):
            widget.get_child().set_from_file(self.downFile)
            self.downFile = ""

        def hoverOffFileButton(widget, event):
            newFileName = widget.get_child().props.file.replace("Over.", ".")
            widget.get_child().set_from_file(newFileName)

        for x in [newEB, openEB, saveEB, allEB, stepEB, stopEB]:
            x.connect('button_press_event', pressFileButton)
            x.connect('button_release_event', releaseFileButton)
            x.connect('enter-notify-event', hoverOverFileButton)
            x.connect('leave-notify-event', hoverOffFileButton)
        # stopButton = Gtk.Button()
        # stopButton.add(stop)

#        self.buttonBox.pack_start(stopButton, False, False, 0)
    def saveFile(self):
        1 + 1

    def new(self):
        1 + 1

    def runAll(self):
        while self.running:
            self.step()

    def stepButtonClicked(self):
        """ Defines what happens if the step button is clicked.
        If the entry text field is empty, step like normal.
        If the entry text field has a command in it execute accordingly
        If the entry text field has characters in it, that aren't recognised as a command, clear the entry and do nothing.
        """
        # Scroll to view the line
        self.code.scroll_to_iter(self.code.get_buffer().get_iter_at_line(self.machine.registers['PC']), 0.25, True, .5, .5)

        # insert a >
        iter = self.codeBuffer.get_iter_at_line(self.machine.registers['PC'])
        self.codeBuffer.insert(iter, ">")

        firstFlag = False
        # remove the > from the previous line, -1 means we're at the first line
        if self.machine.lastLine != -1:
            start = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 0)
            end = self.codeBuffer.get_iter_at_line_offset(self.machine.lastLine, 1)
            self.codeBuffer.delete(start, end)
        else:
            firstFlag = True

        if self.ran:
            if not self.restartPrompt:
                self.outPut("Do you wish to restart? (y/n)")
                self.restartPrompt = True
        elif self.running:
            self.step()

    def step(self):
        print self.machine.eightBitRegister('BL')
        """ The guts of the second pass. Where the magic happens! """
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
                print "empty cmd"
                self.machine.lastLine = self.machine.registers['PC']
                self.machine.registers['PC'] += 1
                return  # skip the empty lines

            if command[0] not in self.commandArgs.keys():
                print "Fatal error. " + command[0] + " not recognised."
                self.stopRunning(-1)
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
                print "Fatal error. " + command[0] + " not recognised."
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

    def on_key_press_event(self, widget, event):
        """ Handles Key Down events, puts the corresponding keyval into a list self.keysDown.
        Also checks for key combinations. """
        keyname = Gdk.keyval_name(event.keyval)

        if keyname == 'Return' or keyname == 'KP_Enter':
            if not self.getCharFlag:
                if not self.code.has_focus(): self.stepButtonClicked()
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

    def outPut(self, string):
        """ Outputs the argument """
        self.outText.get_buffer().insert(self.outText.get_buffer().get_end_iter(), string)
        self.outText.scroll_to_iter(self.outText.get_buffer().get_end_iter(), 0.1, True, .5, .5)

if __name__ == "__main__":

    GObject.threads_init()

    A = Assembler()
    Gtk.main()
