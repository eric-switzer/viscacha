r""" Class to manage the creation of system windows"""
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


def compare_cmdorder(x, y):
    return x['displayorder'] - y['displayorder']


# make a selection - "Go"
def input_select_func(cmditem, messagequeue, commandqueue, page):
    return input_select.InputSelect(cmditem, messagequeue, commandqueue, page)


# Input an on/off signal
def input_onoff_func(cmditem, messagequeue, commandqueue, page):
    return input_onoff.InputOnOff(cmditem, messagequeue, commandqueue, page)


# Integer clicker
def input_clicker_func(cmditem, messagequeue, commandqueue, page):
    return input_clicker.InputClicker(cmditem, messagequeue,
                                      commandqueue, page)


# Pulldown selection menu
def input_pulldown_func(cmditem, messagequeue, commandqueue, page):
    return input_pulldown.InputPullDown(cmditem, messagequeue,
                                        commandqueue, page)


# Slider to input floats
def input_float_slider_func(cmditem, messagequeue, commandqueue, page):
    return input_float_slider.InputFloatSlider(cmditem, messagequeue,
                                               commandqueue, page)


# Input a float
def input_float_func(cmditem, messagequeue, commandqueue, page):
    return input_float.InputFloat(cmditem, messagequeue,
                                  commandqueue, page)


# Timer clicker method
def input_timerclicker_func(cmditem, messagequeue, commandqueue, page):
    return input_timerclicker.InputTimerClicker(cmditem, messagequeue,
                                                commandqueue, page)


# input strings
def input_string_func(cmditem, messagequeue, commandqueue, page):
    return input_string.InputString(cmditem, messagequeue,
                                    commandqueue, page)


# input strings + pulldown options
def input_string_pulldown_func(cmditem, messagequeue, commandqueue, page):
    return input_string_pulldown.InputStringPulldown(cmditem, messagequeue,
                                                     commandqueue, page)


type_switch = {
    "input_select": input_select_func,
    "input_onoff": input_onoff_func,
    "input_clicker": input_clicker_func,
    "input_pulldown": input_pulldown_func,
    "input_float": input_float_func,
    "input_float_slider": input_float_slider_func,
    "input_timerclicker": input_timerclicker_func,
    "input_string": input_string_func,
    "input_string_pulldown": input_string_pulldown_func}


class SystemControlWindow:
    def __init__(self, parent, db, messagequeue, commandqueue, sysname):
        self.announce = 'SystemControlWindow: '
        self.messagequeue = messagequeue
        self.commandqueue = commandqueue
        Pmw.Color.changecolor(parent, background='#3E5D75',
                              foreground='#FFFFFF')

        # pack the tabbed menu for each category of control commands
        self.syswindow = Tkinter.Toplevel()
        self.syswindow.title(repr(sysname))
        notebook = Pmw.NoteBook(self.syswindow)
        notebook.pack(fill='both', expand=1, padx=10, pady=10)

        # for each category of control for the system, generate a new
        # tab, and for each tab, generate all the controls for that category
        categories = control_parse.find_subgroups(db, 'system',
                                                  sysname, 'category')

        print categories
        self.command_hierarchy = {}
        for category_item in categories:
            page = notebook.add(category_item)
            cmdtag = control_parse.find_commands(db, 'system', sysname,
                                                 'category', category_item)

            cmdtag.sort(compare_cmdorder)
            for cmditem in cmdtag:
                #if cmditem['system'] == sysname and \
                #   cmditem['category'] == category_item:
                #print category_item + " " + repr(cmditem)
                self.command_hierarchy[cmditem['short_name']] = \
                    type_switch.get(cmditem['type'])(cmditem,
                                    self.messagequeue, self.commandqueue, page)

                self.command_hierarchy[cmditem['short_name']].pack(side=Tkinter.TOP, anchor=Tkinter.W)
                # to pass options not in the command specification (cmditem)
                # keyword=value_to_pass,
        notebook.setnaturalsize()
        # now collapse the entry methods after the maximum window size is known
        for category_item in categories:
            cmdtag = control_parse.find_commands(db, 'system', sysname,
                                                 'category', category_item)
            for cmditem in cmdtag:
                if cmditem['edit_level'] == 1:
                    self.command_hierarchy[cmditem['short_name']].flattenentry()
        # put in a refresh order
        self.commandqueue.put('refresh')

    def refresh_system(self, msg):
        # take everything following, and including the GUI_MESSAGE tag and
        # parse it into button messages
        refresh_string = msg[msg.find(GUI_MESSAGE):].split()
        refresh_shortname = refresh_string[1]
        refresh_type = refresh_string[2]
        refresh_val = refresh_string[3]
        buttons_available = self.command_hierarchy.keys()
        if buttons_available.count(refresh_shortname) > 1:
            print 'SystemControlWindow: refresh more than one button error'
        else:
            try:
                buttons_available.index(refresh_shortname)
                print 'hwid: ' + repr(refresh_shortname) + \
                      ' type: ' + repr(refresh_type) + \
                      ' val: ' + repr(refresh_val)

                self.command_hierarchy[refresh_shortname].refresh_button(refresh_type, refresh_val)
            except ValueError:
                pass
                print 'This system has no button named %s' % refresh_shortname
