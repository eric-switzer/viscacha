import os
import wx
import redis
import time
import network_client
import control_tabs
import control_parse
from threading import Thread
from wx.lib.pubsub import Publisher


class MainWindow(wx.Frame):
    r"""This is the main window for the client and spawns all other processes
    and windows
    TODO: remove parent=None, id=-1 option?
    """
    def __init__(self, parent=None, id=-1):
        # get the JSON configuration file
        configaddr = "http://www.cita.utoronto.ca/~eswitzer/master.json"
        self.config = control_parse.ControlSpec(configaddr)

        # start the redis server connection
        self.pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
        self.redis_conn = redis.Redis(connection_pool=self.pool)

        # client IDs are a random string for this instance
        self.client_id = "client_" + ''.join('%02x' % ord(x) for
                                             x in os.urandom(16))

        print "starting new client instance: " + self.client_id
        self.redis_conn.lpush("gui_clients", self.client_id)

        self.server_info = self.redis_conn.info()
        print "number of clients connected: %d" % \
              self.server_info['connected_clients']

        # start a subscription for this client to receive messages from redis
        self.acksub = network_client.RedisSubscribe(self.pool, self.client_id,
                                                 subname="housekeeping_ack",
                                                 pubchan="redis_incoming")

        # start a thread which simply runs redis "monitor" and prints the text
        self.redmon = network_client.RedisMonitor(self.pool, self.client_id)

        self.event_dispatch = {}
        wx.Frame.__init__(self, parent, id, "Command Window",
                          wx.DefaultPosition, wx.Size(600, 150))
                          #style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER )
        self.panel = wx.Panel(self, id=wx.ID_ANY)

        self.build_menu()
        self.build_buttons()

    def build_buttons(self):
        sizer = wx.GridBagSizer(3, 2)
        sizer.Add(wx.Button(self.panel, -1, 'Refresh'), (0,0), (1,1), wx.EXPAND)
        sizer.Add(wx.Button(self.panel, -1, 'Who'), (0,1), (1,1), wx.EXPAND)
        sizer.Add(wx.Button(self.panel, -1, 'Send comment'), (0,2), (1,1), wx.EXPAND)
        sizer.Add(wx.TextCtrl(self), (1,0), (1,3), wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.Centre()

    def build_menu(self):
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        monitormenu = wx.Menu()
        commandmenu = wx.Menu()

        filemenu.AppendSeparator()
        quit = wx.MenuItem(filemenu, 100, '&Quit\tCtrl+Q',
                           'Quit the Application')

        filemenu.AppendItem(quit)

        n_systems = len(self.config.system_list())
        for (system_item, sys_num) in zip(self.config.system_list(),
                                          range(101, 101 + 2 * n_systems, 2)):

            self.event_dispatch[sys_num] = [system_item, False]
            self.event_dispatch[sys_num + 1] = [system_item, True]
            menudesc = "Open monitor-only window for %s" % system_item
            monitormenu.AppendItem(wx.MenuItem(monitormenu, sys_num,
                                               '&%s' % system_item,
                                                menudesc))

            menudesc = "Open commanding window for %s" % system_item
            commandmenu.AppendItem(wx.MenuItem(commandmenu, sys_num+1,
                                               '&%s' % system_item,
                                                menudesc))

            self.Bind(wx.EVT_MENU, self.on_cmdwindow, id=sys_num)
            self.Bind(wx.EVT_MENU, self.on_cmdwindow, id=sys_num + 1)

        menubar.Append(filemenu, '&File')
        menubar.Append(monitormenu, '&Monitor')
        menubar.Append(commandmenu, '&Command')

        self.SetMenuBar(menubar)
        self.CreateStatusBar()

        self.Bind(wx.EVT_MENU, self.on_quit, id=100)

    def on_quit(self, event):
        self.redis_conn.publish(self.client_id, "terminate")
        # wait for the threads to die before disconnecting
        time.sleep(0.1)
        self.redis_conn.lrem("gui_clients", self.client_id, 1)
        self.pool.disconnect()
        self.Close()

    def on_cmdwindow(self, event):
        print self.event_dispatch[event.GetId()]


if __name__ == "__main__":
    app = wx.App()
    win = MainWindow().Show(True)
    #control_tabs.ControlTabs("Housekeeping").Show()
    app.MainLoop()
