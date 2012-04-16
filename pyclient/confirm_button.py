import Tkinter
import Pmw
PASSWORD='tough@ct'
##
# \namespace confirm_button
# Confirmation button class 
#

class ConfirmButton:
    def __init__(self, buttonrec, value):
        self.announce = 'ConfimButton: '
        self.level = buttonrec['confirm']
        self.desc = buttonrec['desc']
        self.value = value
        self.confirmed=0
        # general confirmation window
        self.confdialog = Pmw.MessageDialog(None,
            title = 'Confirmation Dialog',
            message_text = 'Change ' + self.desc + ' to ' + repr(self.value) + '?',
            buttonboxpos = 'e',
            iconpos = 'n',
            icon_bitmap = 'warning',
            buttons = ('Continue', 'Cancel'),
            command = self.execute,
            defaultbutton = 'Cancel')
        self.confdialog.iconname('Confirmation Dialog')
        self.confdialog.withdraw()
 
        # get a password
        self.password = Pmw.PromptDialog(None,
            title = 'Password confirmation',
            label_text = 'Password:',
            entryfield_labelpos = 'n',
            entry_show = '*',
            defaultbutton = 0,
            buttons = ('OK', 'Cancel'))
        self.password.withdraw()

        # soft confirmation dialog.
        self.confirm = Pmw.MessageDialog(
            title = 'Reconfirm',
            message_text = 'Change ' + self.desc + ' to ' + repr(self.value) + '?',
            defaultbutton = 0,
            buttons = ('OK', 'Cancel'))
        self.confirm.withdraw()
 
        self.confdialog.activate(geometry = 'first+100+100')

    def execute(self, result):
        if result is None or result == 'Cancel':
            self.confirmed = 0
            self.confdialog.deactivate(result)
        else:
            # no further confirmation is needed, go ahead
            if self.level == 0:
              self.confirmed = 1
              self.confdialog.deactivate() 

            # need soft confirmation
            if self.level == 1:
              result = self.confirm.activate(geometry = 'first+100+100')
              if result == 'OK':
                self.confirmed = 1
              else:
                self.confirmed = 0
              self.confdialog.deactivate()
  
            # get password confirmation
            if self.level == 2:
              result = self.password.activate(geometry = 'first+100+100')
              if result == 'OK':
                if self.password.get() == PASSWORD:
                  self.confirmed = 1
                else: 
                  print 'PASSWORD INCORRECT'
                  self.confirmed = 0
              else:
                self.confirmed = 0
              self.confdialog.deactivate()
