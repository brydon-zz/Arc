from gi.repository import Gtk, Gdk, GObject, Pango
import CommandInterpreter, Intel8088
from Assembler import Assembler as Assemb

""""Assembler Class for Intel 8088 Architecture"""
class Assembler(Assemb):

    def __init__(self):

        """ Begin GUI """
        styles = """
* {
    border: 0px;
}        

GtkNotebook, GtkEntry {
    border: 1px solid #333
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
        self.builder.add_from_file("GladeMockup3.glade")
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
        self.builder.get_object("notebook").set_name("notebook")
        self.builder.get_object("fixed1").set_name("fixed1")
        self.builder.get_object("fixed2").set_name("fixed2")
        self.builder.get_object("fixed3").set_name("fixed3")

        # Set up the text behaviour
        self.outText.set_wrap_mode(Gtk.WrapMode.WORD)
        self.code.set_wrap_mode(Gtk.WrapMode.WORD)
        self.memory.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.stack.set_justification(Gtk.Justification.CENTER)

        # Hex Switch needs a special trigger signal that glade cannot understand
        self.hexSwitch.connect('notify::active', self.hexSwitchClicked)

        # Key events!
        self.win.connect('key_press_event', self.on_key_press_event)
        self.win.connect('key_release_event', self.on_key_release_event)
        # Window Icon -> what shows up in unity bar/toolbar/etc.
        self.win.set_icon_from_file("icon.png")

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
        # self.sysCodes = as88.getSysCodes()

        self.LIST_TYPE = type([1, 1])

        self.lineCount = 0

        self.mode = "head"
        self.running = False
        self.ran = False
        self.restartPrompt = False

        self.keysDown = []

if __name__ == "__main__":

    GObject.threads_init()

    A = Assembler()
    print "Constructed"
    Gtk.main()

