#!/usr/bin/python
from gi.repository import Gtk, Gdk

"""
They have memory start
and memory end 
"""

""""Assembler Class for Intel 8088 Architecture"""
class Assembler:

	def __init__(self):
		styles = """
#As88Window {
	background:url('bg.jpg');
}

#As88Window #code, #As88Window #outText, #As88Window #entry, #As88Window #stack {
	background-color:#2F0B24;
	font-family:mono;
	color:#FFF;
}
"""

		lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut ornare rhoncus neque eget hendrerit. Donec accumsan elementum est id egestas. Nulla dolor sem, tincidunt ut suscipit et, volutpat ut arcu. Sed rutrum dapibus nunc at lobortis. Cras in lorem interdum, fringilla magna a, condimentum mi. Donec hendrerit justo mauris, sed placerat quam aliquet sed. Ut convallis tristique porttitor.
Aliquam euismod dui id placerat aliquam. Suspendisse purus ipsum, lacinia non vulputate non, faucibus non mi. Fusce eu metus lacinia, tempor arcu a, gravida tortor. Mauris lorem sem, ultrices vitae aliquam eu, tristique vel enim. Nam placerat mattis rutrum. Etiam vestibulum magna turpis, at rutrum erat imperdiet vitae. Nunc congue accumsan ante vel bibendum. Pellentesque quis tortor vel dolor auctor molestie. Vestibulum tincidunt elementum nibh vel imperdiet. Pellentesque et leo pulvinar, sodales erat ut, accumsan felis. In ultricies fermentum aliquet. Interdum et malesuada fames ac ante ipsum primis in faucibus. Sed tincidunt fringilla odio, vel iaculis libero rutrum sed. Pellentesque vel est consectetur, placerat sem accumsan, scelerisque purus. Aliquam sed velit varius, volutpat sapien id, sagittis tortor. Praesent eu velit erat.
Ut cursus feugiat leo, vel posuere mi lobortis sit amet. Maecenas vitae aliquam turpis. In libero tortor, vulputate nec arcu luctus, porttitor tincidunt lectus. In hac habitasse platea dictumst. Suspendisse lobortis, nisi non dictum adipiscing, sapien quam malesuada mauris, sit amet faucibus erat dolor ut velit. Donec fringilla purus malesuada leo sollicitudin iaculis. Pellentesque vestibulum congue nisi nec vestibulum. Mauris eleifend tellus sit amet faucibus vulputate. Morbi bibendum ligula tristique eleifend rhoncus. Integer egestas accumsan tempus. Suspendisse sem arcu, sodales at nisl eget, imperdiet sagittis nibh. Aliquam ornare nisi ut purus tempor, ac fermentum libero condimentum. Sed eget mauris in mi malesuada varius. Vivamus nisi tellus, molestie ac neque a, consectetur gravida libero. Phasellus ut cursus lorem. In eu leo ullamcorper, rhoncus quam eu, ultrices elit.
Donec pulvinar eros quis nisl congue accumsan. Sed vitae turpis scelerisque, porttitor nisl luctus, venenatis felis. Sed egestas sagittis tortor ut malesuada. Praesent aliquet augue hendrerit dolor euismod mattis. Nunc molestie iaculis dolor, sit amet ullamcorper mauris viverra vel. Vivamus in consequat risus. Etiam fermentum rutrum sapien eu rutrum. Cras quis sapien arcu. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Suspendisse egestas vitae nibh vitae sodales. Vivamus nisi magna, ultrices non dictum eget, imperdiet nec dolor"""

		"""Handlers for the actions in the interface."""
		class Handler:
			def onDeleteWindow(self, *args):
				Gtk.main_quit(*args)

			def onEntryActivate(self, button):
				print "lol k"

			def onOpen(self, button):
				A.openFile()

		self.builder = Gtk.Builder()
		self.builder.add_from_file("As88_Mockup.glade")
		self.builder.connect_signals(Handler())

		self.win = self.builder.get_object("window1")
		self.win.set_name('As88Window')

		self.style_provider = Gtk.CssProvider()

		self.style_provider.load_from_data(styles)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self.outText = self.builder.get_object("outText")
		self.code = self.builder.get_object("code")
		self.entry = self.builder.get_object("entry")
		self.stack = self.builder.get_object("stack")

		self.outBuffer = self.outText.get_buffer()
		self.codeBuffer = self.code.get_buffer()

		self.outText.set_name("outText")
		self.code.set_name("code")
		self.entry.set_name("entry")
		self.stack.set_name("stack")

		self.outText.set_wrap_mode(Gtk.WrapMode.WORD)
		self.code.set_wrap_mode(Gtk.WrapMode.WORD)

		self.outBuffer.set_text(lorem)
		self.codeBuffer.set_text(lorem)

		self.win.show_all()

	"""Opens up a file dialog to select a file then loads that file in to the assembler."""
	def openFile(self):
		self.fileChooser = Gtk.FileChooserDialog(title="Choose A File",parent=self.win,buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		self.response = self.fileChooser.run()

		if self.response == Gtk.ResponseType.OK:
			self.fileName = self.fileChooser.get_filename()

		self.fileChooser.destroy()

		if self.fileName == None:
			return None

		self.f = open(self.fileName,'r')
		self.codeString = ""

		#this loop strips comments
		while True:
			lineIn = self.f.readline()
			if lineIn == "": break
			self.codeString += lineIn[:lineIn.find("!")]+"\n"
		self.f.close()

		self.startRunning()

	"""Starts the whole sha-bang. Runs the code and everything."""
	def startRunning(self):
		self.codeBuffer.set_text(self.codeString)
		self.lines = self.codeString.split("\n")

		self.lookupTable = {}
		self.localVars = {}
		self.data = {}
		self.BSS = {}

		self.lineCount = 0

		# This for Loop is gonna go thru the lines, set up a nice lookUp table for jumps 
		# and record program start and end. and set up some memory stuff.
		self.listType = type([1,1])
		self.mode = "head"
		self.codeBounds = [1,1]
		for line in self.lines:
			l = line.strip()
			self.lineCount += 1

			if self.mode == "head" and "=" in l:
				l = line.split('=')
				l[0]=l[0].strip()
				l[1]=l[1].strip()
				if l[0] in self.localVars.keys():
					print "Error on line "+self.lineCount+", cannot define ''"+l[0]+"'' more than once."
				else: self.localVars[l[0]] = l[1]
				continue

			if ".SECT" in l:

				if self.mode == ".SECT .TEXT":
					self.codeBounds[1] = self.lineCount-1
				elif l == ".SECT .TEXT":
					self.codeBounds[0] = self.lineCount+1

				self.mode = l
				print "|"+self.mode+"|"
				continue

			if ":" in l: 		#Defining tings
				temp = l.split(":")[0]
				if self.mode == ".SECT .TEXT":
					if temp not in self.lookupTable.keys():
						self.lookupTable[temp] = self.lineCount
					else:
						if temp.isdigit():
							if type(self.lookupTable[temp]) == self.listType:
								self.lookupTable[temp].append(self.lineCount)
							else:
								self.lookupTable[temp] = [self.lookupTable[temp],self.lineCount]

						else:
							print "Duplicate entry: \"" + temp + "\" on line " + str(self.lineCount) + " and line " + str(self.lookupTable[temp])
				elif self.mode == ".SECT .DATA":
					# DO STUFF
					1+1
				elif self.mode == ".SECT .BSS":
					# DO STUFF
					1+1
		print self.lookupTable
		print self.localVars
		del temp


A=Assembler()
Gtk.main()
