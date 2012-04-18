import command_interface
from param import *
from logger import *
import control_parse

class MCEInterface(command_interface.CommandInterface):
  """ interface class for the MCE user
  """
  def add(self, session):
    self.server.users[session.name] = session
    command_interface.CommandInterface.add(self, session)

  def remove(self, session):
    command_interface.CommandInterface.remove(self,session)
    
  # override the command formatter to make 
  # MCE-specific commands
  def form_command(self, line):
    cmdstring = line.split(None)
    if len(cmdstring) != 2:
      do_human_put(self.session, 'malformed MCE command')
      return None
    else:
      cmdname = cmdstring[0]
      cmdval  = cmdstring[1]
      # REPORT to clients that the value is sent!
      return '%s,%s;' % (cmdname,cmdval)

  def do_clientput(self, session, line):
    self.server.client_interface.do_controldbput(session,line)
