# ACT main control interface 
# Eric Switzer, March 29, 2006. (switzer@princeton.edu)
import Tkinter
import Pmw
import control_parse
import button_base
import input_onoff
import input_select
import input_float
import input_clicker
import input_string
import input_string_pulldown
import input_float_slider
import input_pulldown
import input_timerclicker
GUI_MESSAGE = 'gui_message'
##
# \namespace windows
# Class to manage the creation of system windows 
#

def compare_cmdorder(x,y):
  return x['displayorder']-y['displayorder']

# make a selection - "Go"
def input_select_name(cmditem, messagequeue, commandqueue, page): 
  return input_select.InputSelect(cmditem, messagequeue, commandqueue, page)

# Input an on/off signal
def input_onoff_name(cmditem, messagequeue, commandqueue, page): 
  return input_onoff.InputOnOff(cmditem, messagequeue, commandqueue, page)

# Integer clicker 
def input_clicker_name(cmditem, messagequeue, commandqueue, page): 
  return input_clicker.InputClicker(cmditem, messagequeue, commandqueue, page)

# Pulldown selection menu
def input_pulldown_name(cmditem, messagequeue, commandqueue, page): 
  return input_pulldown.InputPullDown(cmditem, messagequeue, commandqueue, page)

# Slider to input floats
def input_float_slider_name(cmditem, messagequeue, commandqueue, page): 
  return input_float_slider.InputFloatSlider(cmditem, messagequeue, commandqueue, page)

# Input a float
def input_float_name(cmditem, messagequeue, commandqueue, page): 
  return input_float.InputFloat(cmditem, messagequeue, commandqueue, page)

# Timer clicker method
def input_timerclicker_name(cmditem, messagequeue, commandqueue, page):
  return input_timerclicker.InputTimerClicker(cmditem, messagequeue, commandqueue, page)

# input strings
def input_string_name(cmditem, messagequeue, commandqueue, page): 
  return input_string.InputString(cmditem, messagequeue, commandqueue, page)

# input strings + pulldown options
def input_string_pulldown_name(cmditem, messagequeue, commandqueue, page): 
  return input_string_pulldown.InputStringPulldown(cmditem, messagequeue, commandqueue, page)

type_switch = {
  "input_select": input_select_name,
  "input_onoff": input_onoff_name,
  "input_clicker": input_clicker_name,
  "input_pulldown": input_pulldown_name,
  "input_float": input_float_name,
  "input_float_slider": input_float_slider_name,
  "input_timerclicker": input_timerclicker_name,
  "input_string": input_string_name,
  "input_string_pulldown": input_string_pulldown_name}

class SystemControlWindow:
  def __init__(self, parent, db, messagequeue, commandqueue, sysname):
    self.announce = 'SystemControlWindow: '
    self.messagequeue = messagequeue
    self.commandqueue = commandqueue
    Pmw.Color.changecolor(parent,background = '#3E5D75', foreground = '#FFFFFF')

    # pack the tabbed menu for each category of control commands
    self.syswindow = Tkinter.Toplevel()
    self.syswindow.title(repr(sysname))
    notebook = Pmw.NoteBook(self.syswindow)
    notebook.pack(fill = 'both', expand = 1, padx = 10, pady = 10)

    # for each category of control for the system, generate a new 
    # tab, and for each tab, generate all the controls for that category
    categories = control_parse.find_subgroups(db,'system',sysname,'category')
    print categories
    self.command_hierarchy={}
    for category_item in categories:
      page = notebook.add(category_item)
      cmdtag = control_parse.find_commands(db,'system',sysname,'category',category_item)
      cmdtag.sort(compare_cmdorder)
      for cmditem in cmdtag:
        #if cmditem['system'] == sysname and cmditem['category'] == category_item:
        #print category_item + " " + repr(cmditem)
        self.command_hierarchy[cmditem['short_name']] = \
          type_switch.get(cmditem['type'])(cmditem, self.messagequeue, self.commandqueue, page)
        self.command_hierarchy[cmditem['short_name']].pack(side = Tkinter.TOP, anchor=Tkinter.W)
        # to pass options not in the command specification (cmditem)
        # keyword=value_to_pass, 
    notebook.setnaturalsize()
    # now collapse the entry methods after the maximum window size is known
    for category_item in categories:
      cmdtag = control_parse.find_commands(db, 'system', sysname, 'category', category_item)
      for cmditem in cmdtag:
        if cmditem['edit_level'] == 1:
          self.command_hierarchy[cmditem['short_name']].flattenentry()
    # put in a refresh order 
    self.commandqueue.put('refresh')

  # refresh method (this changes attributes of a given button to reflect server messages)
  def refresh_system(self, msg):
   # take everything following, and including the GUI_MESSAGE tag and 
   # parse it into button messages 
   RefreshString = msg[msg.find(GUI_MESSAGE):].split()
   RefreshShortname = RefreshString[1]
   RefreshType = RefreshString[2]
   RefreshVal = RefreshString[3]
   ButtonsAvailable = self.command_hierarchy.keys()
   if ButtonsAvailable.count(RefreshShortname) > 1:
     print 'SystemControlWindow: ambiguous button refresh request, more than one button by this name'
   else:
     try: 
       ButtonsAvailable.index(RefreshShortname)
       print 'hwid: '+repr(RefreshShortname)+' type: '+repr(RefreshType)+' val: '+repr(RefreshVal)
       self.command_hierarchy[RefreshShortname].refresh_button(RefreshType, RefreshVal)
     except ValueError:
       None
       #print 'SystemControlWindow: this system has no button named ' +repr(RefreshShortname)

