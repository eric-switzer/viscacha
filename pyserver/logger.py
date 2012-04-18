import time
from param import *

# push a time-stammped string to the active session
def timepush(session,logtype,line):
  timestring = time.asctime(time.localtime())
  session.push(timestring+' '+line+'\r\n')
  write_log(logtype,timestring+' '+line+'\n')

# push a string to the active session, log
def commentpush(session,logtype,line):
  timestring = time.asctime(time.localtime())
  write_log(logtype,timestring+' '+line+'\n')
  session.push(line+'\r\n')

# push a statement to the log that is not pushed to 
# one of the session (this might be a command that the 
# user enters)
def silentlogpush(logtype,line):
  timestring = time.asctime(time.localtime())
  write_log(logtype,timestring+' '+line+'\n') 

def silentpush(session,line):
  session.push(line+'\r\n')

# command I/O logger for the interface layer
# call: 'write_log(TYPE, value)'
# currently the type is prepended to the line
# todo: add verbosity levels, other log files, treatments
def server_message(logfile, entry):
  if VERBOSITY >= 2:
    logfile.write('SERVER_MESSAGE: '+entry)
def server_cmdout(logfile, entry):
  if VERBOSITY >= 3:
    logfile.write('SERVER_CMDOUT:  '+entry)
def server_error(logfile, entry):
  logfile.write('SERVER_ERROR:  '+entry)
def server_auth(logfile, entry):
  if VERBOSITY >= 1:
    logfile.write('SERVER_AUTH:    '+entry)
def inbound(logfile, entry):
  if VERBOSITY >= 2:
    logfile.write('IN:             '+entry)
def outbound(logfile, entry):
  if VERBOSITY >= 2:
    logfile.write('OUT:            '+entry)

type_switch = {
  "SERVER_MESSAGE": server_message,
  "SERVER_CMDOUT": server_cmdout,
  "SERVER_ERROR": server_error,
  "SERVER_AUTH": server_auth,
  "IN": inbound,
  "OUT": outbound}

def write_log(logtype,entry):
   logfile = open(LOGFILE, 'a') 
   type_switch.get(logtype)(logfile,entry)
   logfile.close()
