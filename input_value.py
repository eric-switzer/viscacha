import wx
from wx.lib.pubsub import Publisher
import client_gui as cg


class TextIndicator(wx.Panel):
    """a panel that displays text on a subscribed wx channel with `name`
    to write text here, publish to the variable name
    """
    def __init__(self, parent, name):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        #self.indicator = wx.StaticText(self, -1, "-" * 10,
        #                               style=wx.ALIGN_CENTER)
        self.indicator = wx.TextCtrl(self,
                                    style=wx.TE_READONLY)

        self.name = name
        self.SetBackgroundColour("#fdf6e3")
        self.Refresh()

        # post a default message in case the wx pubsub is not working
        self.update(None)

        # create a pubsub receiver
        Publisher().subscribe(self.update, name)

    def update(self, msg):
        try:
            dataval = msg.data
            value = "cur: %s" % repr(dataval.strip())

            # whenever the value is updated, see if it corresponds to the last
            # commanded value
            issue_message = ("ack", dataval)
            Publisher().sendMessage(self.name + "/indicator", issue_message)
        except:
            value = "inactive"

        #self.indicator.SetLabel(value)
        self.indicator.SetValue(value)


class TextControlButton(wx.Panel):
    """a panel to publish command messages to redis
    """
    def __init__(self, parent, name, redis_conn, pubname="commanding"):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.textentry = wx.TextCtrl(self, -1)
        self.name = name
        self.redis_conn = redis_conn
        self.pubname = pubname

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.box.Add(self.textentry, proportion=1, flag=wx.ALIGN_LEFT)
        self.box.Add(wx.Button(self, 1, "Send"), proportion=0, flag=wx.ALIGN_LEFT)
        #self.box.Add(wx.Button(self, wx.ID_OK), proportion=0, flag=wx.ALIGN_LEFT)
        # TODO: add indicator

        self.SetSizer(self.box)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.issue, id=1)

    def issue(self, event):
        command = "%s %s" % (self.name, self.textentry.GetValue())
        self.redis_conn.publish(self.pubname, command)
        split_command = command.split(" ")
        issue_message = ("issued", " ".join(split_command[1:]))
        Publisher().sendMessage(self.name + "/indicator", issue_message)


class ButtonBarValue(wx.Panel):
    """A bar a buttons to control a variable's value
    current structure:
        fixed text field describing the variable
        an indicator of its current status
        a panel to issue commands to that variable
    """
    def __init__(self, parent, identifier, name, cmd_config, commanding, redis_conn):
        wx.Panel.__init__(self, parent, id=identifier, style=wx.RAISED_BORDER)
        self.SetBackgroundColour("#eee8d5")
        self.config = cmd_config
        self.desctext = wx.StaticText(self, -1, self.config['desc'])

        self.indicator = TextIndicator(self, name)
        self.box = wx.BoxSizer(wx.HORIZONTAL)

        self.box.Add(self.desctext, proportion=1,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.box.Add(self.indicator, proportion=0,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        if commanding:
            self.issuecmd = TextControlButton(self, name, redis_conn,
                                            pubname=self.config['destination'])
            self.box.Add(self.issuecmd,
                    proportion=0, flag=wx.ALIGN_RIGHT)

            self.status = cg.CommandStatusIndicator(self, name)
            self.box.Add(self.status, proportion=0,
                    flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(self.box)
        self.Centre()


