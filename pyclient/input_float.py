""" floating point entry class"""
import Tkinter
import math
import Pmw
import confirm_button
import button_base


class InputFloat(Pmw.MegaWidget, button_base.ButtonBase):
    """ set floating point numbers (field entry)
    """

    def __init__(self, buttonrec,
                 messagequeue, commandqueue,
                 parent=None, **kw):

        button_base.ButtonBase.__init__(self, buttonrec,
                                        messagequeue, commandqueue,
                                        parent, **kw)

        self.announce = 'InputFloat: '
        self.selectioncontainer.collapse()
        self.safetycontainer.collapse()

    def _entrymethod(self):
        # make the entry bar
        self.entrymethod = self.createcomponent('entrymethod',
                        (), None,
                        Pmw.EntryField, self.entrycontainer.interior(),
                        labelpos='w',
                        value=self.buttonrec['default_val'],
                        label_text='',
                        modifiedcommand=self._doCommand,
                        validate={'validator': 'real',
                                  'min': self.range_min,
                                  'max': self.range_max})

    def _entryaccess(self):
        return float(self.entrymethod.getvalue())

    # access method to the current value component
    def _currentdisplayaccess(self, inputvalue):
        formatted = '%5.3f' % float(inputvalue)

        if 'units' in self.buttonrec:
            unitlabel = self.buttonrec['units']
        else:
            unitlabel = ''

        self.currentvalue.configure(text=formatted + ' ' + unitlabel)

    # access method to the current value component
    def _selectiondisplayaccess(self, inputvalue):
        formatted = '%5.3f' % float(inputvalue)
        self.selectionvalue.configure(text=formatted)

    def _doCommand(self):
        #print 'changed number entry field'
        None

    def switch_requested_value(self, inputvalue):
        formatted = '%5.3f' % float(inputvalue)
        self.entrymethod.setvalue(formatted)
