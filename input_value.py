import wx
from wx.lib.pubsub import Publisher
import client_gui as cg


class ValueIndicator(wx.Panel):
    """a panel that displays text on a subscribed wx channel with `name`
    to write text here, publish to the variable name
    """
    def __init__(self, parent, name, units=""):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.indicator = wx.StaticText(self, -1, "-" * 10,
                                       style=wx.ALIGN_CENTER)
        #self.indicator = wx.TextCtrl(self,
        #                            style=wx.TE_READONLY)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.indicator, 1)
        self.SetSizer(self.sizer)
        self.Layout()

        self.name = name
        self.units = units
        self.SetBackgroundColour("#fdf6e3")
        self.Refresh()

        # post a default message in case the wx pubsub is not working
        self.update(None)

        # create a pubsub receiver
        Publisher().subscribe(self.update, name)

    def update(self, msg):
        try:
            dataval = msg.data
            value = "cur: %s %s" % (dataval.strip(), self.units)

            # whenever the value is updated, see if it corresponds to the last
            # commanded value
            issue_message = ("ack", dataval)
            Publisher().sendMessage(self.name + "/indicator", issue_message)
        except:
            value = "inactive"

        self.indicator.SetLabel(value)
        #self.indicator.SetValue(value)


class ValueControlButton(wx.Panel):
    """a panel to publish command messages to redis
    """
    def __init__(self, parent, name, redis_conn,
                 pubname="commanding", confirm=False, var_range=None):

        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.textentry = wx.TextCtrl(self, -1)
        self.name = name
        self.redis_conn = redis_conn
        self.pubname = pubname
        self.confirm = confirm
        self.var_range = var_range

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.box.Add(self.textentry, proportion=1, flag=wx.ALIGN_LEFT)
        self.box.Add(wx.Button(self, 1, "Send"),
                     proportion=0, flag=wx.ALIGN_LEFT)

        self.SetSizer(self.box)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.issue, id=1)

    # TODO: may choose to force types with e.g. getattr(__builtin__,'int')
    def issue(self, event):
        # if confirmation is required
        if self.confirm:
            dlg = wx.MessageDialog(self,
                "Do you really want to perform this action?",
                "Confirm", wx.OK | wx.CANCEL | wx.ICON_QUESTION)

            result = dlg.ShowModal()
        else:
            result = wx.ID_OK

        # if the range needs to be checked
        if self.var_range is not None:
            val_safe = False
            try:
                value = float(self.textentry.GetValue())
                if ((value <= self.var_range[1]) and \
                    (value >= self.var_range[0])):
                    val_safe = True
                else:
                    print value, "out of range", self.var_range
            except ValueError:
                value = self.textentry.GetValue()
                print "unable to interpret as float:", value
        else:
            value = self.textentry.GetValue()
            val_safe = True

        if result == wx.ID_OK and val_safe:
            command = "%s %s" % (self.name, value)
            self.redis_conn.publish(self.pubname, command)
            split_command = command.split(" ")
            issue_message = ("issued", " ".join(split_command[1:]))
            Publisher().sendMessage(self.name + "/indicator", issue_message)
        else:
            print "operation cancelled"


class ButtonBarValue(wx.Panel):
    """A bar a buttons to control a variable's value
    current structure:
        fixed text field describing the variable
        an indicator of its current status
        a panel to issue commands to that variable
    """
    def __init__(self, parent, identifier, name,
                cmd_config, commanding, redis_conn):
        wx.Panel.__init__(self, parent, id=identifier, style=wx.RAISED_BORDER)
        self.SetBackgroundColour("#eee8d5")
        self.config = cmd_config
        self.desctext = wx.StaticText(self, -1, self.config['desc'])

        self.indicator = ValueIndicator(self, name,
                                        units=self.config['units'])

        self.box = wx.BoxSizer(wx.HORIZONTAL)

        self.box.Add(self.desctext, proportion=1,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.box.Add(self.indicator, proportion=0,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        if commanding:
            try:
                var_range = self.config['minmax']
            except:
                var_range = None

            self.issuecmd = ValueControlButton(self, name, redis_conn,
                                            pubname=self.config['destination'],
                                            confirm=self.config['confirm'],
                                            var_range=var_range)

            self.box.Add(self.issuecmd,
                    proportion=0, flag=wx.ALIGN_RIGHT)

            self.status = cg.CommandStatusIndicator(self, name)
            self.box.Add(self.status, proportion=0,
                    flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(self.box)
        self.Centre()
