import wx
from wx.lib.pubsub import Publisher


class TextIndicator(wx.Panel):
    def __init__(self, parent, name):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.indicator = wx.StaticText(self, -1, "-" * 10,
                                       style=wx.ALIGN_CENTER)
        self.name = name
        self.SetBackgroundColour("#fdf6e3")
        self.Refresh()

        # create a pubsub receiver
        Publisher().subscribe(self.update, name)

    def update(self, msg):
        value = "cur: %s" % repr(msg.data)
        self.indicator.SetLabel(value)


class TextControlButton(wx.Panel):
    def __init__(self, parent, name, redis_conn, pubname="commanding"):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.textentry = wx.TextCtrl(self, -1)
        self.name = name
        self.redis_conn = redis_conn
        self.pubname = pubname

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.box.Add(self.textentry, proportion=1, flag=wx.ALIGN_LEFT)
        self.box.Add(wx.Button(self, 1, 'Send'), proportion=0, flag=wx.ALIGN_LEFT)
        # TODO: add indicator

        self.SetSizer(self.box)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.issue, id=1)

    def issue(self, event):
        command = "%s %s" % (self.name, self.textentry.GetValue())
        self.redis_conn.publish(self.pubname, command)


class ButtonBase(wx.Panel):
    def __init__(self, parent, id, cmd_config, commanding, redis_conn):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.SetBackgroundColour("#eee8d5")
        self.config = cmd_config
        self.name = cmd_config['short_name']
        self.desctext = wx.StaticText(self, -1, self.config['desc'])
        self.indicator = TextIndicator(self, self.name)

        self.box = wx.BoxSizer(wx.HORIZONTAL)

        self.box.Add(self.desctext, proportion=1,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.box.Add(self.indicator, proportion=0,
                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        if commanding:
            issuecmd = TextControlButton(self, self.name, redis_conn)
            self.box.Add(issuecmd,
                    proportion=0, flag=wx.ALIGN_RIGHT)

        self.SetSizer(self.box)
        self.Centre()


class SubsystemTab(wx.Panel):
    def __init__(self, parent, config, system_name,
                 subsystem_name, commanding, redis_conn):

        wx.Panel.__init__(self, parent)
        self.config = config
        self.variable_list = config.variable_list(system_name, subsystem_name)
        self.num_variable = len(self.variable_list)

        # find the order of the controls
        # TODO can the db be natively ordered (JSON -> dict?) 
        display_order = []
        for variable_item in self.variable_list:
            display_order.append(\
                self.config.configdb[variable_item]['displayorder'])

        print display_order
        print self.variable_list
        self.variable_list = [var for (order, var) in \
                              sorted(zip(display_order, self.variable_list))]
        print self.variable_list

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.buttons = {}
        for (variable_item, idx) in \
            zip(self.variable_list, range(self.num_variable)):

            self.buttons[variable_item] = ButtonBase(self, -1,
                                    self.config.variable_dict(variable_item),
                                    commanding,
                                    redis_conn)

            self.box.Add(self.buttons[variable_item], proportion=0,
                         flag=wx.ALIGN_TOP | wx.EXPAND)

        self.SetSizerAndFit(self.box)
        self.Centre()


class SystemFrame(wx.Frame):
    def __init__(self, config, system_name, commanding, redis_conn):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=system_name)

        subsystem_list = config.subsystem_list(system_name)

        self.nbpanel = wx.Panel(self)
        self.tabset = wx.Notebook(self.nbpanel)
        self.tabset.SetBackgroundColour("#fdf6e3")

        self.nb_pages = {}
        tab_sizes = []
        for subsystem in subsystem_list:
            self.nb_pages[subsystem] = SubsystemTab(self.tabset, config,
                                                    system_name,
                                                    subsystem,
                                                    commanding, redis_conn)
            #staticbox = wx.StaticBox(nbpage, -1, subsystem)
            #sizer = wx.StaticBoxSizer(staticbox, wx.EXPAND)
            #nbpage.SetSizer(sizer)

            self.nb_pages[subsystem].SetInitialSize()
            tab_sizes.append(self.nb_pages[subsystem].GetSize())
            self.tabset.AddPage(self.nb_pages[subsystem], subsystem)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.tabset, 1, wx.EXPAND, 0)
        self.nbpanel.SetSizer(self.sizer)

        windowsize = max(tab_sizes) + (100,100)
        self.SetClientSize(windowsize)
        self.SendSizeEvent()

        self.sizer.Fit(self.nbpanel)
        self.Layout()
