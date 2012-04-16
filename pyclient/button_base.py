import Tkinter
import math
import Pmw
import confirm_button
from param import *
from control_parse import control_typecast
##
# \namespace button_base
# Control button base class
#


class ButtonBase(Pmw.MegaWidget):
    """
    Control Button base class
    This forms the base class for all contol buttons

    model:
    the layout of a general button type is:
    1. label - 'self.buttonlabel'
    displays the command description--this feature is 'locked in' and
    can not be overridden in inheritance
    2. requested value - call '_selectiondisplaymethod' generates self.selectionvalue
    in the base class this is simply a label with that quantity, but can/should
    be overridden to be more specific to the signal (time, on/off, value, string)
    3. entry method - call '_entrymethod' generates self.entrymethod
    This generates the widget responsible for taking user input and must be
    overridden in inhericance for specific types of input
    4. safety indicator - 'self.indicator'
    displays the safety of the requested command based on bounds passed to
    the class.  This can not be overridden.
    5. change commit indicator - 'self.lockindicator'
    displays whether the command just issues was echoed by an 'ok, changed value'
    from the server.
    6. current value indicator - call '_currentdisplaymethod' generates self.currentvalue
    in the base class this is simply a label with that quantity, but can/should
    be overridden to be more specific to the signal (time, on/off, value, string)
    7. communication button - 'self.sendcmd'
    makes the send button that sends the request to the server in a uniform way
    for each of the methods in the base class that are meant to be overridden
    (_selectiondisplaymethod, _entrymethod, and _currentdisplaymethod), there is
    and associated access method that is meant to be overridden that gives generic
    access to the entry method's value, or the display method,
    (_selectiondisplayaccess, _entryaccess, and _currentdisplayaccess).
    """

    ##
    # \param self member function
    # \param buttonrec parameters that specify the button
    # \param messagequeue queue of messages from the server
    # \param commandqueue queue of commands outbound from the server
    # \param parent parent window
    # \param kw additional options not specified in buttonrec
    def __init__(self,
                 buttonrec,
                 messagequeue,
                 commandqueue,
                 parent=None,
                 **kw):
        optiondefs = (
            ('orient',      'horizontal',     Pmw.INITOPT),
            ('labelmargin', 0,                Pmw.INITOPT),
            ('labelpos',    None,             Pmw.INITOPT)
        )
        # absorb the button options and IO Queue objects
        self.announce = 'ButtonBase: '
        self.defineoptions(kw, optiondefs)
        self.messagequeue = messagequeue
        self.commandqueue = commandqueue
        self.buttonrec = buttonrec

        # Init base class (after defining options).
        Pmw.MegaWidget.__init__(self, parent)
        # Create the components.
        interior = self.interior()

        # process min/max variables (if they exist)
        try:
            self.range_max = self.buttonrec['minmax'][1]
            self.range_min = self.buttonrec['minmax'][0]
        except KeyError:
            self.range_max = 0
            self.range_min = 0

        # make two containers for the label/current/entry wigets
        # these can be collapsed in classes that don't need them
        self.buttonlabelcontainer = \
                self.createcomponent('buttonlabelcontainer',
                                     (), None,
                                     Pmw.Group, interior,
                                     tag_pyclass=None)

        # container to hold the current value of the variable on the server
        self.currentcontainer = self.createcomponent('currentcontainer',
                (), None,
                Pmw.Group, interior, tag_pyclass=None)

        self.currentcontainerlabel = \
                Tkinter.Label(self.currentcontainer.interior(),
                              text='cur: ', bg='#C2AD67')

        self.currentcontainerlabel.pack(padx=0, pady=0, side=Tkinter.LEFT,
                                        fill=Tkinter.X)

        # container to hold all of the editing methods
        self.entrycontainer = self.createcomponent('entrycontainer',
                (), None,
                Pmw.Group, interior, tag_pyclass=None)

        # edit levels:
        # 0 - always in edit mode
        # 1 - edit mode after hitting edit button
        # 2 - display only mode
        if self.buttonrec['edit_level'] == 1:
            self.editmode = self.createcomponent('editmode',
                    (), None,
                    Tkinter.Button, interior,
                    text="Edit",
                    bg="#3D3D3D",
                    fg="#FFFFFF",
                    command=self.flattenentry)
        else:
            if self.buttonrec['edit_level'] == 0:
                btext = " < "

            if self.buttonrec['edit_level'] == 2:
                btext = " "

            self.editmode = self.createcomponent('editmode',
                    (), None,
                    Tkinter.Label, interior,
                    text=btext)

        self.editmode.pack(padx=0, pady=0, side=Tkinter.LEFT)

        self._buttonlabelmethod()
        self._currentdisplaymethod()
        self.entrycontainer.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.buttonlabel.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.currentvalue.pack(padx=0, pady=0, side=Tkinter.RIGHT)

        # Use grid to position all components
        if self['orient'] == 'vertical':
            self.buttonlabelcontainer.grid(row=1, column=1)
            self.currentcontainer.grid(row=2, column=1)
            self.editmode.grid(row=3, column=1)
            self.entrycontainer.grid(row=4, column=1)
            self.createlabel(interior, childRows=4)
        else:
            self.buttonlabelcontainer.grid(row=1, column=1)
            self.currentcontainer.grid(row=1, column=2)
            self.editmode.grid(row=1, column=3)
            self.entrycontainer.grid(row=1, column=4)
            self.createlabel(interior, childCols=4)

        # generate the editor dialog
        self._geneditdialogs()
        # if the mode is display only, then collapse the edit modes
        # this is slightly inefficient
        if buttonrec['edit_level'] == 2:
            self.flattenentry()

        # Check keywords and init options.
        self.initialiseoptions()
        self.lastrequest = None

    ##
    # if the edit level is not set to display mode, the generate the edit
    # dialogs
    def _geneditdialogs(self):
        # container to hold the current selection
        self.selectioncontainer = self.createcomponent('selectioncontainer',
                (), None,
                Pmw.Group, self.entrycontainer.interior(), tag_pyclass=None)

        self.selectioncontainerlabel = \
                Tkinter.Label(self.selectioncontainer.interior(),
                text='sel: ', bg='#C2AD67')

        self.selectioncontainerlabel.pack(padx=0, pady=0, side=Tkinter.LEFT)

        # container to hold the safety indicated for the requested value
        self.safetycontainer = self.createcomponent('safetycontainer',
                (), None,
                Pmw.Group, self.entrycontainer.interior(), tag_pyclass=None)

        self.safetycontainerlabel = \
                Tkinter.Label(self.safetycontainer.interior(), text='safe: ')

        self.safetycontainerlabel.pack(padx=0, pady=0, side=Tkinter.LEFT)

        # container to hold the command commit progress or lock state
        self.lockcontainer = self.createcomponent('lockcontainer',
                (), None,
                Pmw.Group, self.entrycontainer.interior(), tag_pyclass=None)
        self.lockcontainerlabel = Tkinter.Label(self.lockcontainer.interior(),
                text='ack: ', bg='#C2AD67')
        self.lockcontainerlabel.pack(padx=0, pady=0, side=Tkinter.LEFT)

        self._entrymethod()
        self._selectiondisplaymethod()
        self._safetymethod()
        self._lockmethod()

        # 'communication buttons'
        self.sendcmd = self.createcomponent('sendcmd',
                (), None,
                Tkinter.Button, self.entrycontainer.interior(),
                text="Send",
                bg="#3D3D3D",
                fg="#FFFFFF",
                command=self._issueCommand)

        self.sendcmd.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.lockcontainer.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.lock.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.entrymethod.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.safetycontainer.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.safety.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.selectioncontainer.pack(padx=0, pady=0, side=Tkinter.RIGHT)
        self.selectionvalue.pack(padx=0, pady=0, side=Tkinter.RIGHT)

        self.lockstate = False
        self._setlock()

    ##
    # determine whether response matches request
    # \param self member function
    # \param valuein value to test
    # \param testvalue value to test against
    def _thesame(self, valuein, testvalue):
        r"""method to determine whether the echoed command change from the
        server is "the same" as the requested change.  This should be
        overridden in subclasses to reflect what 'the same' means.
        """
        try:
            valuein = float(valuein)
            testvalue = float(valuein)
            return valuein == testvalue
        except ValueError:
            return False

    ##
    # refresh the button lock/value status
    # \param self member function
    # \param type either 'lock', 'value', or 'reply'
    # \param value for type='lock', either 'on' or 'off', otherwise new value
    def refresh_button(self, type, value):
        """the server can perform several operations on the status of a button
         1. toggle the lock indicator
         2. set the current value label
         3. reply to a command (this sets the current value and unlocks)"""
        if type == 'lock':
            print self.announce + 'refreshing lock state to ' + value
            if value == 'on':
                self.lockstate = True
            if value == 'off':
                self.lockstate = False
            self._setlock()
        if type == 'value':
            print self.announce + 'refreshing button value to ' + value
            self._currentdisplayaccess(value)
            self.switch_requested_value(value)
        if type == 'reply':
            print self.announce + 'reply received from the server: ' + value
            self._currentdisplayaccess(value)
            self.switch_requested_value(value)
            if self._thesame(value, self.lastrequest):
                self.lockstate = False
                self._setlock()
            else:
                print self.announce + 'reply from server (' + value + ') ' + \
                  'does not match request (' + self.lastrequest + \
                  '), locking button'
                self.lockstate = True
                self._setlock()

    ##
    # toggle the entry method hiding
    def flattenentry(self):
        self.entrycontainer.toggle()

    ##
    # toggle the button's lock state
    def _setlock(self):
        if self.lockstate:
            self.lock.configure(background=LOCKED)
        else:
            self.lock.configure(background=UNLOCKED)

    ##
    # create the button label component object
    def _buttonlabelmethod(self):
        self.buttonlabel = self.createcomponent('buttonlabel',
                (), None,
                Tkinter.Label, self.buttonlabelcontainer.interior(),
                        text=self.buttonrec['desc'],
                        fg='#FFFFFF',
                        bg='#3E5D75',
                        width=50,
                        anchor=Tkinter.W,
                        justify=Tkinter.LEFT)

    ##
    # create the 'currently selected' field display
    def _selectiondisplaymethod(self):
        self.selectionvalue = self.createcomponent('selectionvalue',
                (), None,
                Tkinter.Label, self.selectioncontainer.interior(),
                    width=10, bg='#E1DCC8')

    ##
    # access method for the 'currently selected' field display value
    # \param inputvalue new value for the selection value field
    def _selectiondisplayaccess(self, inputvalue):
        if 'units' in self.buttonrec:
            unitlabel = self.buttonrec['units']
        else:
            unitlabel = ''
        self.selectionvalue.configure(text=inputvalue + ' ' + unitlabel)

    ##
    # create the 'currently active' field display
    def _currentdisplaymethod(self):
        if 'current_display_width' in self.buttonrec:
            dispwidth = self.buttonrec['current_display_width']
        else:
            dispwidth = 10

        self.currentvalue = self.createcomponent('currentvalue',
                (), None,
                Tkinter.Label, self.currentcontainer.interior(),
                    width=dispwidth, bg='#E1DCC8')

    ##
    # access method for the 'currently active' field display value
    # \param inputvalue new value for the display field
    def _currentdisplayaccess(self, inputvalue):
        self.currentvalue.configure(text=inputvalue)

    ##
    # Access method for the value of the requested value.
    # \param inputvalue new value for the request field.
    def switch_requested_value(self, inputvalue):
        print self.announce + 'no derived class for switch_requested_value().'

    ##
    # create the safety indicator for the button, requested state
    def _safetymethod(self):
        self.safety = self.createcomponent('safety',
                (), None,
                Tkinter.Frame, self.safetycontainer.interior(),
                        width=16,
                        height=16,
                        borderwidth=1,
                        relief='raised')

    ##
    # create the current button's lock indicator
    def _lockmethod(self):
        self.lock = self.createcomponent('lock',
                (), None,
                Tkinter.Frame, self.lockcontainer.interior(),
                        width=16,
                        height=16,
                        borderwidth=1,
                        relief='raised')

    ##
    # create the button's entry method
    def _entrymethod(self):
        self.entrymethod = self.createcomponent('entrymethod',
                (), None,
                Pmw.EntryField, self.entrycontainer.interior(),
                        labelpos='w',
                        value='Abstract base class',
                        label_text='',
                        modifiedcommand=self._doCommand)

    ##
    # read access method to the button's entry field
    def _entryaccess(self):
        print 'ButtonBase, abstract base class, override _entryaccess'
        return None

    ##
    # issue a command to the server
    def _issueCommand(self):
        """after issuing the command, set the lock flag and wait for a server
        response if the server responds with a new value, and that value is the
        same as the one requested, then lock->unlocked, indicating that the
        command was committed
        """
        fieldvalue = control_typecast(self._entryaccess(), 'string')
        self.confirmbutton = confirm_button.ConfirmButton(self.buttonrec,
                                                          fieldvalue)
        if self.confirmbutton.confirmed:
            print self.announce + 'Command confirmed'
            print self.announce + 'sending ' + fieldvalue

            self.commandqueue.put('dput_verbose ' + \
                                  self.buttonrec['destination'] + ' ' + \
                                  self.buttonrec['short_name'] + ' ' + \
                                  fieldvalue)

            self.lockstate = True
            self._setlock()
            self.lastrequest = fieldvalue
        else:
            print self.announce + 'Command cancelled'

    def _doCommand(self):
        print 'ButtonBase, abstrct base class, override _doCommand'
