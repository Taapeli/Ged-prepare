#!/usr/bin/env python3
#
# Gedcom cleaner application window
# 12.12.2016 / Juha Mäkeläinen
#

import os 
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from argparse import Namespace

import gedcom_transform

# Show menu in application window, not on the top of Ubuntu desktop
os.environ['UBUNTU_MENUPROXY']='0'
args = Namespace(nolog=True, output_gedcom='out.txt', encoding='UTF-8', dryrun=False)

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)
        
    def appedShow(self, text):
        # Printing text to scrollable text view
        outbox = builder.get_object("tulosruutu")
        outbox.get_buffer().insert_at_cursor(text)
        outbox.get_buffer().insert_at_cursor("\n")

    def opSelection_changed(self, combo):
        global transformer
        op = combo.get_property('active-id')
        butt = builder.get_object("runButton")
        butt.set_sensitive(op != "-")
        txt = "Toiminto '{}'".format(op)
        builder.get_object("checkbutton2").set_sensitive(op == 'places')
        self.appedShow(txt)
        # Define transformer program and the argumets used
        transformer = gedcom_transform.find_transform(txt)
        if not transformer: 
            self.appedShow("Transform not found; use -l to list the available transforms")
            return 
        transformer.add_args(parser)
        
    def onRunClicked(self, button):
        global transformer
        self.appedShow("Painettu: " + button.get_label())
        
        # Käynnistetään pyydetty toiminto
        gedcom_transform.process_gedcom(args, transformer)

        rev = builder.get_object("revertButton")
        rev.set_sensitive(True)
        
    def onRevertClicked(self, button):
        self.appedShow("Painettu: " + button.get_label())
        rev = builder.get_object("revertButton")
        rev.set_sensitive(False)
    
    def on_file_open_activate(self, menuitem, data=None):
        self.dialog = Gtk.FileChooserDialog("Open...",
            window,
            Gtk.FileChooserAction.OPEN, #Gtk.FILE_CHOOSER_ACTION_OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
             #Gtk.STOCK_CANCEL, Gtk.RESPONSE_CANCEL,  Gtk.STOCK_OPEN, Gtk.RESPONSE_OK))
            )
        self.response = self.dialog.run()
        if self.response == Gtk.ResponseType.OK:
            self.appedShow("Syöte: " + self.dialog.get_filename())
            self.dialog.destroy()
        else:
            self.appedShow("Outo palaute {}".format(self.response))

def runner():
    global parser
    print("\nTaapeli GEDCOM transform program A (version 0.1)\n")
    parser = gedcom_transform.argparse.ArgumentParser()
    parser.add_argument('transform', help="Name of the transform (Python module)")
    parser.add_argument('input_gedcom', help="Name of the input GEDCOM file")
    #parser.add_argument('output_gedcom', help="Name of the output GEDCOM file; this file will be created/overwritten" )
    parser.add_argument('--display-changes', action='store_true',
                        help='Display changed rows')
    parser.add_argument('--dryrun', action='store_true',
                        help='Do not produce an output file')
    #parser.add_argument('--display-nonchanges', action='store_true',
    #                    help='Display unchanged places')
    parser.add_argument('--encoding', type=str, default="utf-8",
                        help="e.g, UTF-8, ISO8859-1")
    parser.add_argument('-l', '--list', action='store_true', help="List transforms")

    if len(sys.argv) > 1 and sys.argv[1] in ("-l","--list"):
        print("List of transforms:")
        for modname,transformer,docline,version in gedcom_transform.get_transforms():
            print("  {:20.20} {:10.10} {}".format(modname,version,docline))
        return

    if len(sys.argv) > 1 and sys.argv[1][0] == '-' and sys.argv[1] not in ("-h","--help"):
        print("First argument must be the name of the transform")
        return

    if len(sys.argv) > 1 and sys.argv[1][0] != '-':
        transformer = gedcom_transform.find_transform(sys.argv[1])
        if not transformer: 
            print("Transform not found; use -l to list the available transforms")
            return
        transformer.add_args(parser)

    args = parser.parse_args()
    gedcom_transform.process_gedcom(args,transformer)



builder = Gtk.Builder()
builder.add_from_file("view/Gedder.glade")
builder.connect_signals(Handler())
#print (dir(builder.get_object('runButton')))
#print ("Button label " + builder.get_object('runButton').get_label())

window = builder.get_object("applicationwindow")
window.show_all()
Gtk.main()