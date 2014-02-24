#!/usr/bin/python2.7
from Assembler import Assembler
from gi.repository import Gtk, Gdk, GObject, Pango

if __name__ == "__main__":

	GObject.threads_init()

	A = Assembler()
	print "Constructed"
	Gtk.main()
