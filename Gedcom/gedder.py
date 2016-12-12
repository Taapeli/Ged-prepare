#
# Gedcom cleaner application window
# 12.12.2016 / Juha Mäkeläinen
#

# Show menu in application window, not on the top of desktop
import os 
os.environ['UBUNTU_MENUPROXY']='0'

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)
        
    def appedShow(self, text):
        # Printing text to scrollable text view
        outbox = builder.get_object("tulosruutu")
        outbox.get_buffer().insert_at_cursor(text)
        outbox.get_buffer().insert_at_cursor("\n")

    def opSelection_changed(self, combo):
        op = combo.get_property('active-id')
        butt = builder.get_object("runButton")
        butt.set_sensitive(op != "-")
        txt = "Valittu {}.py".format(op)
        builder.get_object("checkbutton2").set_sensitive(op == 'places')
        self.appedShow(txt)
        
    def onRunClicked(self, button):
        self.appedShow("Painettu: " + button.get_label())
        rev = builder.get_object("revertButton")
        rev.set_sensitive(True)
        
    def onRevertClicked(self, button):
        self.appedShow("Painettu: " + button.get_label())
        rev = builder.get_object("revertButton")
        rev.set_sensitive(False)
    
    def on_menuFileOpen_activate(self, button):
        self.appedShow("Piti valita avattava tiedosto")


builder = Gtk.Builder()
builder.add_from_file("view/Gedder.glade")
builder.connect_signals(Handler())
#print (dir(builder.get_object('runButton')))
#print ("Button label " + builder.get_object('runButton').get_label())

window = builder.get_object("applicationwindow")
window.show_all()
Gtk.main()