import wx
from wx.lib.pubsub import Publisher

class TextIndicator(wx.Panel):
    def __init__(self, parent, id, name):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.desctext = wx.StaticText(self, -1, name)
        self.parent = parent

        # create a pubsub receiver
        Publisher().subscribe(self.update, name)

    def update(self, msg):
        t = msg.data
        self.desctext.SetLabel(t)


class ButtonBase(wx.Panel):
    def __init__(self, parent, id, cmd_config, commanding, redis_conn):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.config = cmd_config
        self.redis_conn = redis_conn
        self.name = cmd_config['short_name']
        desctext = wx.StaticText(self, -1, self.config['desc'])
        indicator = TextIndicator(self, -1, self.name)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(desctext, proportion=1, flag=wx.ALIGN_LEFT)
        box.Add(indicator, proportion=0, flag=wx.ALIGN_LEFT)
        if commanding:
            box.Add(wx.Button(self, -1, 'Button3'), proportion=0, flag=wx.ALIGN_RIGHT)

        self.SetSizer(box)
        self.Centre()


class SubsystemTab(wx.Panel):
    def __init__(self, parent, config, system_name,
                 subsystem_name, commanding, redis_conn):

        self.config = config
        wx.Panel.__init__(self, parent)
        self.variable_list = config.variable_list(system_name, subsystem_name)
        num_variable = len(self.variable_list)

        box = wx.BoxSizer(wx.VERTICAL)
        for (variable_item, idx) in zip(self.variable_list, range(num_variable)):
            new_button = ButtonBase(self, -1,
                                    self.config.variable_dict(variable_item),
                                    commanding,
                                    redis_conn)

            box.Add(new_button, proportion=0, flag=wx.ALIGN_TOP|wx.EXPAND)

        self.SetSizerAndFit(box)
        self.Centre()


class SystemFrame(wx.Frame):
    def __init__(self, config, system_name, commanding, redis_conn):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=system_name)

        subsystem_list = config.subsystem_list(system_name)

        p = wx.Panel(self)
        nb = wx.Notebook(p)

        for subsystem in subsystem_list:
            nbpage = SubsystemTab(nb, config, system_name, subsystem,
                                  commanding, redis_conn)
            #staticbox = wx.StaticBox(nbpage, -1, subsystem)
            #sizer = wx.StaticBoxSizer(staticbox, wx.EXPAND)
            #nbpage.SetSizer(sizer)

            nb.AddPage(nbpage, subsystem)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 1, wx.EXPAND, 0)
        p.SetSizer(sizer)
        sizer.Fit(p)
        self.Layout()
