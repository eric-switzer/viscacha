import Tkinter
import math
import Pmw
import confirm_button
import button_base
##
# \namespace input_timerclicker
# time H:M:S clicker entry class
#

# convert time in seconds to H:M:S format
def convert_time(timeInt):
  mm = math.modf(timeInt/60.0)
  seconds = int(mm[0]*60)
  hm = math.modf(mm[1]/60.0)
  minutes = int(hm[0]*60)
  hours = int(hm[1])

  return repr(hours)+":"+repr(minutes)+":"+repr(seconds)


class InputTimerClicker(Pmw.MegaWidget,button_base.ButtonBase):
    """ set timers
    """

    def __init__(self, buttonrec, messagequeue, commandqueue, parent = None, **kw):
      button_base.ButtonBase.__init__(self, buttonrec, messagequeue, commandqueue, parent, **kw)
      self.announce = 'InputTimerClicker: '
      self.selectioncontainer.collapse()
      self.safetycontainer.collapse()

    def _entrymethod(self):
        self.entrymethod = self.createcomponent('entrymethod',
                (), None,
                Pmw.TimeCounter, self.entrycontainer.interior(),
                        labelpos = 'w',
                        label_text='HH:MM:SS',
                        command = self._doCommand,
                        min = '00:00:00',
                        max = '23:59:59')

        self.nvalue = convert_time(self.buttonrec['default_val'])
        if self.nvalue is not None:
            self.entrymethod.setvalue(self.nvalue)

    def _entryaccess(self):
      return float(self.entrymethod.getint())

    def _currentdisplayaccess(self, inputvalue):
      self.currentvalue.configure(text = repr(int(float(inputvalue)))+ "sec")

    def _doCommand(self):
        valueInt = self.entrymethod.getint()
        valueStr = self.entrymethod.getstring()
        self._selectiondisplayaccess('fucket')
    
    def switch_requested_value(self, inputvalue):
      print self.announce + 'Someone needs to write the ' \
                            'switch_requested_value() method here.  '\
                            'It needs to parse input value to a time. -AH'
