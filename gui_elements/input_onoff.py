import Tkinter
import Pmw
import confirm_button
import button_base
##
# \namespace input_onoff
# on/off toggle class
#

class InputOnOff(Pmw.MegaWidget,button_base.ButtonBase):
    """ turn something on/off
    """

    def __init__(self, buttonrec, messagequeue, commandqueue, parent = None, **kw):
      button_base.ButtonBase.__init__(self, buttonrec, messagequeue, commandqueue, parent, **kw)
      self.announce = 'InputOnOff: '
      self.safetycontainer.collapse()
      self.selectioncontainer.collapse()

    def _entrymethod(self):
      self.entrymethod = self.createcomponent('entrymethod',
              (), None,
              Pmw.RadioSelect, self.entrycontainer.interior(),
                      buttontype = 'radiobutton',
                      orient = 'horizontal',
                      labelpos = 'w',
                      label_text = '',
                      command = self._doCommand,
                      hull_borderwidth = 1,
                      hull_relief = 'ridge')
       
      self.entrymethod.add('on');
      self.entrymethod.add('off');
      value = self.buttonrec['default_val']
      if value is 1:
        self.entrymethod.setvalue('on')
      else: 
        self.entrymethod.setvalue('off')

    # define the display method
    #def _currentdisplaymethod(self):
    #  self.currentvalue = self.createcomponent('currentvalue',
    #       (), None,
    #       Tkinter.Frame, self.currentcontainer.interior(),
    #       width=16, height = 16, borderwidth = 0, relief = 'raised')
   
    # access method to the current value component
    def _currentdisplayaccess(self, inputvalue):
      print inputvalue
      if int(float(inputvalue)) >= 0.5:
        self.currentvalue.configure(bg = "#ffffff")
        self.currentvalue.configure(text = "on")
      else:
        self.currentvalue.configure(bg = "#999999")
        self.currentvalue.configure(text = "off")
    
    # define the 'same' function 
    def _thesame(self,valuein,testvalue):
     try:
         valuein = int(float(valuein))
         testvalue = int(float(valuein))
         return valuein == testvalue
     except ValueError:
         return False

    def _entryaccess(self):
      valueStr = self.entrymethod.getcurselection()
      print valueStr
      if valueStr is 'on':
        return 1
      else:
        return 0

    def _doCommand(self, valueStr):
      None 

    def switch_requested_value(self, inputvalue):
      if int(float(inputvalue)) >= 0.5:
        self.entrymethod.setvalue('on')
      else:
        self.entrymethod.setvalue('off')
