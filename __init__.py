#!/usr/bin/python2.7
from gi.repository import Gtk, Gdk, GObject, Pango
import threading, os, as88, time

# TODO: issues with restarting
# TODO: Implement the WHOLE reg set
# TODO: ASSEMBLE?
# TODO: Run all and run untils with input

""""Assembler Class for Intel 8088 Architecture"""
class Assembler:

	def __init__(self):

		""" Begin GUI """
		styles = """
#As88Window {
	background:url('bg.jpg');
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
				A.openFile()

			def onButtonClicked(self, button):
				A.stepButtonClicked()

		# Make stuff from the GLADE file and setup events
		self.builder = Gtk.Builder()
		self.builder.add_from_file("As88_Mockup.glade")
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
		self.memoryBuffer.get_tag_table().add(self.textTagRed)
		self.memoryBuffer.get_tag_table().add(self.textTagOrange)
		self.memoryBuffer.get_tag_table().add(self.textTagMagenta)
		self.memoryBuffer.get_tag_table().add(self.textTagGreen)
		self.memoryBuffer.get_tag_table().add(self.textTagBlue)
		self.memoryBuffer.get_tag_table().add(self.textTagPurple)

		self.memoryColours = [self.textTagRed, self.textTagOrange, self.textTagMagenta, self.textTagGreen, self.textTagBlue, self.textTagPurple]

		self.memory.props.has_tooltip = True
		self.memory.connect("query-tooltip", self.toolTipOption, self.textTagRed)
		self.memory.connect("query-tooltip", self.toolTipOption, self.textTagOrange)
		self.memory.connect("query-tooltip", self.toolTipOption, self.textTagGreen)
		self.memory.connect("query-tooltip", self.toolTipOption, self.textTagBlue)
		self.memory.connect("query-tooltip", self.toolTipOption, self.textTagPurple)
		self.memory.connect("query-tooltip", self.toolTipOption, self.textTagMagenta)
		""" End GUI """

		self.inBuffer = ""
		self.fileName = None
		self.displayInHex = True
		self.getCharFlag = False

		self.lookupTable = {}
		self.localVars = {}
		self.stackData = []
		self.DATA = {}
		self.BSS = {}

		as88.newAssembler(self)

		self.registers = as88.getRegisters()
		self.flags = as88.getFlags()
		self.commandArgs = as88.getCommandArgs()
		self.do = as88.getFunctionTable()
		# self.sysCodes = as88.getSysCodes()

		self.LIST_TYPE = type([1, 1])

		self.jumpLocation = -1

		self.lineCount = 0

		self.mode = "head"
		self.codeBounds = [1, 1]
		self.running = False
		self.ran = False
		self.restartPrompt = False

		self.addressSpace = []

		for i in range(1024):
			self.addressSpace.append(str(0))

		self.keysDown = []

	def toolTipOption(self, widget, x, y, keyboard_tip, tooltip, data):
		if keyboard_tip:
			offset = widget.props.buffer.cursor_position
			myiter = widget.props.buffer.get_iter_at_offset(offset)
		else:
			coords = widget.window_to_buffer_coords(Gtk.TextWindowType.TEXT, x, y)
			ret = widget.get_iter_at_position(coords[0], coords[1])

		if ret[0].has_tag(data):
			offset = ret[0].get_offset() / (1 + self.displayInHex)
			for element in self.BSS:
				if self.BSS[element][0] <= offset <= self.BSS[element][1]:
					tooltip.set_text("%s (from %s to %s)" % (element, self.intToHex(self.BSS[element][0]) if self.displayInHex else str(self.BSS[element][0]), self.intToHex(self.BSS[element][1]) if self.displayInHex else str(self.BSS[element][1])))
					break
			else:
				for element in self.DATA:
					if self.DATA[element][0] <= offset <= self.DATA[element][1]:
						tooltip.set_text("%s (from %s to %s)" % (element, self.intToHex(self.DATA[element][0]) if self.displayInHex else str(self.DATA[element][0]), self.intToHex(self.DATA[element][1]) if self.displayInHex else str(self.DATA[element][1])))
						break


		else:
			return False

		return True

	def on_key_press_event(self, widget, event):
		""" Handles Key Down events, puts the corresponding keyval into a list self.keysDown.
		Also checks for key combinations. """
		keyname = Gdk.keyval_name(event.keyval)
		# print keyname
		if keyname == 'Return' or keyname == 'KP_Enter':
			if not self.getCharFlag:
				self.stepButtonClicked()
			else:
				self.inBuffer = self.entry.get_text() + "\n"
				self.registers["AX"] = ord(self.inBuffer[0])
				self.inBuffer = self.inBuffer[1:]
				self.getCharFlag = False
			return

		if not keyname in self.keysDown: self.keysDown.append(keyname)

		if ('O' in self.keysDown or 'o' in self.keysDown) and ('Control_L' in self.keysDown or 'Control_R' in self.keysDown):
			self.keysDown = []
			self.openFile()

	def on_key_release_event(self, widget, event):
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

			self.codeString = f.read()

			f.close()

			self.startRunning()
		except IOError:
			self.outPut("There was a fatal issue opening " + self.fileName + ". Are you sure it's a file?")

	def startRunning(self):
		"""Starts the whole sha-bang.
		First pass for forward references, and setting up local vars, etc.
		Second loop to be done LATES."""

		self.ran = False

		self.clearGui()

		GObject.idle_add(lambda: self.codeBuffer.set_text(self.codeString))

		self.updateRegisters()

		self.lines = self.codeString.split("\n")

		self.lookupTable = {}
		self.localVars = {}
		self.stackData = []
		self.DATA = {}
		self.BSS = {}

		self.jumpLocation = -1

		self.lineCount = 0

		self.mode = "head"
		self.codeBounds = [1, 1]

		self.addressSpace = []

		for i in range(1024):
			self.addressSpace.append(str(0))

		errorCount = 0


		BSScount = 0

		# This for Loop is gonna go thru the lines, set up a nice lookUp table for jumps
		# and record program start and end. and set up some memory stuff.

		""" FIRST PASS """

		for line in self.lines:
			# Looping thru every line
			# we will go thru, at most, 4 modes
			# a "head" mode - where constants are defined
			# 	 eg _EXIT = 1 etc.
			# a "text" mode (".SECT .TEXT") where the code is located
			# 	 on the first loop thru we just keep track of where this is, and set up a jump table
			# a "data" mode (".SECT .DATA") where variables are defined
			# 	 str: .ASCIZ "%s f"
			# a "bss" mode (".SECT .BSS") where memory chunks are defined
			# 	 fdes: .SPACE 2
			l = line.strip()

			if "!" in line:
				l = line[:line.find("!")].strip()  # ignore comments

			self.lineCount += 1

			if self.mode == "head" and "=" in l:
				l = l.split('=')
				l[0] = l[0].strip()
				l[1] = l[1].strip()
				if l[0] in self.localVars.keys():
					self.outPut("Error on line " + str(self.lineCount) + ", cannot define \''" + l[0] + "\' more than once.")
					errorCount += 1
				else: self.localVars[l[0]] = l[1]
				continue

			if ".SECT" in l:

				# record where the .SECT .TEXT section starts, and ends
				if self.mode == ".SECT .TEXT":  # ends, we've gone one too far
					self.codeBounds[1] = self.lineCount - 1
				elif l == ".SECT .TEXT":  # starts, we're one too short
					self.codeBounds[0] = self.lineCount + 1

				self.mode = l
				continue

			if ":" in l:  # Spliting on a colon, for defining vars, or jump locations, etc.
				temp = l.split(":")[0]
				if self.mode == ".SECT .TEXT":
					# a : in .SECT .TEXT means a jump location
					# we can define multiple jump locations by digits
					# but only one by ascii per each ascii name

					if temp not in self.lookupTable.keys():
						self.lookupTable[temp] = self.lineCount
					else:
						if temp.isdigit():  # If we're defining multiple jump locations for one digit, keep a list
							if type(self.lookupTable[temp]) == self.LIST_TYPE:
								self.lookupTable[temp].append(self.lineCount)
							else:
								self.lookupTable[temp] = [self.lookupTable[temp], self.lineCount]
						else:
							self.outPut("Duplicate entry: \"" + temp + "\" on line " + str(self.lineCount) + " and line " + str(self.lookupTable[temp]))
							errorCount += 1
				elif self.mode == ".SECT .DATA":
					# info in .SECT .DATA follows the format
					# str: .ASCIZ "hello world"
					# where .ASCIZ means an ascii string with a zero at the end
					# and .ASCII means an ascii string

					if ".ASCIZ" in l or ".ASCII" in l:  # If we're dealing with a string
						if l.count("\"") < 2:  # each string to be defined should be in quotes, raise error if quotes are messed
							self.outPut("fatal error on line " + str(self.lineCount))
							errorCount += 1
							return None
						temp2 = l[l.find("\"") + 1:l.rfind("\"")]  # otherwise grab the stuff in quotes
						self.DATA[temp] = [BSScount, BSScount + len(temp2) + (".ASCIZ" in l) - 1]  # and set temp equal to a list of hex vals of each char
						self.addressSpace[BSScount:BSScount + len(temp2)] = temp2 + "0"*(".ASCIZ" in l)
						BSScount += len(temp2) + (".ASCIZ" in l)

				elif self.mode == ".SECT .BSS":
					# info in .SECT .BSS follows the format
					# fdes: .SPACE 2
					# Where essentially .BSS just defines memory space

					temp2 = l.split(".SPACE")[1]  # let's find the size of the mem chunk to def
					self.BSS[temp.strip()] = [BSScount, BSScount + int(temp2.strip()) - 1]  # and def it in bss as it's start and end pos
					BSScount += int(temp2.strip())

		# TODO: error check before second pass
		""" SECOND PASS """
		if errorCount == 0:
			self.lineNumber = self.codeBounds[0] - 1
			self.running = True
		else:
			self.outPut("Your code cannot be run, it contains %d errors" % errorCount)

	def updateStack(self, data=""):
		# self.outBuffer.apply_tag(self.textTagBold, self.outBuffer.get_start_iter(), self.outBuffer.get_end_iter())
		if data != "": self.stackData.append(str(data))
		if self.displayInHex:
			GObject.idle_add(lambda: self.stackBuffer.set_text("\n".join(["0"*(4 - len(hex(int(x)).split("x")[1])) + hex(int(x)).split("x")[1] for x in self.stackData])))
		else:
			GObject.idle_add(lambda: self.stackBuffer.set_text("\n".join(["0"*(4 - len(x)) + x for x in self.stackData])))

	def outPut(self, string, i=""):
		""" Outputs the arguments, in the fashion i: string"""
		if i == "":
			GObject.idle_add(lambda: (self.outText.get_buffer().insert(self.outText.get_buffer().get_end_iter(), ">> " + string),
					self.outText.scroll_to_iter(self.outText.get_buffer().get_end_iter(), 0.1, True, .5, .5)))
		else:
			GObject.idle_add(lambda: (self.outText.get_buffer().insert(self.outText.get_buffer().get_end_iter(), str(i) + ": " + string + "\n"),
					self.outText.scroll_to_iter(self.outText.get_buffer().get_end_iter(), 0.1, True, .5, .5),
					self.code.scroll_to_iter(self.code.get_buffer().get_iter_at_line(i + 1), 0.25, True, .5, .5),
					self.codeBuffer.apply_tag(self.textTagBold, self.codeBuffer.get_iter_at_line(i), self.codeBuffer.get_iter_at_line(i + 1))))

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
							self.regFlags.get_buffer().set_text("")))

	def getChar(self):
		if self.inBuffer == "":
			self.getCharFlag = True
			self.outPut("Waiting for input:")
		else:
			self.outPut(self.inBuffer + "\n")
			self.registers['AX'] = ord(self.inBuffer[0])
			self.inBuffer = self.inBuffer[1:]

	def colourMem(self):
		# TODO: Optimize this so that it doesn't highlight things way off in memory that aren't displayed?
		for index, location in enumerate(self.DATA.values() + self.BSS.values()):
			self.memoryBuffer.apply_tag(self.memoryColours[index % len(self.memoryColours)], self.memoryBuffer.get_iter_at_offset(location[0] * (self.displayInHex + 1)), self.memoryBuffer.get_iter_at_offset((location[1] + 1) * (self.displayInHex + 1)))

	def updateRegisters(self):
		""" Simply put, updates the register gui elements with the values of the registers. """

		flagStr = "  %-5s %-5s %-5s %-5s %-5s %-1s\n  %-6d%-6d%-6d%-6d%-6d%-1d" % (self.flags.keys()[0], self.flags.keys()[1], self.flags.keys()[2], self.flags.keys()[3], self.flags.keys()[4], self.flags.keys()[5], int(self.flags.values()[0]), int(self.flags.values()[1]), int(self.flags.values()[2]), int(self.flags.values()[3]), int(self.flags.values()[4]), int(self.flags.values()[5]))

		if self.displayInHex:
			GObject.idle_add(lambda: (self.regA.get_buffer().set_text("AX: %s\n AH: %s\n AL: %s" % ("0"*(4 - len(self.intToHex(self.registers['AX']))) + self.intToHex(self.registers['AX']), "0"*(2 - len(self.intToHex(self.eightBitRegister('AH')))) + self.intToHex(self.eightBitRegister("AH")), "0"*(2 - len(self.intToHex(self.eightBitRegister('AL')))) + self.intToHex(self.eightBitRegister('AL')))),
								self.regB.get_buffer().set_text("BX: %s\n BH: %s\n BL: %s" % ("0"*(4 - len(self.intToHex(self.registers['BX']))) + self.intToHex(self.registers['BX']), "0"*(2 - len(self.intToHex(self.eightBitRegister('BH')))) + self.intToHex(self.eightBitRegister("BH")), "0"*(2 - len(self.intToHex(self.eightBitRegister('BL')))) + self.intToHex(self.eightBitRegister("BL")))),
								self.regC.get_buffer().set_text("CX: %s\n CH: %s\n CL: %s" % ("0"*(4 - len(self.intToHex(self.registers['CX']))) + self.intToHex(self.registers['CX']), "0"*(2 - len(self.intToHex(self.eightBitRegister('CH')))) + self.intToHex(self.eightBitRegister("CH")), "0"*(2 - len(self.intToHex(self.eightBitRegister('CL')))) + self.intToHex(self.eightBitRegister("CL")))),
								self.regD.get_buffer().set_text("DX: %s\n DH: %s\n DL: %s" % ("0"*(4 - len(self.intToHex(self.registers['DX']))) + self.intToHex(self.registers['DX']), "0"*(2 - len(self.intToHex(self.eightBitRegister('DH')))) + self.intToHex(self.eightBitRegister("DH")), "0"*(2 - len(self.intToHex(self.eightBitRegister('DL')))) + self.intToHex(self.eightBitRegister("DL")))),
								self.regBP.get_buffer().set_text("BP: " + str(hex(self.registers['BP']).split("x")[1])),
								self.regSP.get_buffer().set_text("SP: " + str(hex(self.registers['SP']).split("x")[1])),
								self.regDI.get_buffer().set_text("DI: " + str(hex(self.registers['DI']).split("x")[1])),
								self.regSI.get_buffer().set_text("SI: " + str(hex(self.registers['SI']).split("x")[1])),
								self.regPC.get_buffer().set_text("PC: " + str(hex(self.registers['PC']).split("x")[1])),
								self.regFlags.get_buffer().set_text(flagStr),
								self.memoryBuffer.set_text("".join([self.intToHex(ord(x)) for x in self.addressSpace[:144]])),
								self.colourMem()
								))
		else:
			GObject.idle_add(lambda: (self.regA.get_buffer().set_text("AX: %d\n AH: %d\n AL: %d" % (self.registers['AX'], self.eightBitRegister("AH"), self.eightBitRegister('AL'))),
								self.regB.get_buffer().set_text("BX: %d\n BH: %d\n BL: %d" % (self.registers['BX'], self.eightBitRegister("BH"), self.eightBitRegister("BL"))),
								self.regC.get_buffer().set_text("CX: %d\n CH: %d\n CL: %d" % (self.registers['CX'], self.eightBitRegister("CH"), self.eightBitRegister("CL"))),
								self.regD.get_buffer().set_text("DX: %d\n DH: %d\n DL: %d" % (self.registers['DX'], self.eightBitRegister("DH"), self.eightBitRegister("DL"))),
								self.regBP.get_buffer().set_text("BP: " + str(self.registers['BP'])),
								self.regSP.get_buffer().set_text("SP: " + str(self.registers['SP'])),
								self.regDI.get_buffer().set_text("DI: " + str(self.registers['DI'])),
								self.regSI.get_buffer().set_text("SI: " + str(self.registers['SI'])),
								self.regPC.get_buffer().set_text("PC: " + str(self.registers['PC'])),
								self.regFlags.get_buffer().set_text(flagStr),
								self.memory.get_buffer().set_text("".join(self.addressSpace[:287])),
								self.colourMem()
								))

	def stepButtonClicked(self):
		""" Defines what happens if the step button is clicked.
		If the entry text field is empty, step like normal.
		If the entry text field has a command in it execute accordingly
		If the entry text field has characters in it, that aren't recognised as a command, clear the entry and do nothing.
		"""
		text = self.entry.get_text().lower().strip()
		if text == "":
			if self.ran:
				if not self.restartPrompt:
					self.outPut("Do you wish to restart? (y/n)")
					self.restartPrompt = True
			elif self.running:
				self.step()
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
					if n >= self.codeBounds[0] and n < self.codeBounds[1]:
						while self.running:
							if self.lineNumber == int(tempList[2]):
								self.step()
								break
							self.step()

						if self.lineNumber != int(tempList[2]) + 1:
							self.outPut("The program exited before it ever reached line " + tempList[2])
					else:
						self.outPut("That line number is not within the bounds of the program.")
				elif tempList[0] == "run" and tempList[1] == "all":
					while self.running:
						self.step()

			GObject.idle_add(lambda: self.entry.set_text(""))

	def step(self):
		""" The guts of the second pass. Where the magic happens! """
		if self.running:

			if self.lineNumber >= self.codeBounds[1]:
				self.stopRunning()
				return

			line = self.lines[self.lineNumber].replace("\t", "")  # clear out tabs

			if "!" in line:  # exclamations mean comments
				line = line[:line.find("!")].strip()  # ignore comments

			if ":" in line:  # colons mean labels, we dealt with those already.
				line = line[line.find(":") + 1:].strip()  # ignore jump points

			self.outPut(line, self.lineNumber)  # Now the line is ready to work with


			if line.count(",") > 1:  # any command can have at most 2 arguments.
				self.outPut("What's up with all the commas on line " + str(self.lineNumber) + "?")
				self.running = False
				self.ran = True
				return -1

			command = [x.strip() for x in line.replace(" ", ",").split(",")]

			for x in range(command.count("")):
				command.remove("")

			if command == None or command == []:
				self.lineNumber += 1
				return  # skip nothing lines, yo.

			if command[0] not in self.commandArgs.keys():
				print "Missing " + command[0] + " from self.commandArgs"
				self.lineNumber += 1
				return

			if len(command) - 1 != self.commandArgs[command[0]]:
				self.outPut("Invalid number of arguments on line " + str(self.lineNumber) + ". " + command[0] + " expects " + str(self.commandArgs[command[0]]) + " argument" + "s"*(self.commandArgs[command[0]] > 1) + " and " + str(len(command) - 1) + (" were " if len(command) - 1 > 1 else " was ") + "given.")
				print command[:]
				self.running = False
				self.ran = True
				return -1

			if command[0] in self.do.keys():
				self.do[command[0]](command, self.lineNumber)
				self.updateRegisters()
			else:
				1 + 1  # TODO: we do nothing right now, once all are implemented we'll throw errors for this sorta thing TODO

			if self.jumpLocation != -1:
				self.lineNumber = self.jumpLocation
				self.jumpLocation = -1
			else:
				self.lineNumber += 1

			if self.lineNumber >= self.codeBounds[1]:
				self.stopRunning()
				return

	def stopRunning(self, i=1):
		self.running = False
		self.ran = True
		if i == 1:
			self.outPut("\nCode executed succesfully.")
		else:
			self.outPut("\nCode execution terminated.")
		# TODO: EOF, anything important like that should go here.

	def hexSwitchClicked(self, button=None, data=None):
		self.displayInHex = not self.displayInHex
		self.updateRegisters()
		self.updateStack()

	def eightBitRegister(self, s):
		try:
			temp = ""

			if s == "AH":
				temp = self.intToHex(self.registers["AX"])[-4:-2]
			elif s == "AL":
				temp = self.intToHex(self.registers["AX"])[-2:]
			elif s == "BH":
				temp = self.intToHex(self.registers["BX"])[-4:-2]
			elif s == "BL":
				temp = self.intToHex(self.registers["BX"])[-2:]
			elif s == "CH":
				temp = self.intToHex(self.registers["CX"])[-4:-2]
			elif s == "CL":
				temp = self.intToHex(self.registers["CX"])[-2:]
			elif s == "DH":
				temp = self.intToHex(self.registers["DX"])[-4:-2]
			elif s == "DL":
				temp = self.intToHex(self.registers["DX"])[-2:]

			return int(temp, 16)

		except ValueError:
			return 0

	def intToHex(self, i):
		return str(hex(i).split("x")[1]).upper()


if __name__ == "__main__":

	GObject.threads_init()

	A = Assembler()
	print "Constructed"
	Gtk.main()
