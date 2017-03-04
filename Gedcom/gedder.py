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
from gi.repository import Gtk, Pango, Gdk

from argparse import Namespace
import gedcom_transform

# Show menu in application window, not on the top of Ubuntu desktop
os.environ['UBUNTU_MENUPROXY']='0'
args = Namespace(nolog=True, output_gedcom='out.txt', encoding='UTF-8', dryrun=False)

class Handler:

    def __init__(self):
        global transformer
        global input_gedcom
        self.builder = Gtk.Builder()
        self.builder.add_from_file("view/Gedder.glade")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("applicationwindow")
        self.aboutdialog = self.builder.get_object("displaystate")
        self.window.show()
        
        self.st = self.builder.get_object('statusbar1')
        self.st_id = self.st.get_context_id("gedder")
        self.message_id = None
        input_gedcom = None
        transformer = None

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)
        
    def appedShow(self, text):
        # Printing text to scrollable text view
        self.st.push(self.st_id, text)
#         outbox = self.builder.get_object("tulosruutu")
#         outbox.get_buffer().insert_at_cursor(text)
#         outbox.get_buffer().insert_at_cursor("\n")

    def on_opNotebook_switch_page (self, notebook, page, page_num, data=None):
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
    
        self.builder.get_object("checkbutton2").set_sensitive(op_selected == 'places')

        # Define transformer program and the argumets used
        if op_selected:
            transformer, vers, doc = get_transform(op_selected)
            if transformer: 
                self.message_id = self.st.push(self.st_id, doc + " " + vers)
                self.activate_run_button()
            else:
                self.appedShow("Transform not found; use -l to list the available transforms")
        elif self.message_id:
            self.message_id = self.st.pop(self.message_id)
        
    def on_runButton_clicked(self, button):
        global transformer
        self.appedShow("Painettu: " + button.get_label())
        
        # Käynnistetään pyydetty toiminto
        gedcom_transform.process_gedcom(args, transformer)

        rev = self.builder.get_object("revertButton")
        rev.set_sensitive(True)
        
    def on_revertButton_clicked(self, button):
        self.appedShow("Painettu: " + button.get_label())
        rev = self.builder.get_object("revertButton")
        rev.set_sensitive(False)

    def on_showButton_clicked(self, button):
        ''' Näytetään luettu lokitiedosto uudessa ikkunassa '''
        self.builder2 = Gtk.Builder()
        self.builder2.add_from_file("view/displaystate.glade")
        self.builder2.connect_signals(self)
        msg = self.builder2.get_object("msg")
        self.disp_window = self.builder2.get_object("displaystate")
        self.disp_window.set_transient_for(self.window)
        self.disp_window.show()
        self.textbuffer = msg.get_buffer()
        w_tag = self.textbuffer.create_tag( "warning", weight=Pango.Weight.BOLD, 
                                            foreground_rgba=Gdk.RGBA(0, 0, 0.5, 1))
        e_tag = self.textbuffer.create_tag( "error", weight=Pango.Weight.BOLD, 
                                            foreground_rgba=Gdk.RGBA(0.5, 0, 0, 1))
        msg.modify_font(Pango.FontDescription("Monospace 9"))
        
        # Read logfile and show it's contentself.textview
        f = open('transform.log', 'r')
        for line in f:
            position = self.textbuffer.get_end_iter()
            if line.startswith("INFO:"):
                self.textbuffer.insert(position, line[5:])
            elif line.startswith("WARNING:"):
                self.textbuffer.insert_with_tags(position,line[8:], w_tag)
            elif line.startswith("ERROR:"):
                self.textbuffer.insert_with_tags(position,line[6:], e_tag)
            else:
                self.textbuffer.insert(position, line)
#         self.textbuffer.set_text(''.join(lines))

    def on_displaystate_close(self, *args):
        ''' Suljetaan lokitiedosto-ikkuna '''
        self.disp_window.destroy()
        
    def inputFilechooser_set(self, button):
        ''' The user has selected a file '''
        global input_gedcom
        name = button.get_filename()
        if name:
            input_gedcom = name
            self.message_id = self.st.push(self.st_id, "Syöte " + input_gedcom)
            self.activate_run_button()

    def on_file_open_activate(self, menuitem, data=None):
        ''' Same as inputFilechooser_file_set_cb - not actually needed '''
        global input_gedcom
        self.dialog = Gtk.FileChooserDialog("Open...",
            self.window,
            Gtk.FileChooserAction.OPEN, #Gtk.FILE_CHOOSER_ACTION_OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
             #Gtk.STOCK_CANCEL, Gtk.RESPONSE_CANCEL,  Gtk.STOCK_OPEN, Gtk.RESPONSE_OK))
            )
        self.response = self.dialog.run()
        if self.response == Gtk.ResponseType.OK:
            input_gedcom = self.dialog.get_filename()
            self.message_id = self.st.push(self.st_id, "Syöte " + input_gedcom)
            self.activate_run_button()
            self.dialog.destroy()
        else:
            self.appedShow("Outo palaute {}".format(self.response))

    def activate_run_button(self):
        ''' If file and operation are choosen '''
        global transformer
        global input_gedcom
        runb = self.builder.get_object("runButton")
        if input_gedcom and transformer: 
            runb.set_sensitive(True)
        else: 
            runb.set_sensitive(False)

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

if __name__ == "__main__":
    main = Handler()
    Gtk.main()

Gtk.main()