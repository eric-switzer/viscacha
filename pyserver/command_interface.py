import control_parse
from param import *
from logger import *
from interfaces import *

class CommandHandler:
  """ interpret commands from the client """
  def unknown(self, session, cmd):
    commentpush(session, 'SERVER_MESSAGE', 'Unknown command: %s' % cmd)

  def handle(self, session, line):
    if not line.strip(): return
    silentlogpush('IN', line)  
    parts = line.split(' ',1)
    cmd = parts[0]
    try: line = parts[1].strip()
    except IndexError: line = ''
    method = getattr(self, 'do_'+cmd, None)
    if callable(method):
      method(session,line)
    else:
      self.unknown(session,cmd)

class CommandInterface(CommandHandler):
  """------------------------------------------------------------------------------
     Session base class
     ------------------------------------------------------------------------------
     model: methods prefixed with 'do_' are available as commands to the user 
        ***session methods:
     1. do_logout/add/remove internal methods that handle login/logout requests
     2. do_who  - print list of all users logged in
     3. look_list - return a list of users with the same interface category
     3. do_look - list of users logged in to the user's interface category
     4. do_ping - test the connection for life
        ***output methods:
     1. broadcast - broadcast message to all users in the user's interface 
        category
     2. sendcmd - bare-bones method to write commands to the users 
        (called externally)
        ***constraint methods:
     1. do_logglelock - turn the session lock on/off for all users logged in to 
        that users's interface category.
     2. do_identify - allows a client to identify with a particular command 
        destination
     3. do_print_ids - print the client/destination binding table
     4. flush_id - remove all destination bindings of the current user
        ***inter-client communication
     1. uput : clients in one category to talk to any other client
     2. tput : clients in one category to send to message to everyone in another
        category
     3. dput : clients in one category send to anyone on the server identifying 
        with a particular destination flag
     4. lput : clients broadcast a log message, which is ignored if the log
        client is not present.

     example commands (including login):
     login guest_user human 20060724170856
     uput  machine_client   short_name command 
     tput  machine_category short_name command 
     dput  destination_flag short_name command
     lput  log_name log_message
  """
  def __init__(self,server):
    self.server = server
    self.sessions = []
    self.lockcontrols = 0

  #------------------------------------------------------------------------------
  # session methods
  #------------------------------------------------------------------------------
  # bare bones methods for logging in/out of a session
  def add(self, session):
    self.sessions.append(session)

  def remove(self,session):
    self.sessions.remove(session)

  def do_logout(self, session, line):
    self.do_flush_id(session,line)
    raise EndSession

  def do_who(self, session, line):
    outstring = SERVER_TOKEN
    for name in self.server.users:
      outstring = outstring + ' ' + name
    commentpush(session, 'SERVER_MESSAGE', outstring)

  def look_list(self):
    output = []
    for object in self.sessions:
      output.append(object.name)
    return output

  def do_look(self,session,line):
    outstring = SERVER_TOKEN
    for other in self.sessions:
      outstring = outstring + ' ' + other.name
    commentpush(session, 'SERVER_MESSAGE', outstring)

  def do_ping(self,session,line):
    commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN+'alive')

  #------------------------------------------------------------------------------
  # TX methods
  #------------------------------------------------------------------------------
  def broadcast(self, line):
    for session in self.sessions:
      timepush(session,'SERVER_MESSAGE',line)
      #session.push(line)

  # override this method to make more specific command calls to a client
  def form_command(self, line):
    return line

  def sendcmd_all(self, line):
    for session in self.sessions:
      if self.form_command(line) != None:
        commentpush(session,'SERVER_CMDOUT', self.form_command(line))

  def sendcmd_user(self, user, line):
    for session in self.sessions:
      if session.name == user:
        if self.form_command(line) != None:
          commentpush(session,'SERVER_CMDOUT', self.form_command(line))

  #------------------------------------------------------------------------------
  # constraint, identification methods
  #------------------------------------------------------------------------------
  def do_togglelock(self,session,line):
    if self.lockcontrols:
      self.lockcontrols = 0 
      self.broadcast(SERVER_TOKEN + session.name + ' UNLOCKED session controls')  
    else:
      self.lockcontrols = 1  
      self.broadcast(SERVER_TOKEN + session.name + ' LOCKED session controls') 

  # print the current identification table
  def do_print_ids(self, session, line):
    commentpush(session,'SERVER_MESSAGE', repr(identification_db))

  # flush a user from the id table
  def do_flush_id(self, session, line):
    flush_identity(session.name)

  # identify one's self as a particular destination
  # eg: identify hk_bbc -- will identify the current user with messages 
  # destined for the bbc
  def do_identify(self, session, line):
    add_identity(line, session.name)

  #------------------------------------------------------------------------------
  # control data-base methods
  #------------------------------------------------------------------------------
  # if one of the devices wants to reply to the user with updated 
  # values, the device client issues 'controldbput'.  Here, if the 
  # command is a reply to a change request, then the global control 
  # database is updated with the new value.  This way, if the client 
  # logs off, they can log back in and refresh their local values 
  # based on the persistent database on the server.
  def do_controldbput(self,session,line):
    refresh_string = line.split()
    short_name = refresh_string[0]
    refresh_type = refresh_string[1]
    refresh_val = refresh_string[2]
    if refresh_type == 'value' or refresh_type == 'reply':
      if short_name in self.server.db.keys():
        rec = self.server.db[short_name]
        variable_type = control_parse.find_controltype(rec['type'], MASTER_SHELVE)
        rec['default_val'] = control_parse.control_typecast(refresh_val,variable_type)
        self.server.db[short_name] = rec
        silentlogpush('SERVER_MESSAGE','ClientInterface: changed '+short_name+' to '+refresh_val)
        self.do_human_put(session, 'gui_message ' + short_name + ' ' + refresh_type + ' '+refresh_val)
      else:
        silentlogpush('SERVER_MESSAGE','command_interface: bad db short name')

  # this call needs more work to make it specific to clients:
  # it spits back the entire control database
  def do_refresh(self,session,line):
   for key in self.server.db.keys():
     try:
       rec = self.server.db[key]
       outstring = 'gui_message '+ rec['short_name']
       outstring = outstring + ' value ' + repr(rec['default_val'])
       silentpush(session, outstring) 
     except KeyError or TypeError:
       silentlogpush('SERVER_MESSAGE', 'control entry missing "short_name" entry')
  

  #------------------------------------------------------------------------------
  # inter-client message methods
  #------------------------------------------------------------------------------
  # UPUT: send a command to a named client
  def do_uput_verbose(self, session, line):
    self.uput(session, line, False)
  def do_uput(self, session, line):
    self.uput(session, line, True)
  def uput(self, session, line, silent):
    cmdstring = line.split(None)
    if len(cmdstring) == 3:
      # parse the incoming line
      user = cmdstring[0]
      short_name = cmdstring[1]
      command_value = cmdstring[2]
      if not self.lockcontrols:
        if user in self.server.users:
          logline = 'uput request to user=%(user)s, \
                    short_name=%(short_name)s, command_value=%(command_value)s' % \
                    {'user':user, 'short_name':short_name, \
                     'command_value':command_value }
          if silent == True:
            silentlogpush('SERVER_MESSAGE', SERVER_TOKEN+logline)
          else:
            silentlogpush('SERVER_MESSAGE', SERVER_TOKEN+logline)
            self.broadcast(SERVER_TOKEN + session.name + \
              ' changed ' + repr(control_parse.get_db_convert(MASTER_SHELVE, 'short_name', short_name, 'desc')) + \
              ' to ' + repr(command_value))
          # commit the request to only that user
          write_to_user(self.server, user, short_name + ' ' + command_value)
        else:
          commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN+user+' is not connected to the interface server')
      else:
        commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN + 'SESSION IS LOCKED') 
    else:
      commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN + 'uput: bad number of arguments')

  # TPUT: send a command to call clients of a given type
  def do_tput_verbose(self, session, line):
    self.tput(session, line, False)
  def do_tput(self, session, line):
    self.tput(session, line, True)
  def tput(self, session, line, silent):
    cmdstring = line.split(None)
    if len(cmdstring) == 3:
      # parse the incoming line
      interface_type = cmdstring[0]
      short_name = cmdstring[1]
      command_value = cmdstring[2]
      if not self.lockcontrols:
        logline = 'tput request to interface_type=%(interface_type)s, \
                  short_name=%(short_name)s, command_value=%(command_value)s' % \
                  {'interface_type':interface_type, 'short_name':short_name, \
                   'command_value':command_value }
        if silent == True:
          silentlogpush('SERVER_MESSAGE', SERVER_TOKEN+logline)
        else:
          silentlogpush('SERVER_MESSAGE', SERVER_TOKEN+logline)
          self.broadcast(SERVER_TOKEN + session.name + \
            ' changed ' + repr(control_parse.get_db_convert(MASTER_SHELVE, 'short_name', short_name, 'desc')) + \
            ' to ' + repr(command_value))
        # commit the request to all users of that interface type
        write_to_all(self.server, interface_type, short_name + ' ' + command_value)
      else:
        commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN + 'SESSION IS LOCKED') 
    else:
      commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN + 'tput: bad number of arguments')

  # DPUT: send a message to destinations that have identified themselves
  def do_dput_verbose(self, session, line):
    self.dput(session, line, False)
  def do_dput(self, session, line):
    self.dput(session, line, True)
  def dput(self, session, line, silent):
    cmdstring = line.split(None)
    if len(cmdstring) != 4:
      # parse the incoming line
      destination = cmdstring[0]
      short_name = cmdstring[1]
      command_value = cmdstring[2]
      if not self.lockcontrols:
        if check_destination(destination):
          logline = 'dput request to destination=%(destination)s, \
                    short_name=%(short_name)s, command_value=%(command_value)s' % \
                    {'destination':destination, 'short_name':short_name, \
                     'command_value':command_value }
          if silent == True:
            silentlogpush('SERVER_MESSAGE', SERVER_TOKEN+logline)
          else:
            silentlogpush('SERVER_MESSAGE', SERVER_TOKEN+logline)
            self.broadcast(SERVER_TOKEN + session.name + \
              ' changed ' + repr(control_parse.get_db_convert(MASTER_SHELVE, 'short_name', short_name, 'desc')) + \
              ' to ' + repr(command_value))
          # commit the request to all users of that interface type
          write_to_destination(self.server, destination, short_name + ' ' + command_value)
        else:
          commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN+destination+' is not bound to any clients')
      else:
        commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN + 'SESSION IS LOCKED') 
    else:
      commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN + 'dput: bad number of arguments')
      
  # LPUT: send a message to a logger; if there is no logger client, the message
  # is ignored.
  def do_lput(self, session, line):
    self.lput(session, line, True)
  def lput(self, session, line, silent):
    cmdstring = line.split(None)
    if len(cmdstring) >= 2:
      # parse the incoming line
      if not self.lockcontrols:
        if check_destination('logger'):
          # commit the request to all users of that interface type
          write_to_destination(self.server, 'logger', line)
    else:
      commentpush(session,'SERVER_MESSAGE',SERVER_TOKEN + 'lput: bad number of arguments')

  # regardless of the client, write a message to all human operators
  def do_human_put(self, session, line):
    write_to_all(self.server, 'human', line)

