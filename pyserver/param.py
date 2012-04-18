import sys, os, shelve, string
import ConfigParser

#---------------------------------------------------------------------
# load the main configuration file
#---------------------------------------------------------------------
# first check the current directory, then /etc/
def LoadConfig(file, config={}):
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    if os.path.exists("./"+file):
      cp.read("./"+file)
    else:
      if os.path.exists("/etc/"+file):
        cp.read("/etc/"+file)
    for sec in cp.sections():
        name = string.lower(sec)
        for opt in cp.options(sec):
            config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
    return config

#---------------------------------------------------------------------
# return the version number string
#---------------------------------------------------------------------
def get_version(shelvefilename):
  print 'using variable database '+shelvefilename
  db = shelve.open(shelvefilename,"r")
  return db['version']['version']

# default configuration for the server
_ConfigDefault = {
    "server_settings.tcpip_port":'5005',
    "server_settings.name":"ACT_Command_Router_default",
    "server_settings.master_shelve":"/usr/src/python/excalibur/mbac_master.shelve",
    "server_settings.daemonize":"no",
    "server_settings.log_file":"/var/log/interface_server.log"
    }

configuration = LoadConfig("interface_server.conf", _ConfigDefault)
INTERFACE_PORT = int(configuration['server_settings.tcpip_port'])
SERVER_TOKEN = '> '
MASTER_SHELVE = configuration['server_settings.master_shelve']
CONTROL_VERSION = get_version(MASTER_SHELVE)
NAME = configuration['server_settings.name']+' Control version '
NAME = NAME+repr(CONTROL_VERSION)
DAEMONIZE = configuration['server_settings.daemonize']
LOGFILE = configuration['server_settings.log_file']
GUI_MESSAGE = 'gui_message'
try:
    VERBOSITY = int(configuration.get('server_settings.verbosity', 1))
except ValueError:
    VERBOSITY  = 1
    
# if client to interface_server logs off
class EndSession(Exception): pass

