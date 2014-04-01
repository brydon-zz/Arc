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
    a = EntryDialog(title="Waiting for input", label="Waiting for input", buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK), modal=True)
    result = a.run()
    print result
