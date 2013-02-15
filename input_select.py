import wx
from wx.lib.pubsub import Publisher
import client_gui as cg


class SelectIndicator():
    """This just waits for the ack and updates the command status indicator
    """
    def __init__(self, name):
        self.name = name

        # create a pubsub receiver
        Publisher().subscribe(self.update, name)

    def update(self, msg):
        try:
            dataval = msg.data
            issue_message = ("ack", dataval)
            Publisher().sendMessage(self.name + "/indicator", issue_message)
        except:
            print "Select indicator failed"


class SelectControlButton(wx.Panel):
    """a panel to publish command messages to redis
    """
    def __init__(self, parent, name, redis_conn, pubname="commanding"):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.name = name
        self.redis_conn = redis_conn
        self.pubname = pubname

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.box.Add(wx.Button(self, 1, "Run"),
                     proportion=0, flag=wx.ALIGN_LEFT)

        self.SetSizer(self.box)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.issue, id=1)

    def issue(self, event):
        command = "%s 1" % (self.name)

        self.redis_conn.publish(self.pubname, command)
        split_command = command.split(" ")
        issue_message = ("issued", " ".join(split_command[1:]))
        Publisher().sendMessage(self.name + "/indicator", issue_message)


class ButtonBarSelect(wx.Panel):
    """bar of buttons to control an on-off toggle quantity
    """
    def __init__(self, parent, identifier, name,
                 cmd_config, commanding, redis_conn):

        wx.Panel.__init__(self, parent, id=identifier, style=wx.RAISED_BORDER)
        self.SetBackgroundColour("#eee8d5")
        self.config = cmd_config
        self.desctext = wx.StaticText(self, -1, self.config['desc'])

        self.indicator = SelectIndicator(name)

        self.box = wx.BoxSizer(wx.HORIZONTAL)

        self.box.Add(self.desctext, proportion=1,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        # TODO swap this out with a toggle
        if commanding:
            self.issuecmd = SelectControlButton(self, name, redis_conn,
                                            pubname=self.config['destination'])

            self.box.Add(self.issuecmd,
                    proportion=0, flag=wx.ALIGN_RIGHT)

            self.status = cg.CommandStatusIndicator(self, name)
            self.box.Add(self.status, proportion=0,
                    flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(self.box)
        self.Centre()
