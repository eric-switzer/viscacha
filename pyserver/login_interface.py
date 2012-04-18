import command_interface
from logger import *
from param import *
from interfaces import *


# initial interface where the client logs in
class LoginPhase(command_interface.CommandInterface):
  def add(self, session):
    command_interface.CommandInterface.add(self,session)
    self.broadcast('InterfaceServer %s ready.' % self.server.name)

  def unknown(self,session,cmd):
    commentpush(session,'SERVER_AUTH',SERVER_TOKEN+'login <client_name> <interface_type> <control version number>')

  def do_login(self,session,line):
    chop = line.split()
    if len(chop) == 3:
      # parse the login string into the username, interface type and version control tag
      name = chop[0].strip()
      interface_type = chop[1].strip()
      version_tag = chop[2].strip()
      logline = 'attemped login user=%(name)s, interface_type=%(interface)s, version_tag=%(version)s' % \
                {'name': name, 'interface':interface_type, 'version': version_tag}
      silentlogpush('SERVER_AUTH', logline) 
      if name not in self.server.users:
        if version_tag == CONTROL_VERSION:
          # now the user is logged in, so attach to an interface
          session.name = name
          try:
            operations = interface_db.get(interface_type)
            operations['login'](session, self.server)
          except TypeError:
            commentpush(session,'SERVER_AUTH',SERVER_TOKEN+'no such interface category')
            raise EndSession
        else:
          commentpush(session,'SERVER_AUTH',SERVER_TOKEN+'error: bad version number')
          raise EndSession
      else:
        commentpush(session,'SERVER_AUTH',SERVER_TOKEN+'error: client %s is already logged in.' % name)
        raise EndSession
    else:
      commentpush(session,'SERVER_AUTH',SERVER_TOKEN+'error: bad client name/version tag')
      raise EndSession

# logout interface 
class LogoutPhase(command_interface.CommandInterface):
  def add(self,session):
    try: del self.server.users[session.name]
    except KeyError: pass
 
