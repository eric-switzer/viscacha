import wx
from wx.lib.pubsub import Publisher
import input_value as vb
import input_onoff as ob


class CommandStatusIndicator(wx.Panel):
    """a box that indicates the success of a submitted command
    green: all commands received and acted on
    yellow: command send, waiting for ack
    red: ack received, but different value
    """

    def __init__(self, parent, name):
        wx.Panel.__init__(self, parent, size=(10, 10))
        self.Refresh()
        self.val_issued = None
        self.name = name

        # post a default message in case the wx pubsub is not working
        self.update(None)

        # create a pubsub receiver
        Publisher().subscribe(self.update, name + "/indicator")

    def update(self, msg):
        try:
            dataval = msg.data
            if dataval[0] == "issued":
                self.SetBackgroundColour("#ffff00")
                print "issued:", self.name, dataval[1]
                self.val_issued = dataval[1]

            if dataval[0] == "ack":
                print self.val_issued, dataval[1]
                # if the ack returns the command that was issued
                if dataval[1] == self.val_issued:
                    print "ack:", self.name, dataval[1]
                    self.SetBackgroundColour("#00ff00")
                else:
                    print "ack failed:", self.name, dataval[1]
                    self.SetBackgroundColour("ff00000")

        except AttributeError:
            self.SetBackgroundColour("#aaaaaa")


class SubsystemTab(wx.Panel):
    """set up a tabbed menu item for one subsystem
    the subsystem is indexed by `system_name`->`subsystem_name`
    """
    def __init__(self, parent, config, system_name,
                 subsystem_name, commanding, redis_conn):

        wx.Panel.__init__(self, parent)
        self.config = config

        # find the controllable variables in this subsystem
        self.variable_list = config.variable_list(system_name, subsystem_name)
        self.num_variable = len(self.variable_list)

        # find the order of the controls
        display_order = []
        for variable_item in self.variable_list:
            display_order.append(\
                self.config.configdb[variable_item]['displayorder'])

        self.variable_list = [var for (order, var) in \
                              sorted(zip(display_order, self.variable_list))]

        # add all the buttons to control variables in this subsystem tab
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.buttons = {}
        for (variable_item, idx) in \
            zip(self.variable_list, range(self.num_variable)):

            config_info = self.config.variable_dict(variable_item)
            if config_info['type'] == "input_value":
                self.buttons[variable_item] = vb.ButtonBarValue(self, -1,
                                    variable_item,
                                    config_info,
                                    commanding,
                                    redis_conn)

            if config_info['type'] == "input_onoff":
                self.buttons[variable_item] = ob.ButtonBarOnoff(self, -1,
                                    variable_item,
                                    config_info,
                                    commanding,
                                    redis_conn)

            # TODO: print error if type not recognized

            self.box.Add(self.buttons[variable_item], proportion=0,
                         flag=wx.ALIGN_TOP | wx.EXPAND)

        self.SetSizerAndFit(self.box)
        self.Centre()


class SystemFrame(wx.Frame):
    """build the full window describing contol of one system
    """
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

        windowsize = max(tab_sizes) + (100, 100)
        self.SetClientSize(windowsize)
        self.SendSizeEvent()

        self.sizer.Fit(self.nbpanel)
        self.Layout()
