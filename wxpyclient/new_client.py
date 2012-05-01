import wx
import redis
import time
import network_client
import control_tabs
import control_parse
import master_config_parse
import log_panel
from threading import Thread
from wx.lib.pubsub import Publisher

# TODO:
# connection window with scrolling log
# connection window: File -> login info dialog, exit
# connection window: indicator for command send, and subscriber connection
# connection window: pull-down for system control windows
# connection window: manual log entry
# connection window: manual refresh
# connection window: clear log
# connection window: who is logged in?
# connection window: about client
# connection window: server lockout
# connection window: redis monitor in log window instead

#pagetabs[subsystem] = ControlGroupPage(nb, subsystem)
#class ControlGroupPage(wx.Panel):
#    def __init__(self, parent):
#        wx.Panel.__init__(self, parent)
#        t = wx.StaticText(self, -1, "text", (60,60))

if __name__ == "__main__":
    network_client.RedisConnection()
    configaddr = "http://www.cita.utoronto.ca/~eswitzer/master.json"
    config = master_config_parse.load_json_over_http(configaddr)
    print config
    print control_parse.find_groups(config, "system")

    app = wx.App()
    win = log_panel.LoggerFrame().Show()
    control_tabs.ControlTabs("Housekeeping").Show()
    app.MainLoop()
