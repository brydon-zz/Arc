#!/usr/bin/python2.7
from gi.repository import Gtk, Gdk, GObject
import threading, os, as88

# TODO: issues with restarting, issues with running certain things before we're ready for second pass, etc.
# TODO: hex the reg output
# TODO: AL and AH, etc.
# TODO: Implement the WHOLE reg set
# TODO: ASSEMBLE?

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

			def onEntryActivate(self, button):
				print "lol k"

			def onOpen(self, button):
				A.openFile()

			def onButtonClicked(self, button):
				A.buttonClicked()

		self.builder = Gtk.Builder()
		self.builder.add_from_file("As88_Mockup.glade")
		self.builder.connect_signals(Handler())

		self.win = self.builder.get_object("window1")
		self.win.set_name('As88Window')

		self.style_provider = Gtk.CssProvider()

		self.style_provider.load_from_data(styles)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

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

		self.outBuffer = self.outText.get_buffer()
		self.codeBuffer = self.code.get_buffer()
		self.stackBuffer = self.stack.get_buffer()

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

		self.outText.set_wrap_mode(Gtk.WrapMode.WORD)
		self.code.set_wrap_mode(Gtk.WrapMode.WORD)

		self.outputText = " "
		self.outBuffer.set_text(self.outputText)

		self.win.connect('key_press_event', self.on_key_press_event)
		self.win.connect('key_release_event', self.on_key_release_event)
		self.win.set_icon_from_file("icon.jpeg")

		self.win.show_all()


		""" End GUI """

		self.fileName = None

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

		self.LIST_TYPE = type([1, 1])
		self.stepping = True  # Change if we want to not single-step thru code

		self.jumpLocation = -1

		self.lineCount = 0

		self.mode = "head"
		self.codeBounds = [1, 1]

		self.step = False
		self.runUntil = -1

		self.addressSpace = []

		for i in range(1024):
			self.addressSpace.append(0)

		self.keysDown = []

	def on_key_press_event(self, widget, event):
		""" Handles Key Down events, puts the corresponding keyval into a list self.keysDown.
		Also checks for key combinations. """
		keyname = Gdk.keyval_name(event.keyval)
		# print keyname
		if keyname == 'Return' or keyname == 'KP_Enter':
			self.stepFn()
			return

		if not keyname in self.keysDown: self.keysDown.append(keyname)

		if 'o' in self.keysDown and ('Control_L' in self.keysDown or 'Control_R' in self.keysDown):
			self.keysDown = []
			self.openFile()

	def on_key_release_event(self, widget, event):
		""" Handes Key Up events, removes the corresponding keyval from the list self.keysDown. """
		keyname = Gdk.keyval_name(event.keyval)

		if keyname in self.keysDown: self.keysDown.remove(keyname)

	def openFile(self):
		"""Opens up a file dialog to select a file then reads that file in to the assembler. """

		self.fileName = None

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
			print "Just about to start threading"
			thread = threading.Thread(target=self.startRunning)
			thread.start()
		except IOError:
			print "There was a fatal issue opening " + self.fileName + ". Are you sure it's a file?"

	def startRunning(self):
		"""Starts the whole sha-bang. Runs the code and everything. Goes thru 2 steps.
		First pass for forward references, and setting up local vars, etc.
		Second pass to run the code.  Intended to be run in separate thread, steps thru the loop
		once at a time. Dependent upon receiving button clicks, or enter presses."""

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

		self.step = False
		self.runUntil = -1
		self.stepping = True

		self.addressSpace = []

		for i in range(1024):
			self.addressSpace.append(0)


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
					print "Error on line " + str(self.lineCount) + ", cannot define \''" + l[0] + "\' more than once."
				else: self.localVars[l[0]] = l[1]
				continue

			if ".SECT" in l:

				# record where the .SECT .TEXT section starts, and ends
				if self.mode == ".SECT .TEXT":  # ends, we've gone one too far
					self.codeBounds[1] = self.lineCount - 1
				elif l == ".SECT .TEXT":  # starts, we're one too short
					self.codeBounds[0] = self.lineCount + 1

				self.mode = l
				print "|" + self.mode + "|"
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
							print "Duplicate entry: \"" + temp + "\" on line " + str(self.lineCount) + " and line " + str(self.lookupTable[temp])
				elif self.mode == ".SECT .DATA":
					# info in .SECT .DATA follows the format
					# str: .ASCIZ "hello world"
					# where .ASCIZ means an ascii string with a zero at the end
					# and .ASCII means an ascii string

					if ".ASCIZ" in l or ".ASCII" in l:  # If we're dealing with a string
						if l.count("\"") < 2:  # each string to be defined should be in quotes, raise error if quotes are messed
							print "fatal error on line " + str(self.lineCount)
							return None
						temp2 = l[l.find("\"") + 1:l.rfind("\"")]  # otherwise grab the stuff in quotes
						self.DATA[temp] = [hex(ord(x)).split("x")[1] for x in temp2]  # and set temp equal to a list of hex vals of each char
						if ".ASCIZ" in l: self.DATA[temp].append("0")  # if it's an asciz then append a 0 to the end.

				elif self.mode == ".SECT .BSS":
					# info in .SECT .BSS follows the format
					# fdes: .SPACE 2
					# Where essentially .BSS just defines memory space

					temp2 = l.split(".SPACE")[1]  # let's find the size of the mem chunk to def
					self.BSS[temp.strip()] = [BSScount, BSScount + int(temp2.strip()) - 1]  # and def it in bss as it's start and end pos
					BSScount += int(temp2.strip())

		# TODO: error check before second pass
		print "Passing twice"
		""" SECOND PASS """
		i = self.codeBounds[0]

		while i < self.codeBounds[1]:
			# So second pass thru the code is where the money is
			# We have a boolean set up for single stepping or not.
			if self.runUntil != -1:
				if i == self.runUntil:
					self.step = True
					self.stepping = True
					self.runUntil = -1
				else:
					self.step = True
					self.stepping = False

			if self.step == True:
				if self.stepping: self.step = False
				line = self.lines[i].replace("\t", "")  # clear out tabs

				if "!" in line:  # exclamations mean comments
					line = line[:line.find("!")].strip()  # ignore comments

				if ":" in line:  # colons mean labels, we dealt with those already.
					line = line[line.find(":") + 1:].strip()  # ignore jump points

				self.outPut(line, i)  # Now the line is ready to work with


				if line.count(",") > 1:  # any command can have at most 2 arguments.
					print "What's up with all the commas on line " + str(i) + "?"
					return -1

				command = [x.strip() for x in line.replace(" ", ",").split(",")]

				if "" in command: command = command.remove("")

				if command == None:
					i += 1
					continue  # skip nothing lines, yo.

				if command[0] != '':
					if command[0] not in self.commandArgs.keys():
						print "Missing " + command[0] + " from self.commandArgs"
						i += 1
						continue

					if len(command) - 1 != self.commandArgs[command[0]]:
						print "Invalid number of arguments on line " + str(i) + ". " + command[0] + " expects " + str(self.commandArgs[command[0]]) + " arguments and " + str(len(command) - 1) + " were given"
						print command[:]
						return -1

					if command[0] in self.do.keys():
						self.do[command[0]](command, i)
						self.updateRegisters()
					else:
						1 + 1  # we do nothing right now, once all are implemented we'll throw errors for this sorta thing TODO

				if self.jumpLocation != -1:
					i = self.jumpLocation
					self.jumpLocation = -1
				else:
					i += 1

		print "Loop is completed, all code is run."
		if self.runUntil != -1:
			print "Strange, the code never reached line " + str(self.runUntil) + " after your request, check your jumps!"

	def stackPush(self, data):
		if data != "": self.stackData.append(str(data))
		GObject.idle_add(lambda: self.stackBuffer.set_text("\n".join(self.stackData)))

	def stepFn(self):
		self.step = True

	def outPut(self, string, i):
		GObject.idle_add(lambda: (self.outText.get_buffer().insert(self.outText.get_buffer().get_end_iter(), str(i) + ": " + string + "\n"),
					self.outText.scroll_to_iter(self.outText.get_buffer().get_end_iter(), 0.1, True, .5, .5),
					self.code.scroll_to_iter(self.code.get_buffer().get_iter_at_line(i + 1), 0.25, True, .5, .5)))

	def clearGui(self):
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

	def updateRegisters(self):
		flagStr = "  %-5s %-5s %-5s %-5s %-5s %-1s\n  %-6d%-6d%-6d%-6d%-6d%-1d" % (self.flags.keys()[0], self.flags.keys()[1], self.flags.keys()[2], self.flags.keys()[3], self.flags.keys()[4], self.flags.keys()[5], int(self.flags.values()[0]), int(self.flags.values()[1]), int(self.flags.values()[2]), int(self.flags.values()[3]), int(self.flags.values()[4]), int(self.flags.values()[5]))

		GObject.idle_add(lambda: (self.regA.get_buffer().set_text("AX: " + str(self.registers['AX'])),
								self.regB.get_buffer().set_text("BX: " + str(self.registers['BX'])),
								self.regC.get_buffer().set_text("CX: " + str(self.registers['CX'])),
								self.regD.get_buffer().set_text("DX: " + str(self.registers['DX'])),
								self.regBP.get_buffer().set_text("BP: " + str(self.registers['BP'])),
								self.regSP.get_buffer().set_text("SP: " + str(self.registers['SP'])),
								self.regDI.get_buffer().set_text("DI: " + str(self.registers['DI'])),
								self.regSI.get_buffer().set_text("SI: " + str(self.registers['SI'])),
								self.regPC.get_buffer().set_text("PC: " + str(self.registers['PC'])),
								self.regFlags.get_buffer().set_text(flagStr)
								# self.memory.get_buffer().set_text(str(self.addressSpace))
								))

	def buttonClicked(self):
		text = self.entry.get_text()
		if text == "":
			self.stepFn()
		else:
			tempList = text.lower().strip().split()
			if tempList[0] == "run" and tempList[1] == "until" and tempList[2].isdigit():
				n = int(tempList[2])
				if n >= self.codeBounds[0] and n < self.codeBounds[1]:
					self.runUntil = int(tempList[2])
				else:
					print "That line number is not within the bounds of the program."
			elif tempList[0] == "run" and tempList[1] == "all":
				self.stepping = False
				self.step = True

			GObject.idle_add(lambda: self.entry.set_text(""))
			del tempList, n


if __name__ == "__main__":

	GObject.threads_init()

	A = Assembler()
	print "Constructed"
	Gtk.main()
