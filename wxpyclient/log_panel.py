import time
import os
import wx
import wx.stc as stc
import datetime
import shlex
from wx.lib.pubsub import Publisher


class Log(stc.StyledTextCtrl):
    def __init__(self, parent, style=wx.SIMPLE_BORDER):
        stc.StyledTextCtrl.__init__(self, parent, style=style)
        self._styles = [None]*32
        self._free = 1

    def getStyle(self, c='black'):
        """
        Returns a style for a given colour if one exists.  If no style
        exists for the colour, make a new style.
        If we run out of styles, (only 32 allowed here) we go to the top
        of the list and reuse previous styles.

        """
        free = self._free
        if c and isinstance(c, (str, unicode)):
            c = c.lower()
        else:
            c = 'black'

        try:
            style = self._styles.index(c)
            return style

        except ValueError:
            style = free
            self._styles[style] = c
            self.StyleSetForeground(style, wx.NamedColour(c))

            free += 1
            if free >31:
                free = 0
            self._free = free
            return style

    def write(self, text, c=None):
        """
        Add the text to the end of the control using colour c which
        should be suitable for feeding directly to wx.NamedColour.
        'text' should be a unicode string or contain only ascii data.
        """
        style = self.getStyle(c)
        lenText = len(text.encode('utf8'))
        end = self.GetLength()
        self.AddText(text)
        self.StartStyling(end, 31)
        self.SetStyling(lenText, style)
        self.EnsureCaretVisible()


    __call__ = write


class LogPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        self.colour = 'black'
        wx.Panel.__init__(self, parent, -1)

        self.SetBackgroundColour('gray')

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.Bind(wx.EVT_LEFT_DOWN, lambda e:self.OnMouse(e, 'Left'))
        self.Bind(wx.EVT_RIGHT_DOWN, lambda e:self.OnMouse(e, 'Right'))
        self.Bind(wx.EVT_MIDDLE_DOWN, lambda e:self.OnMouse(e, 'Middle'))

        for i in ('red', 'green', 'blue', 'cyan', 'magenta'):
            btn = wx.Button(self, -1, i)
            sizer.Add(btn, 1, wx.TOP|wx.BOTTOM, 15)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)

        self.SetSizer(sizer)
        Publisher().subscribe(self.updateDisplay, "redis_monitor")

    def updateDisplay(self, msg):
        #self.log('\nchannel=%s msg=%s' % (msg.topic[0], msg.data), "black")
        monitor_msg = msg.data
        ctime = monitor_msg['time']
        formatted = datetime.datetime.fromtimestamp(monitor_msg['time'])
        timestamp = formatted.strftime('%Y-%m-%d %H:%M')
        message = monitor_msg['command']
        message = " ".join(shlex.split(message))
        self.log("%s > %s\n" % (timestamp, message), "black")

    def OnMouse(self, event, type):
        self.log('\n%s Mouse Button Clicked'%type, self.colour)
        event.Skip()

    def OnButton(self, event):
        btn = event.GetEventObject()
        label = btn.GetLabel()
        self.colour = label
        self.log('\n%s button clicked'%label, label)
        event.Skip()


class LoggerFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Server log window')

        log = Log(self)
        tp = LogPanel(self, log)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tp, 0, wx.EXPAND)
        sizer.Add(log, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetSize((400, 300))

