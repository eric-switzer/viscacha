import wx
from wx.lib.pubsub import Publisher


class ButtonBase(wx.Panel):
    def __init__(self, parent, id, title):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, style=wx.RAISED_BORDER)
        self.SetBackgroundColour("Light Blue")

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(wx.Button(self, -1, 'Button1'), 1, wx.ALL, 5)
        box.Add(wx.Button(self, -1, 'Button2'), 0, wx.EXPAND)
        box.Add(wx.Button(self, -1, 'Button3'), 0, wx.ALIGN_CENTER)
        self.displayLbl = wx.StaticText(self, label="Amount of time since thread started goes here")
        box.Add(self.displayLbl)
        self.SetSizer(box)

        Publisher().subscribe(self.updateDisplay, "redis_incoming")

    def updateDisplay(self, msg):
        """
        Receives data from thread and updates the display
        """
        t = msg.data
        if isinstance(t, int):
            self.displayLbl.SetLabel("Time since thread started: %s seconds" % t)
        else:
            self.displayLbl.SetLabel("%s" % t)

