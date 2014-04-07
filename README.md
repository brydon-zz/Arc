#Intel 8088 Simulator

This program is an interactive Intel 8088 CPU and assembly code IDE.
It provides an environment for users to write Intel 8088 Assembly Code.
Complete with syntax highlighting and a helpful index of Intel 8088 
instructions and descriptions of their operation. It is ideal for users
who wish to learn Intel 8088 assembly code or for users who wish to 
obtain a deeper understanding of assembly code in general.

The user can simulate their code by stepping through each instruction line
by line or by running all the code at once.  The user can set multiple
breakpoints to aid in debugging and interpreting the code.  The program
has a graphical representation of the registers and memory space of the
Intel 8088 to assist the user in understanding the assembly code their
writing.

##Features

- Development Environment with Syntax Highlighting
- Simulates the execution of 8088 Assembly Code 
- Provides Graphical Representation of Registers, Memory, and Stack
- Helpful Documentation of the Instruction Set

##Simulator Usage

The simulator has various functions.
- New (also accesible by Ctrl+N)
- Open (also accesible by Ctrl+O)
- Save (also accesible by Ctrl+S)
- Save As (also accesible by Ctrl+Shift+N)
- Step Once (also accesible by Enter)
- Run All (also accesible by Ctrl+Enter or Shift+Enter)
- Stop Running (also accesible by Ctrl+X)
- Exit (also accesible by Ctrl+Q)

Where New creates a new file, trashing any unsaved changes in the current.

Open opens a new file as selected via a dialog, trashing any unsaved changes in the current.

Save saves the current file, or asks via a dialog to save if the current file hasn't already been saved.

Save As prompts via a dialog where to save a copy of the file.

Step Once runs one line of code, (re)starting the simulation if necessary.

Run All runs all lines of code, (re)starting the simulation if necessary.

Exit closes the program, prompting regarding active simulations or unsaved changes if necessary.

In the Text Field users can enter in various assembly language instructions,
or load in instructions via file. The code follows the basic schema:
  PREAMBLE
  .SECT .TEXT
    code
  .SECT .DATA
    data
  .SECT .BSS
    buffers

Any text folliwng a exclamation mark (!) on a line is a comment and so ignored

Local variables can be defined in the 'preamble' of your assembly code.
To do this enter very simple assignments at the top of the document.

Things like

    _EXIT = 1

etc.

Blank Buffers in memory can be defined in the .SECT .BSS section at the bottom of your code.

Like so:

    .SECT .BSS
      num: .SPACE 3

Defines a 3 space buffer called "num".

Values can be loaded into memory with the .SECT .DATA section like so:

    .SECT .DATA
      helloWorld:   .ASCIIZ "Hello World"
      helloNoZerp:  .ASCII "Hello World"

Where .ASCIIZ stores a zero terminated string in memory.
And .ASCII stores the string in memory.  

The code section is everything between a .SECT .TEXT
line and either a .SECT .DATA, .SECT .BSS, or end of the file.
In the code section any basic 

Any numerals directly placed in are interpreted as hex if they are ended
by a "h". Otherwise they are interpreted as int.

Like so:

    PUSH 25   ! This pushes the integer 25
    PUSH 25h  ! This pushes the hex value 0x25 = 37

##Simulator Interface Basics
The text field on the left hand side is for the entering/loading of assembly code.  
The line of numbers to its left represents the line numbers of each associated line.  
The grey field on the bottom left is for output by the program upon running.  
The bar of buttons below performs basic actions as described above.  
The coloured bar that says either "hide" or "show" can shrink or expand the interface.  
If the interface is expanded then on the left there are two tabs: machine info and help.  
Machine Info tab displays various information about the current status of the simulation including: register values, flag status, memory status, and stack.  
The hex switch toggles viewing this information in hexadecimal or an ascii/decimal interpretation.  
The Help tab contains info about all the instructions in the instruction set including the format of their expected arguments, flags affected, description, and english word title.  

## About

This program is written in Python and released under the GPL 2.0 License.
For more information please view the LICENSE file or visit:
http://www.gnu.org/licenses/old-licenses/gpl-2.0.html

Copyright (c) 2014 Brydon Eastman
