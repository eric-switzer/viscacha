""" pulldown menu selection class """
import shelve
import Tkinter
import Pmw
import confirm_button
import button_base
import control_parse
from param import MASTER_SHELVE


class InputPullDown(Pmw.MegaWidget, button_base.ButtonBase):
    """ pulldown menu for mode selection
    """

    def __init__(self, buttonrec,
                 messagequeue, commandqueue,
                 parent=None, **kw):

        button_base.ButtonBase.__init__(self, buttonrec,
                                        messagequeue, commandqueue,
                                        parent, **kw)

        self.announce = 'InputPullDown: '
        self.safetycontainer.collapse()
        self.selectioncontainer.collapse()

        def _entrymethod(self):
            self.db = shelve.open(MASTER_SHELVE, "r")
            self.pulldownlist = self.db[self.buttonrec['options']]
            self.items = control_parse.pare_pulldown(self.pulldownlist)
            self.var = self.items[repr(self.buttonrec['default_val'])]
            self.entrymethod = self.createcomponent('entrymethod',
                      (), None,
                      Pmw.OptionMenu, self.entrycontainer.interior(),
                      labelpos='w',
                      label_text='Options: ',
                      menubutton_textvariable=self.var,
                      items=self.items.values(),
                      hull_borderwidth=1,
                      menubutton_width=20,
                      hull_relief='ridge')

    def _entryaccess(self):
        return int(control_parse.value_to_key(self.items,
                   self.entrymethod.getvalue())[0])

    def switch_requested_value(self, inputvalue):
        self.entrymethod.setvalue(self.items[str(int(float(inputvalue)))])
        print 'Done!'
