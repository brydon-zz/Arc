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

#As88Window #outText, #As88Window #stack, #As88Window #regA, #As88Window #regB, #As88Window #regC, #As88Window #regD, #As88Window #regSP, #As88Window #regBP, #As88Window #regSI,#As88Window #regDI, #As88Window #regPC, #As88Window #regFlags, #As88Window #memory {
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
        self.notebook = self.builder.get_object("notebook")
        self.eventbox = self.builder.get_object("eventbox")
        self.seperatorLabel = self.builder.get_object("seperatorLabel")

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
        self.notebook.set_name("notebook")
        self.builder.get_object("fixed1").set_name("fixed1")
        # self.builder.get_object("fixed2").set_name("fixed2")
        self.seperatorLabel.set_name("seperatorLabelTrue")

        self.builder.get_object("codeScrolled").set_name("codeScrolled")
        self.builder.get_object("outScrolled").set_name("outScrolled")

        # Set up the text behaviour
        self.outText.set_wrap_mode(Gtk.WrapMode.WORD)
        self.memory.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.stack.set_justification(Gtk.Justification.CENTER)
        # self.code.set_wrap_mode(Gtk.WrapMode.WORD)

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

        # self.win.show_all()

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

        self.notebook.set_visible(False)
        self.win.show_all()

    def clickSeperator(self, a, b):
        if self.shrunk:
            self.notebook.set_visible(True)
            self.shrunk = False
        else:
            self.notebook.set_visible(False)
            self.shrunk = True

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
        helpDisplayText.get_buffer().set_text("abcd")

        scroll.add(tree)
        box.pack_start(scroll, True, True, 0)

if __name__ == "__main__":

    GObject.threads_init()

    A = Assembler()
    print "Constructed"
    Gtk.main()
