#!/usr/bin/env python3
#
# Gedcom cleaner application window
# 12.12.2016 / Juha Mäkeläinen
#

import os 
import sys
import gi
gi.require_version('Gtk', '3.0')
import importlib
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

    def on_opNotebook_switch_page (self,  notebook, page, page_num, data=None):
        ''' Valittu välilehti määrää toiminnon 
        '''
        global transformer
        opers = ("names", "places", "marriages", "hiskisources", "kasteet", None)
        op_selected = None
        
        self.tab = notebook.get_nth_page(page_num)
        self.label = notebook.get_tab_label(self.tab).get_label()
        if page_num < len(opers):
            op_selected = opers[page_num]
#             if op_selected:
#                 self.message_id = st.push(st_id, "{} -toiminto {!r}-moduulilla".format(self.label, op_selected))
    
        builder.get_object("checkbutton2").set_sensitive(op_selected == 'places')

        # Define transformer program and the argumets used
        if op_selected:
            transformer, vers, doc = get_transform(op_selected)
            if transformer: 
                self.message_id = st.push(st_id, doc + " " + vers)
#                 butt = builder.get_object("runButton")
#                 butt.set_sensitive(True)
            else:
                self.appedShow("Transform not found; use -l to list the available transforms")
                self.message_id = st.pop(self.message_id)
        else:
            self.message_id = st.pop(self.message_id)
        
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


def get_transform(name):
    ''' Return the transform module and it's description from "transforms" package 
        if name == "marriages", a tranformer module "transforms.marriages" is imported
    '''
    filename = "transforms/" + name + ".py"
    if os.path.exists(filename):
        transformer = importlib.import_module("transforms."+name)
        doc = transformer.__doc__
        if doc:
            docline = doc.strip().splitlines()[0]
        else:
            docline = ""
        version = getattr(transformer, "version", "")
        return (transformer, version, docline)
    return None


builder = Gtk.Builder()
builder.add_from_file("view/Gedder.glade")
builder.connect_signals(Handler())
st = builder.get_object('statusbar1')
# print (dir(st))
st_id = st.get_context_id("gedder")
# print ("Statuspaikka " + str(st_id))

window = builder.get_object("applicationwindow")
# statusbar = Gtk.Statusbar()
# context = statusbar.get_context_id("example")
window.show_all()
Gtk.main()