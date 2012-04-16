import Tkinter
import Pmw
import confirm_button
import button_base
##
# \namespace input_float_slider
# floating point slider entry method
#

class InputFloatSlider(Pmw.MegaWidget,button_base.ButtonBase):
    """ set floating point numbers (slider entry)
    """

    def __init__(self, buttonrec, messagequeue, commandqueue, parent = None, **kw):
      button_base.ButtonBase.__init__(self, buttonrec, messagequeue, commandqueue, parent, **kw)
      self.announce = 'InputFloatSlider: '

    def _entrymethod(self):
      # Create the scale component.
      self.tickinterval = (self.range_max-self.range_min)/5.0
      if self['orient'] == 'vertical':
          from_ = self.range_max
          to = self.range_min 
      else:
          from_ = self.range_min
          to = self.range_max
      # make the entry slider
      self.entrymethod = self.createcomponent('entrymethod',
              (), None,
              Tkinter.Scale, self.entrycontainer.interior(),
                      orient = self['orient'],
                      command = self._doCommand,
                      tickinterval = self.tickinterval,
                      length = 200,
                      from_ = from_,
                      to = to,
                      showvalue = 0)

      value = self.buttonrec['default_val']
      if value is not None:
          self.entrymethod.set(value)

    def _entryaccess(self):
      return self.entrymethod.get()

    # access method to the current value component
    def _currentdisplayaccess(self, inputvalue):
      self.currentvalue.configure(text = inputvalue + " %") 

    # access method to the current value component
    def _selectiondisplayaccess(self, inputvalue):
      self.selectionvalue.configure(text = inputvalue + " %") 

    def _doCommand(self, valueStr):
      valueInt = self.entrymethod.get()
      colors = self.buttonrec['colors']
      thresholds = self.buttonrec['thresholds']
      color = colors[-1]
      for index in range(len(colors) - 1):
        if valueInt <= thresholds[index]:
          color = colors[index]
          break
      self.safety.configure(background = color)
      self._selectiondisplayaccess(valueStr)

    def switch_requested_value(self, inputvalue):
      if inputvalue is not None:
          self.entrymethod.set(inputvalue)

Pmw.forwardmethods(InputFloatSlider, Tkinter.Scale, 'scale')

