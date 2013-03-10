"""A wxpython GUI for commanding/monitoring through a redis intermediary"""
import os
import wx
import redis
import time
import network_client
import control_parse
import client_gui
from wx.lib.pubsub import Publisher
from optparse import OptionParser


class MainWindow(wx.Frame):
    r"""This is the main window for the client and spawns all other processes
    and windows
    TODO: remove parent=None, id=-1 option?
    """
    def __init__(self, configaddr, server, port, parent=None, id=-1):
        # start the redis server connection
        self.pool = redis.ConnectionPool(host=server, port=port, db=0)
        self.redis_conn = redis.Redis(connection_pool=self.pool)

        # get the JSON configuration file
        self.config = control_parse.ControlSpec(configaddr=configaddr,
                                                silent=False,
                                                redis_conn=self.redis_conn)

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
                                                    subname="commanding_ack")

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
        r"""Put buttons on the main server window"""
        sizer = wx.GridBagSizer(3, 2)

        # Issue a command to grab all the current variable states.
        sizer.Add(wx.Button(self.panel, 1, 'Refresh'),
                  (0, 0), (1, 1), wx.EXPAND)

        # See which GUI clients are connected to the server
        sizer.Add(wx.Button(self.panel, 2, 'Who'),
                  (0, 1), (1, 1), wx.EXPAND)

        # Enter a comment in the logfile
        sizer.Add(wx.Button(self.panel, 3, 'Send comment'),
                  (0, 2), (1, 1), wx.EXPAND)

        self.log_entry = wx.TextCtrl(self)
        sizer.Add(self.log_entry, (1, 0), (1, 3), wx.EXPAND)
        self.SetSizerAndFit(sizer)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.on_refresh, id=1)
        self.Bind(wx.EVT_BUTTON, self.on_who, id=2)
        self.Bind(wx.EVT_BUTTON, self.on_log, id=3)

    def build_menu(self):
        r"""Build the menu bar (file and command/monitor windows)"""
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        monitormenu = wx.Menu()
        commandmenu = wx.Menu()

        filemenu.AppendSeparator()
        quit_item = wx.MenuItem(filemenu, 100, '&Quit\tCtrl+Q',
                           'Quit the Application')

        filemenu.AppendItem(quit_item)

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
            commandmenu.AppendItem(wx.MenuItem(commandmenu, sys_num + 1,
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
        r"""shutdown connections and leave the client"""
        self.redis_conn.publish(self.client_id, "terminate")
        # wait for the threads to die before disconnecting
        time.sleep(0.1)
        # un-register this client connection and disconnect
        self.redis_conn.lrem("gui_clients", self.client_id, 1)
        self.pool.disconnect()
        # now close the GUI
        self.Close()

    def on_cmdwindow(self, event):
        r"""open a new commanding/monitor window from the menu bar"""
        (system_name, commanding) = tuple(self.event_dispatch[event.GetId()])
        sysframe = client_gui.SystemFrame(self.config, system_name,
                                          commanding, self.redis_conn)

        sysframe.Show(True)
        # now push current values to all of the clients
        self.on_refresh(0)

    def on_refresh(self, event):
        r"""Issue a pipelined stack of 'get's to redis to find all variable
        states on the server"""

        print "GUI: refreshing all variables relative to the server"
        pipe = self.redis_conn.pipeline()
        varlist = []

        for sys_variable in self.config.all_variables():
            varlist.append(sys_variable)
            pipe.get(sys_variable)

        values = pipe.execute()
        for (varname, val) in zip(varlist, values):
            if val is not None:
                # this does not need wx.CallAfter
                Publisher().sendMessage(varname, val)
            else:
                print "%s unknown on server; setting to default" % varname
                # TODO: fix this; also wxpublish the value
                #self.redis_conn.set(self.name, cmd_config['default'])

    def on_who(self, event):
        r"""List clients connected to the server"""
        print self.redis_conn.lrange("gui_clients", 0, -1)

    def on_log(self, event):
        r"""Submit a log entry"""
        message = self.log_entry.GetValue()
        self.redis_conn.publish("log", message)


if __name__ == "__main__":
    r"""main command-line interface"""
    parser = OptionParser(usage="usage: %prog [options] json_url",
                          version="%prog 1.0")

    parser.add_option("-s", "--server",
                      action="store",
                      dest="server",
                      default="localhost",
                      help="Redis host")

    parser.add_option("-p", "--port",
                      action="store",
                      dest="port",
                      default="6379",
                      help="Redis host port")

    (options, args) = parser.parse_args()
    optdict = vars(options)

    if len(args) != 1:
        #parser.error("no JSON url given; using dummy")
        print "no JSON url given; using dummy"
        jsonfile = "redis://command_specification"
    else:
        jsonfile = args[0]

    print "connecting to %s:%s" % (optdict['server'], optdict['port'])
    print "based on JSON URL: %s" % jsonfile

    client_app = wx.App()
    main_win = MainWindow(jsonfile, optdict['server'], int(optdict['port']))
    main_win.Show(True)
    client_app.SetTopWindow(main_win)
    #control_tabs.ControlTabs("Housekeeping").Show()
    client_app.MainLoop()
