#!/usr/bin/python2.7
from gi.repository import Gtk, Gdk, GObject
import threading

""""Assembler Class for Intel 8088 Architecture"""
class Assembler:

	def __init__(self):
		
		""" Begin GUI """
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

		self.registers = {"AX":0,"BX":0,"CX":0,"DX":0,"SP":0,"BP":0,"SI":0,"DI":0,"PC":0}

		self.flags = {"Z":False,"S":False,"V":False,"C":False,"A":False,"P":False}
		#				

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
					"MOV":lambda x,i: self.mov(x,i),
					"JE":lambda x,i: self.je(x,i),
					"JG":lambda x,i: self.jg(x,i),
					"JL":lambda x,i: self.jl(x,i),
					"JLE":lambda x,i: self.jle(x,i),
					"JGE":lambda x,i: self.jge(x,i)
					}
		self.jumpLocation = -1

		self.lineCount = 0
		self.LIST_TYPE = type([1,1])
		self.mode = "head"
		self.codeBounds = [1,1]
				
		self.step = False
		self.stepping = True
		self.addressSpace = []
		self.keysDown = []
		
		for i in range(1024):
			self.addressSpace.append(0)

	def on_key_press_event(self,widget, event):
		keyname = Gdk.keyval_name(event.keyval)
		
		if not keyname in self.keysDown: self.keysDown.append(keyname)
		print self.keysDown
		if 'o' in self.keysDown and ('Control_L' in self.keysDown or 'Control_R' in self.keysDown):
			self.keysDown = []
			self.openFile()	
		
	def on_key_release_event(self,widget, event):
		keyname = Gdk.keyval_name(event.keyval)
		
		if keyname in self.keysDown: self.keysDown.remove(keyname)

	"""Opens up a file dialog to select a file then loads that file in to the assembler. """
	def openFile(self):
		self.fileChooser = Gtk.FileChooserDialog(title="Choose A File",parent=self.win,buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		response = self.fileChooser.run()

		if response == Gtk.ResponseType.OK:
			self.fileName = self.fileChooser.get_filename()

		self.fileChooser.destroy()

		if self.fileName == None:
			return None

		f = open(self.fileName,'r')
		
		self.codeString = f.read() 
		
		f.close()

		print "Just about to start threading"
		thread = threading.Thread(target=self.startRunning)
		thread.start()

	"""Starts the whole sha-bang. Runs the code and everything."""
	def startRunning(self):
		
		self.codeBuffer.set_text(self.codeString)
		self.lines = self.codeString.split("\n")
		
		BSScount = 0
		
		# This for Loop is gonna go thru the lines, set up a nice lookUp table for jumps 
		# and record program start and end. and set up some memory stuff.
		
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
		while i  < self.codeBounds[1]:
			# So second pass thru the code is where the money is
			# We have a boolean set up for single stepping or not.
			if self.step == True:
				if self.stepping: self.step = False
				line = self.lines[i].replace("\t","") # clear out tabs

				if "!" in line: # exclamations mean comments
					line = line[:line.find("!")].strip() #ignore comments

				if ":" in line: # colons mean labels, we dealt with those already.
					line = line[line.find(":")+1:].strip() # ignore jump points

				self.outPut(line,i) # Now the line is ready to work with


				if line.count(",") > 1: # any command can have at most 2 arguments.
					print "What's up with all the commas on line "+str(i)+"?"
					return -1

				command = [x.strip() for x in line.replace(" ",",").split(",")]

				if "" in command: command = command.remove("")

				if command == None:
					i += 1
					continue # skip nothing lines, yo.

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

		print "Loop is completed, all code is run."
		del temp, temp2

	def stackPush(self,data):
		if data != "": self.stackData.append(str(data))
		GObject.idle_add(self.update_stack)
	
	def update_stack(self):
		self.stackBuffer.set_text("\n".join(self.stackData))

	def stepFn(self):
		self.step = True
		
	def outPut(self,string,i):
		self.nextString = str(i)+": "+string+"\n"
		self.line = i
		GObject.idle_add(self.output_call)
	
	def output_call(self):
		self.outText.get_buffer().insert(self.outText.get_buffer().get_end_iter(),self.nextString)
		self.outText.scroll_to_iter(self.outText.get_buffer().get_end_iter(),0.1,True,.5,.5)
		self.code.scroll_to_iter(self.code.get_buffer().get_iter_at_line(self.line),0.25,True,.5,.5)
		
	def add(self,command,i):
		if command[1] == "SP" and command[2].isdigit():
			for j in range(int(command[2])/2):
				if len(self.stackData) > 0:
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
		print str(self.localVars.keys())+" "+str(self.DATA.keys())
		if command[1].isdigit():					# pushing a number to the stack
			self.stackPush(command[1])
		elif command[1] in self.DATA.keys():		# pushing a string from .SECT .DATA to the stack
			self.stackPush("foo")
		elif command[1] in self.localVars.keys():	# pushing a local int to the stack
			self.stackPush(self.localVars[command[1]])
		elif command[1] in self.BSS.keys():
			self.stackPush(self.BSS[command[1]][0])
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
		if command[1] in self.registers.keys():
			if command[2].isdigit():
				self.registers[command[1]] += int(command[2])
			elif command[2] in self.localVars.keys():
				self.registers[command[1]] += int(self.localVars[command[2]])
	
	def je(self,command,i):
		if 1+1:
			self.jmp(command,i)
	
	def jg(self,command,i):
		if 1+1:
			self.jmp(command,i)
			
	def jge(self,command,i):
		if 1+1:
			self.jmp(command,i)
	
	def jle(self,command,i):
		if 1+1:
			self.jmp(command,i)
	
	def jl(self,command,i):
		if 1+1:
			self.jmp(command,i)	

if __name__ == "__main__":

	GObject.threads_init()

	A=Assembler()
	print "Constructed"
	Gtk.main()
