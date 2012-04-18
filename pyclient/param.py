import sys, getopt
import control_parse
import shelve
##
# \namepsace param
# Global parameters for the client
#

# server information
DEFAULT_SERVER_NAME = 'localhost'
DEFAULT_SERVER_PORT = 5005
DEFAULT_CLIENT_NAME = 'login_name'

# Some global interface parameters
GUI_MESSAGE = 'gui_message'
LOCKED = '#6699ff'
UNLOCKED = '#66CC00'
ON = '#66CC00'
OFF = '#6699ff'

# debugging messages
VERB_NO_MESSAGES = 0  # silent mode
VERB_ONLY_ERRORS = 1  # only serious errors
VERB_WARNINGS = 2     # warnings
VERB_EVERYTHING = 3   # all messages
VERBOSE_LEVEL = 10

# Directories and files
INSTALL_DIR = '/usr/src/python/excalibur/'
# for local installations
MASTER_SHELVE = 'mbac_master.shelve'
#MASTER_SHELVE = INSTALL_DIR+'mbac_master.shelve'
#MASTER_SHELVE = INSTALL_DIR+'ccam_master.shelve'

def usage():
  print 'GCIPy control client \n\n \
  command line arguments: \n \
  -s --system      [system name]   only pop up control windows for [system name] \n \
  -u --user        [user name]     login using [user name] \n \
  -n --nowindows   [command]       no windows, only issue [command] to the server \n \
  -l --servername  [server name]   log in to the interface server with [server name] \n \
  -p --serverport  [server port]   log in to the interface server on port [server port] \n \
  -v --verbose     [level]         silent=0, ++errors=1, ++warnings=2, ++everything else=3 \n \
  -r --refreshrate [refresh rate]  set the time between server refresh calls (not implemented yet) \n \
  -o --list                        list possible systems and exit \n \
  -h --help                        this help lising \n'

# define the command call options
COMMAND_LONGOPTS = ['system=', 'user=', 'nowindows=', 'servername=', \
                    'serverport=', 'verbose=', 'refreshrate=', 'list', 'help']

# parse the call options
def parse_argv(argvin, options):
  try:
    opts, args = getopt.getopt(argvin[1:], 's:u:n:l:p:v:r:moh', COMMAND_LONGOPTS)
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  for o, a in opts:
      if o in ('-s', '--system'):
        options['ARGV_SYSTEM'] = a
        print 'Opening only the '+a+' window'
      if o in ('-u', '--user'):
        options['CLIENT_NAME'] = a
      if o in ('-n', '--nowindows'):
        options['ARGV_CMDLINE'] = a
      if o in ('-l', '--servername'):
        options['SERVER_NAME'] = a
      if o in ('-p', '--serverport'):
        options['SERVER_PORT'] = a
      if o in ('-v', '--verbose'):
        options['VERBOSE_LEVEL'] = a
      if o in ('-r', '--refreshrate'):
        options['ARGV_REFRESHRATE'] = a
      if o in ('-o', '--list'):
        db = shelve.open(MASTER_SHELVE,"r")
        system_list = control_parse.find_groups(db,"system")
        print system_list
        sys.exit()
      if o in ('-h', '--help'):
        usage()
        sys.exit()

