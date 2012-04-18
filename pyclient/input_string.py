""" string entry class"""
import Tkinter
import math
import Pmw
import confirm_button
import button_base


class InputString(Pmw.MegaWidget, button_base.ButtonBase):
    """ enter strings
    """

    def __init__(self, buttonrec,
                 messagequeue, commandqueue,
                 parent=None, **kw):

        button_base.ButtonBase.__init__(self, buttonrec,
                                        messagequeue, commandqueue,
                                        parent, **kw)

        self.announce = 'InputString: '
        self.safetycontainer.collapse()
        self.selectioncontainer.collapse()

    def _entrymethod(self):
        # make the entry bar
        self.entrymethod = self.createcomponent('entrymethod',
                (), None,
                Pmw.EntryField, self.entrycontainer.interior(),
                labelpos='w',
                value=self.buttonrec['default_val'],
                label_text='',
                modifiedcommand=self._doCommand,
                validate=None)

    def _thesame(self, valuein, testvalue):
        try:
            return valuein == testvalue
        except ValueError:
            return False

    def _entryaccess(self):
        return self.entrymethod.getvalue()

    def _doCommand(self):
        None
        #print 'changed number entry field'

    def switch_requested_value(self, inputvalue):
        self.entrymethod.setvalue(inputvalue)
