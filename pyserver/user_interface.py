import command_interface
from logger import *
from param import *


class ClientInterface(command_interface.CommandInterface):
    """ interface class for a human user (either text or gui interface)
      possible commands:
      1. put - push a message to other users and the local log
      2. ping - check to see that the interface is up
      3. who/look - see what users/systems are logged in
      4. togglelock - toggle the global system control lock
      5. houseput - direct commands to AMCP
    """
    # add method for the human user client: broadcast a new user join
    def add(self, session):
        self.broadcast(SERVER_TOKEN + session.name + ' became active')
        self.server.users[session.name] = session
        command_interface.CommandInterface.add(self, session)

    def remove(self, session):
        self.broadcast(SERVER_TOKEN + session.name + ' became inactive')
        command_interface.CommandInterface.remove(self, session)

    def do_put(self, session, line):
        self.broadcast(session.name + ': ' + line)
