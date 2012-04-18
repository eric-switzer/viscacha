import command_interface
from interfaces import *
from param import *
from logger import *
import control_parse

class AmcpInterface(command_interface.CommandInterface):
  """ interface class for the housekeeping user
  """
  def add(self, session):
    self.server.users[session.name] = session
    command_interface.CommandInterface.add(self, session)

  def remove(self, session):
    command_interface.CommandInterface.remove(self,session)
    
  # override the command formatter to make 
  # AMCP-specific commands
  def form_command(self, line):
    cmdstring = line.split(None)
    if len(cmdstring) != 2:
      do_human_put(self.session, 'malformed housekeeping command')
      return None
    else:
      cmdnum = int(float(control_parse.get_db_convert(MASTER_SHELVE,'short_name',cmdstring[0],'hwid')))
      cmdval = float(cmdstring[1])
      # REPORT to clients that the value is sent!
      return '%5d,%10.10f;' % (cmdnum,cmdval)

  # refresh method to grab all server values when amcp starts
  def do_refresh(self,session,line):
    db = shelve.open(MASTER_SHELVE,"r")
    for key in self.server.db.keys():
      try:
        rec = self.server.db[key]
        if 'amcp' in identification_db[rec['destination']]:
          cmdnum = int(float(control_parse.db_convert(db,'short_name',rec['short_name'], 'hwid')))
          cmdval = float(rec['default_val'])
          refresh_line = '%5d,%10.10f;' % (cmdnum,cmdval)
          #refresh_line = rec['short_name']+' '+repr(rec['default_val'])
          #write_to_destination(self.server,rec['destination'],refresh_line)
          commentpush(session,'SERVER_CMDOUT', refresh_line)
      except KeyError or TypeError:
        silentlogpush('SERVER_MESSAGE', 'control entry missing "short_name" entry')
    commentpush(session,'SERVER_CMDOUT', '-1,0;')

  def do_clientput(self, session, line):
    self.server.client_interface.do_controldbput(session,line)
