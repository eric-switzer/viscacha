import Tkinter
import math
import Pmw
import confirm_button
import button_base
##
# \namespace input_clicker
# integer clicker entry class 
#

class InputClicker(Pmw.MegaWidget,button_base.ButtonBase):
    """ set integers using either a clicker or field entry
    """

    def __init__(self, buttonrec, messagequeue, commandqueue, parent = None, **kw):
        button_base.ButtonBase.__init__(self, buttonrec, messagequeue, commandqueue, parent, **kw)
        self.announce = 'InputClicker: '
        self.selectioncontainer.collapse()
        self.safetycontainer.collapse()

    def _entrymethod(self):
        # make the entry bar
        self.entrymethod = self.createcomponent('entrymethod',
                (), None,
                Pmw.Counter, self.entrycontainer.interior(),
                        labelpos = 'w',
                        entryfield_value = self.buttonrec['default_val'],
                        label_text='',
                        entryfield_command = self._doCommand,
                        entryfield_validate = {'validator' : 'integer',
                                'min' : self.range_min, 'max' : self.range_max})

    def _entryaccess(self):
      #return float(self.entrymethod.getvalue())
      return int(self.entrymethod.getvalue())

    # access method to the current value component
    def _currentdisplayaccess(self, inputvalue):
      if self.buttonrec.has_key('units'):
        unitlabel = self.buttonrec['units']
      else:
        unitlabel = ''
      #formatted = '%5.3f' % float(inputvalue)
      self.currentvalue.configure(text = inputvalue + ' '+unitlabel) 

    # access method to the current value component
    def _selectiondisplayaccess(self, inputvalue):
      formatted = '%5.3f' % float(inputvalue)
      self.selectionvalue.configure(text = formatted) 

    def _doCommand(self):
       #print 'changed number entry field'
       None
