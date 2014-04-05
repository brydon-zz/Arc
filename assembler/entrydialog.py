"""
A simple lightweight EntryDialog class.
It creates a Dialog box that contains at least one Entry Box.
If you use the label="text" kwarg you can set a Label to appear in the Dialog.
Using the buttons kwarg you can set the buttons that appear in the Dialog.
On run() the EntryDialog will return the value of the entry box if the user
presses enter within the dialog box, or if they click on an OK button.

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

from gi.repository import Gtk


class EntryDialog(Gtk.Dialog):
    def __init__(self, *args, **kwargs):
        if 'default' in kwargs:
            default = kwargs['default']
            del kwargs['default']
        else:
            default = ''

        if 'label' in kwargs:
            labelText = kwargs['label']
            del kwargs['label']
        else:
            labelText = ""

        super(EntryDialog, self).__init__(*args, **kwargs)

        self.entry = Gtk.Entry(text=default)
        self.entry.connect("activate", lambda entry, dialog, resp:
                           dialog.response(resp), self, Gtk.ResponseType.OK)
        self.vbox.pack_end(self.entry, True, True, 0)

        if labelText != "":
            label = Gtk.Label(label=labelText)
            label.set_justify(Gtk.Justification.LEFT)
            self.vbox.pack_end(label, True, True, 0)

        self.vbox.show_all()

    def run(self):
        response = super(EntryDialog, self).run()
        if response == Gtk.ResponseType.OK:
            return self.entry.get_text()
        else:
            return None

if __name__ == "__main__":
    a = EntryDialog(title="Waiting for input", label="Waiting for input",
                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK), modal=True)
    result = a.run()
    print result
