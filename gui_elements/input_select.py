import Tkinter
import Pmw
import confirm_button
import button_base
from param import *
##
# \namespace input_select
# on/off toggle class
#

class InputSelect(Pmw.MegaWidget, button_base.ButtonBase):
    """ issue a "go"
    """

    def __init__(self, buttonrec, messagequeue, commandqueue, parent = None, **kw):
      button_base.ButtonBase.__init__(self, buttonrec, messagequeue, commandqueue, parent, **kw)
      self.announce = 'InputSelect: '
      self.selectioncontainer.collapse()
      self.safetycontainer.collapse()
      self.currentcontainer.collapse()

    # Create the button component.
    def _entrymethod(self):
      self.entrymethod = self.createcomponent('entrymethod',
              (), None,
              Tkinter.Frame, self.entrycontainer.interior(),
                      width = 3,
                      height = 3,
                      borderwidth = 1,
                      relief = 'raised')


    # define the display methods
    def _currentdisplaymethod(self):
      self.currentvalue = self.createcomponent('currentvalue',
              (), None,
              Tkinter.Frame, self.currentcontainer.interior(),
                      width = 3,
                      height = 3,
                      borderwidth = 1,
                      relief = 'raised')

    def _currentdisplayaccess(self, value):
      None
 
    # define the 'same' function 
    def _thesame(self,valuein,testvalue):
     try:
         valuein = int(float(valuein))
         return valuein == 1
     except ValueError:
         return False

    def _entryaccess(self):
      return 1

    def _doCommand(self, tag, state):
      None

