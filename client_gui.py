import wx
from wx.lib.pubsub import Publisher

class TextIndicator(wx.Panel):
    def __init__(self, parent, id, name):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.desctext = wx.StaticText(self, -1, name)

        # create a pubsub receiver
        Publisher().subscribe(self.update, "redis_incoming")

    def update(self, msg):
        t = msg.data
        #print t["data"], t["channel"]
        if isinstance(t, float):
            self.desctext.SetLabel(t)
        else:
            self.desctext.SetLabel("%s" % t)

class ButtonBase(wx.Panel):
    def __init__(self, parent, id, cmd_config):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.config = cmd_config
        desctext = wx.StaticText(self, -1, self.config['desc'])
        indicator = TextIndicator(self, -1, cmd_config['short_name'])

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(desctext, proportion=1, flag=wx.ALIGN_LEFT)
        box.Add(indicator, proportion=0, flag=wx.ALIGN_LEFT)
        box.Add(wx.Button(self, -1, 'Button3'), proportion=0, flag=wx.ALIGN_RIGHT)
        self.SetSizer(box)
        self.Centre()

class SubsystemTab(wx.Panel):
    def __init__(self, parent, config, system_name, subsystem_name):
        self.config = config
        wx.Panel.__init__(self, parent)
        self.command_list = config.command_list(system_name, subsystem_name)
        num_command = len(self.command_list)

        box = wx.BoxSizer(wx.VERTICAL)
        for (command_item, idx) in zip(self.command_list, range(num_command)):
            new_button = ButtonBase(self, -1,
                                    self.config.command_dict(command_item))

            box.Add(new_button, proportion=0, flag=wx.ALIGN_TOP|wx.EXPAND)

        self.SetSizerAndFit(box)
        self.Centre()


class SystemFrame(wx.Frame):
    def __init__(self, config, system_name, commanding):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=system_name)

        subsystem_list = config.subsystem_list(system_name)

        p = wx.Panel(self)
        nb = wx.Notebook(p)

        for subsystem in subsystem_list:
            nb.AddPage(SubsystemTab(nb, config, system_name, subsystem),
                       subsystem)

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)


