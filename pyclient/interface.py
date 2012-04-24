"""system GUI class that spawns control windows"""
import Tkinter
import Pmw
import time
import threading
import random
import Queue
import sys
import shelve
import control_parse    # parse the control list
from param import *
sys.path.append(INSTALL_DIR+'/gui_elements/')
sys.path.append('./gui_elements/')
import windows

class MainInterface:
    """------------------------------------------------------------------------------
         Central GUI interface class
         ------------------------------------------------------------------------------
         model:
             This class will generate a central server window and buttons, and generate
             GUI windows to control individual systems. Incoming messages are dished out to
             the other windows, to their 'refresh_system' method. If the messages are
             not destined for individual system windows, they're issued in a text window.
    """
    def __init__(self, parent, options, messagequeue, commandqueue, exitClient):
        self.announce = 'MainInterface: '
        self.options = options
        self.messagequeue = messagequeue
        self.commandqueue = commandqueue
        Pmw.initialise(root=parent,size=12,fontScheme='pmw1')

        parent.title("Server Message Window")
        self.scroller = Tkinter.Scrollbar(parent)
        self.textbar = Tkinter.Text(parent)
        self.commententry = Tkinter.Entry(parent)

        # set up the command list window
        self.buttonframe = Tkinter.Frame(parent)
        self.instacklabel = Tkinter.Label(self.buttonframe, text="in label")
        self.outstacklabel = Tkinter.Label(self.buttonframe, text="out label")
        self.refreshbutton = Tkinter.Button(self.buttonframe, text="Refresh")
        self.clearbutton = Tkinter.Button(self.buttonframe, text="Clear Window")
        self.insertbutton = Tkinter.Button(self.buttonframe, text="Insert Comment")
        self.whobutton = Tkinter.Button(self.buttonframe, text="Who")
        self.bindbutton = Tkinter.Button(self.buttonframe, text="Show bindings")
        self.lockbutton = Tkinter.Button(self.buttonframe, text="Toggle server lock")
        self.exitbutton = Tkinter.Button(self.buttonframe, text="Exit")

        # pack the buttons
        self.instacklabel.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        self.outstacklabel.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        self.refreshbutton.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        self.clearbutton.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        self.insertbutton.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        self.whobutton.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        self.bindbutton.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        self.lockbutton.pack(side=Tkinter.LEFT, fill=Tkinter.X)
        self.exitbutton.pack(side=Tkinter.LEFT, fill=Tkinter.X)

        self.buttonframe.pack(side=Tkinter.TOP, fill=Tkinter.X)
        self.commententry.pack(side=Tkinter.TOP, fill=Tkinter.X)
        self.scroller.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.textbar.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)

        # configure each of the widgets
        self.scroller.config(command=self.textbar.yview)
        self.textbar.config(yscrollcommand=self.scroller.set)
        self.textbar.config(background="black", foreground="white", state="disabled")

        self.refreshbutton.config(command=self.issue_refresh)
        self.clearbutton.config(command=self.clear_textbar)
        self.insertbutton.config(command=self.insert_comment)
        self.whobutton.config(command=self.query_who)
        self.bindbutton.config(command=self.show_binding)
        self.lockbutton.config(command=self.lock_server)
        self.exitbutton.config(command=exitClient)

        # read in the master control shelve file
        self.db = shelve.open(MASTER_SHELVE, "r")

        # set up the about window to disply version information, etc
        #Pmw.aboutversion('2.0')
        Pmw.aboutcopyright('control database version: \
                                             ' + self.db['version']['version'])
        Pmw.aboutcontact(
                'GCIPy 2.0 \n\n' +
                'Contacts: (for subsystem clients to the interface_server) \n' +
                'AMCP housekeeping: Adam Hincks, Eric Switzer \n' +
                'AMCP KUKA interface: Adam Hincks, Jeff Funke \n' +
                'MCE scripts, operation: UBC MCE group, Michael Niemack, Eric Switzer \n' +
                'MCE tuning: Elia Battistelli, Michael Niemack \n' +
                'MCE control client: Eric Switzer \n' +
                '(based on the Python General Control Interface, Switzer 4/08/06) \n'
                )
        self.aboutdia = Pmw.AboutDialog(parent, applicationname = 'ACT Control Interface')
        self.aboutdia.withdraw()

        # Create button to launch the dialog.
        self.aboutbutton = Tkinter.Button(self.buttonframe, text = 'Client Info',
            command = self.execute_about)
        self.aboutbutton.pack(side=Tkinter.LEFT, fill=Tkinter.X)

        # set up the system control windows
        # default is to open none
        self.system_list = control_parse.find_groups(self.db,"system")
        if self.options['ARGV_SYSTEM']:
            if self.options['ARGV_SYSTEM'] in self.system_list:
                self.system_list = [ self.options['ARGV_SYSTEM'] ]
            else:
                print self.announce+'can not spawn '+self.options['ARGV_SYSTEM']
                sys.exit()
        else:
            self.system_list = []

        if len(self.system_list) is 0:
            print "use the command line argument -o or --list to list possible commanding systems"

        print self.announce+'Setting up windows for the systems, '+repr(self.system_list)
        self.window_hierarchy={}
        for self.system_item in self.system_list:
            print self.announce+'System: ' + self.system_item
            self.window_hierarchy[self.system_item]= \
                     windows.SystemControlWindow(parent, \
                                                 self.db, \
                                                 self.messagequeue, \
                                                 self.commandqueue, \
                                                 self.system_item)

    def execute_about(self):
        self.aboutdia.show()

    # send a put command
    def insert_comment(self):
        self.commandqueue.put('put '+self.commententry.get())

    def query_who(self):
        self.commandqueue.put('who')

    def show_binding(self):
        self.commandqueue.put('print_ids')

    def lock_server(self):
        self.commandqueue.put('togglelock')

    # put information in the text box
    def insert_text(self,text_insert):
        self.textbar.config(state="normal")
        self.textbar.insert(Tkinter.END,text_insert)
        self.textbar.config(state="disabled")
        self.textbar.see(Tkinter.END)

    def issue_refresh(self):
        self.commandqueue.put('refresh')

    # clear the text bar
    def clear_textbar(self):
        self.textbar.config(state="normal")
        self.textbar.delete(1.0,Tkinter.END)
        self.textbar.config(state="disabled")

    # treat incoming data
    def incoming_stream(self):
        # update the number of items on the stack
        self.instacklabel.config(text='in: '+repr(self.messagequeue.qsize()))
        self.outstacklabel.config(text='out: '+repr(self.commandqueue.qsize()))
        # proces seach message on the incoming stack
        while self.messagequeue.qsize():
            try:
                msg = self.messagequeue.get(0)
                # if the server message is destined for a button, then it will be prepended by
                # GUI_MESSAGE, otherwise, just write it to the text box on the server message window
                if msg.find(GUI_MESSAGE) == -1:
                    self.insert_text(control_parse.unflatten_string(msg)+'\n')
                else:
                    # hand the message to each window
                    for self.system_item in self.system_list:
                        self.window_hierarchy[self.system_item].refresh_system(msg)
            except Queue.Empty:
                pass

