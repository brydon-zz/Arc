#!/usr/bin/python2.7
"""
Intel 8088 Simulator

This program is an interactive Intel 8088 CPU and assembly code IDE. 
It provides an environment for users to write Intel 8088 Assembly Code. 
Complete with syntax highlighting and a helpful index of Intel 8088 
instructions and descriptions of their operation. It is ideal for users 
who wish to learn Intel 8088 assembly code or for users who wish to 
obtain a deeper understanding of assembly code in general.

The user can simulate their code by stepping thru each instruction 
line by line or by running all the code at once. The user can set 
multiple breakpoints to aid in debugging and interpreting the code. 
The program has a graphical representation of the registers and memory 
space of the Intel 8088 to assist the user in understanding the assembly 
code their writing.

Features

    Development Environment with Syntax Highlighting
    Simulates the execution of 8088 Assembly Code
    Provides Graphical Representation of Registers, Memory, and Stack
    Helpful Documentation of the Instruction Set

Copyright (c) 2014 Brydon Eastman

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

from simulatorgui import Simulator
from gi.repository import Gtk

if __name__ == "__main__":

	A = Simulator()
	print "Constructed"
	Gtk.main()

