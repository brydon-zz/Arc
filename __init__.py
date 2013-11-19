#!/usr/bin/python2.7
from gi.repository import Gtk, Gdk, GObject
import threading

""""Assembler Class for Intel 8088 Architecture"""
class Assembler:

	def __init__(self):
		styles = """
#As88Window {
	background:url('bg.jpg');
}

#As88Window #code, #As88Window #outText, #As88Window #stack {
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

			def onButtonClicked(self, button):
				A.stepFn()

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
		self.button = self.builder.get_object("button1")

		self.outBuffer = self.outText.get_buffer()
		self.codeBuffer = self.code.get_buffer()
		self.stackBuffer = self.stack.get_buffer()

		self.outText.set_name("outText")
		self.code.set_name("code")
		self.entry.set_name("entry")
		self.stack.set_name("stack")

		self.outText.set_wrap_mode(Gtk.WrapMode.WORD)
		self.code.set_wrap_mode(Gtk.WrapMode.WORD)

		self.outputText = " "
		self.outBuffer.set_text(self.outputText)

		self.win.show_all()

		self.step = False
		self.stepping = True
		self.addressSpace = []
		for i in range(1024):
			self.addressSpace.append(0)

	"""Opens up a file dialog to select a file then loads that file in to the assembler. """
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

		#this reads in the file
		while True:
			lineIn = self.f.readline()
			if lineIn == "": break
			self.codeString += lineIn
		self.f.close()

		print "Just about to start threading"
		thread = threading.Thread(target=self.startRunning)
		thread.start()

	"""Starts the whole sha-bang. Runs the code and everything."""
	def startRunning(self):
		self.codeBuffer.set_text(self.codeString)
		self.lines = self.codeString.split("\n")

		self.lookupTable = {}
		self.localVars = {}
		self.stackData = []
		self.DATA = {}
		self.BSS = {}

		self.registers = {"AX":0,"BX":0,"CX":0,"DX":0,"SP":0,"BP":0,"SI":0,"DI":0,"PC":0}

		self.flags = {"Z":False,"S":False,"V":False,"C":False,"A":False,"P":False}

		self.commandArgs = {"ADD":2,
							"PUSH":1,
							"JMP":1,
							"JE":1,
							"JG":1,
							"JL":1,
							"JLE":1,
							"JGE":1,
							"MOV":2,
							"SYS":0,
							"POP":1,
							"CMPB":2,
							"STOSB":0
							}
		self.do = {
					"ADD":lambda x,i: self.add(x,i),
					"PUSH":lambda x,i: self.push(x,i),
					"JMP":lambda x,i: self.jmp(x,i),
					"MOV":lambda x,i: self.mov(x,i)
					}
		self.jumpLocation = -1
		BSScount = 0

		self.lineCount = 0

		# This for Loop is gonna go thru the lines, set up a nice lookUp table for jumps 
		# and record program start and end. and set up some memory stuff.
		self.LIST_TYPE = type([1,1])
		self.mode = "head"
		self.codeBounds = [1,1]
		
		""" FIRST PASS """
		
		for line in self.lines:
			# Looping thru every line
			# we will go thru, at most, 4 modes
			# a "head" mode - where constants are defined
			#	 eg _EXIT = 1 etc.
			# a "text" mode (".SECT .TEXT") where the code is located
			#	 on the first loop thru we just keep track of where this is, and set up a jump table
			# a "data" mode (".SECT .DATA") where variables are defined
			#	 str: .ASCIZ "%s f"
			# a "bss" mode (".SECT .BSS") where memory chunks are defined
			#	 fdes: .SPACE 2
			l = line.strip()
			
			if "!" in line:
				l = line[:line.find("!")].strip() #ignore comments
			
			self.lineCount += 1

			if self.mode == "head" and "=" in l:
				l = l.split('=')
				l[0]=l[0].strip()
				l[1]=l[1].strip()
				if l[0] in self.localVars.keys():
					print "Error on line "+self.lineCount+", cannot define \''"+l[0]+"\' more than once."
				else: self.localVars[l[0]] = l[1]
				continue

			if ".SECT" in l:

				# record where the .SECT .TEXT section starts, and ends
				if self.mode == ".SECT .TEXT": # ends, we've gone one too far
					self.codeBounds[1] = self.lineCount-1
				elif l == ".SECT .TEXT":  # starts, we're one too short
					self.codeBounds[0] = self.lineCount+1

				self.mode = l
				print "|"+self.mode+"|"
				continue

			if ":" in l: 		# Spliting on a colon, for defining vars, or jump locations, etc.
				temp = l.split(":")[0]
				if self.mode == ".SECT .TEXT":
					# a : in .SECT .TEXT means a jump location
					# we can define multiple jump locations by digits
					# but only one by ascii per each ascii name
					
					if temp not in self.lookupTable.keys():
						self.lookupTable[temp] = self.lineCount
					else:
						if temp.isdigit(): # If we're defining multiple jump locations for one digit, keep a list 
							if type(self.lookupTable[temp]) == self.LIST_TYPE:
								self.lookupTable[temp].append(self.lineCount)
							else:
								self.lookupTable[temp] = [self.lookupTable[temp],self.lineCount]
						else:
							print "Duplicate entry: \"" + temp + "\" on line " + str(self.lineCount) + " and line " + str(self.lookupTable[temp])
				elif self.mode == ".SECT .DATA":
					# info in .SECT .DATA follows the format
					# str: .ASCIZ "hello world"
					# where .ASCIZ means an ascii string with a zero at the end
					# and .ASCII means an ascii string
					
					if ".ASCIZ" in l or ".ASCII" in l: # If we're dealing with a string
						if l.count("\"") < 2: # each string to be defined should be in quotes, raise error if quotes are messed
							print "fatal error on line "+str(self.lineCount)
							return None
						temp2 = l[l.find("\"")+1:l.rfind("\"")] # otherwise grab the stuff in quotes
						self.DATA[temp] = [hex(ord(x)).split("x")[1] for x in temp2] # and set temp equal to a list of hex vals of each char
						if ".ASCIZ" in l: self.DATA[temp].append("0") # if it's an asciz then append a 0 to the end.
						
				elif self.mode == ".SECT .BSS":
					# info in .SECT .BSS follows the format
					# fdes: .SPACE 2
					# Where essentially .BSS just defines memory space
					
					temp2 = l.split(".SPACE")[1] #let's find the size of the mem chunk to def
					self.BSS[temp.strip()]=[BSScount,BSScount+int(temp2.strip())-1] # and def it in bss as it's start and end pos
					BSScount += int(temp2.strip())
					
		#TODO: error check before second pass
		print "Passing twice"
		""" SECOND PASS """
		i = self.codeBounds[0]
		print self.stepping
		print self.step
		while i  <= self.codeBounds[1]:
			if self.step == True:
				if self.stepping: self.step = False
				line = self.lines[i].replace("\t","")

				if "!" in line:
					line = line[:line.find("!")].strip() #ignore comments

				if ":" in line:
					line = line[line.find(":")+1:].strip() # ignore jump points

				self.outPut(line,i)

				if line.count(",") > 1:
					print "What's up with all the commas on line "+str(i)+"?"
					return -1

				command = [x.strip() for x in line.replace(" ",",").split(",")]

				if "" in command: command = command.remove("")

				if command == None:
					i += 1
					continue

				if command[0] != '':
					if command[0] not in self.commandArgs.keys():
						print "Missing "+command[0]+" from self.commandArgs"
						i += 1
						continue

					if len(command)-1 != self.commandArgs[command[0]]:
						print "Invalid number of arguments on line "+str(i)+". "+command[0]+" expects " + str(self.commandArgs[command[0]]) + " arguments and "+str(len(command)-1)+" were given"
						print command[:]
						return -1

					if command[0] in self.do.keys():
						self.do[command[0]](command,i)
					else:
						1+1 # we do nothing right now, once all are implemented we'll throw errors for this sorta thing TODO

				if self.jumpLocation != -1:
					i = self.jumpLocation
					self.jumpLocation = -1
				else:
					i += 1

		print "Loop is completed"
		del temp, temp2

	def stackPush(self,data):
		if data != "": self.stackData.append(data)
		self.stackBuffer.set_text("\n".join(self.stackData))

	def stepFn(self):
		self.step = True
		
	def outPut(self,string,i):
		self.outText.get_buffer().insert(self.outText.get_buffer().get_end_iter(),string+"\n")
		#self.outText.scroll_to_iter(self.outText.get_buffer().get_end_iter(),0.1,True,.5,.5)
		#self.code.scroll_to_iter(self.code.get_buffer().get_iter_at_line(i),0.25,True,.5,.5)

	def add(self,command,i):
		if command[1] == "SP" and command[2].isdigit():
			for j in range(int(command[2])/2):
				self.stackData.pop()
				self.stackPush("")
		elif command[1].isdigit():
			print "Error on line "+str(i)+". Add cannot have a numerical first argument."
		elif command[1] in self.registers.keys():
			if command[2].isdigit():
				self.registers[command[1]] += int(command[2])
			elif command[2] in self.localVars.keys():
				self.registers[command[1]] += int(self.localVars[command[2]])

	def push(self,command,i):
		if command[1].isdigit():					# pushing a number to the stack
			self.stackPush(command[1])
		elif command[1] in self.DATA.keys():		# pushing a string from .SECT .DATA to the stack
			self.stackPush("foo")
		elif command[1] in self.localVars.keys():	# pushing a local int to the stack
			self.stackPush(self.localVars[command[1]])
		elif "(" in command[1] and ")" in command[1]:
			temp = command[1][command[1].find("(")+1:command[1].find(")")]
			if temp in self.BSS.keys():
				#TODO memory
				1+1
			else:
				print("Error on line "+str(i)+". I don't understand what ("+temp+") is")
		else:
			print(command)
			print("Unknown error on line "+str(i)+".")

	def jmp(self,command,i):
		if command[1] in self.lookupTable.keys():
			if type(self.lookupTable[command[1]]) == self.LIST_TYPE:
				1+1
			else:
				self.jumpLocation = self.lookupTable[command[1]]

	def mov(self,command,i):
		print "Moving "+command[0]+" to "+command[1]

if __name__ == "__main__":

	GObject.threads_init()

	A=Assembler()
	print "Constructed"
	Gtk.main()
