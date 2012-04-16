#!/usr/bin/python
import getopt, sys
import Tkinter, Pmw
from param import *
import network_client
import random
##
# \namespace gci
# __main__ for the client
#

def main():
  # set the default values and the parse the command line 
  options = {'ARGV_SYSTEM':None, \
              'CLIENT_NAME':DEFAULT_CLIENT_NAME, \
              'ARGV_CMDLINE':None, \
              'SERVER_NAME':DEFAULT_SERVER_NAME, \
              'SERVER_PORT':DEFAULT_SERVER_PORT, \
              'ARGV_REFRESHRATE':None}
  
  parse_argv(sys.argv,options)
  rand =random.Random()

  # did the user request a single text-based command (no GUI)
  if options['ARGV_CMDLINE']:
    root = None
  else:
    root = Tkinter.Tk()

  client = network_client.ClientNetworkInterface(root, options)
  root.mainloop()

if __name__ == "__main__":
   main()
   #profile.run('main()','gciprof')



