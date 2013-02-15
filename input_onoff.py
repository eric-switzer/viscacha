import wx
from wx.lib.pubsub import Publisher
import client_gui as cg


class OnoffIndicator(wx.Panel):
    """a panel that displays text on a subscribed wx channel with `name`
    to write text here, publish to the variable name
    """
    def __init__(self, parent, name):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER, size=(30, 30))

        self.name = name
        self.Refresh()

        # post a default message in case the wx pubsub is not working
        self.update(None)

        # create a pubsub receiver
        Publisher().subscribe(self.update, name)

    def update(self, msg):
        try:
            dataval = msg.data
            value = float(dataval.strip())

            if value:
                self.SetBackgroundColour("#00ff00")
            else:
                self.SetBackgroundColour("#000000")

            # whenever the value is updated, see if it corresponds to the last
            # commanded value
            issue_message = ("ack", dataval)
            Publisher().sendMessage(self.name + "/indicator", issue_message)
        except:
            self.SetBackgroundColour("#aaaaaa")


class OnoffControlButton(wx.Panel):
    """a panel to publish command messages to redis
    """
    def __init__(self, parent, name, redis_conn, pubname="commanding"):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.name = name
        self.redis_conn = redis_conn
        self.pubname = pubname

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.cb = wx.CheckBox(self, -1, 'Toggle', (10, 10))
        self.box.Add(self.cb, proportion=1, flag=wx.ALIGN_LEFT)
        #self.box.Add(wx.Button(self, 1, "Toggle"),
        #             proportion=0, flag=wx.ALIGN_LEFT)

        wx.EVT_CHECKBOX(self, self.cb.GetId(), self.issue)

        self.SetSizer(self.box)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.issue, id=1)

    def issue(self, event):
        if self.cb.GetValue():
            command = "%s 1" % (self.name)
        else:
            command = "%s 0" % (self.name)

        self.redis_conn.publish(self.pubname, command)
        split_command = command.split(" ")
        issue_message = ("issued", " ".join(split_command[1:]))
        Publisher().sendMessage(self.name + "/indicator", issue_message)


class ButtonBarOnoff(wx.Panel):
    """bar of buttons to control an on-off toggle quantity
    """
    def __init__(self, parent, identifier, name,
                 cmd_config, commanding, redis_conn):

        wx.Panel.__init__(self, parent, id=identifier, style=wx.RAISED_BORDER)
        self.SetBackgroundColour("#eee8d5")
        self.config = cmd_config
        self.desctext = wx.StaticText(self, -1, self.config['desc'])

        self.indicator = OnoffIndicator(self, name)

        self.box = wx.BoxSizer(wx.HORIZONTAL)

        self.box.Add(self.desctext, proportion=1,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.box.Add(self.indicator, proportion=0,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        # TODO swap this out with a toggle
        if commanding:
            self.issuecmd = OnoffControlButton(self, name, redis_conn,
                                            pubname=self.config['destination'])

            self.box.Add(self.issuecmd,
                    proportion=0, flag=wx.ALIGN_RIGHT)

            self.status = cg.CommandStatusIndicator(self, name)
            self.box.Add(self.status, proportion=0,
                    flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(self.box)
        self.Centre()
