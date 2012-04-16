import Tkinter, Pmw
import shelve
import math
import confirm_button
import button_base
import control_parse
from param import MASTER_SHELVE
##
# \namespace input_string_pulldown
# pulldown menu selection and string entry class
#

class InputStringPulldown(Pmw.MegaWidget,button_base.ButtonBase):
    """ enter strings
    """

    def __init__(self, buttonrec, messagequeue, commandqueue, parent = None, **kw):
        button_base.ButtonBase.__init__(self, buttonrec, messagequeue, commandqueue, parent, **kw)
        self.announce = 'InputStringPulldown: '
        self.safetycontainer.collapse()
        self.selectioncontainer.collapse()

    def _entrymethod(self):
        # make the entry bar
        self.entrymethod = self.createcomponent('entrymethod',
                (), None,
                Pmw.Group, self.entrycontainer.interior(), tag_pyclass=None)
        self._entrybar()
        self._pulldownbar()
        self.entrybar.pack(padx = 0, pady = 0, side=Tkinter.RIGHT)
        self.pulldownbar.pack(padx = 0, pady = 0, side=Tkinter.LEFT)

    def _entrybar(self): 
        self.entrybar = self.createcomponent('entrybar',
                (), None,
                Pmw.EntryField, self.entrymethod.interior(),
                labelpos = 'w',
                value = '',
                label_text='',
                modifiedcommand = self._doCommand,
                validate = None)

    def _pulldownbar(self):
        self.db = shelve.open(MASTER_SHELVE,"r")
        self.pulldownlist = self.db[self.buttonrec['options']]
        self.items = control_parse.pare_pulldown(self.pulldownlist)
        #self.var = self.items[self.buttonrec['default_val']] 
        self.pulldownbar = self.createcomponent('pulldownbar',
                (), None,
                Pmw.OptionMenu, self.entrymethod.interior(),
                        labelpos = 'w',
                        label_text = 'type: ',
                        #menubutton_textvariable = self.var,
                        items = self.items.values(),  
                        hull_borderwidth = 1,
                        menubutton_width = 20,
                        hull_relief = 'ridge')

    def _entryaccess(self):
      #return self.entrybar.getvalue()+repr(int(control_parse.value_to_key(self.items,self.entrymethod.getvalue())[0])) 
      cmd_statement = self.entrybar.getvalue()
      cmd_type = control_parse.value_to_key(self.items,self.pulldownbar.getvalue())[0]
      return control_parse.flatten_string(cmd_type+' '+cmd_statement)

    def _doCommand(self):
        #print 'changed number entry field'
        None
