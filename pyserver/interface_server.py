import os
import shelve
import socket
import asyncore
import threading
import asynchat
from param import *
import daemonize
from logger import *
import login_interface
import user_interface
import amcp_interface
import mce_interface
import generic_interface


# manage transitions between modes, individual interfaces
class InterfaceSession(asynchat.async_chat):
    def __init__(self, server, sock):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\r\n")
        self.data = []
        self.name = None
        self.enter(login_interface.LoginPhase(server))

    def enter(self, interface):
        try:
            cur = self.interface
        except AttributeError:
            pass
        else:
            cur.remove(self)

        self.interface = interface
        interface.add(self)

    def collect_incoming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        line = ''.join(self.data)
        self.data = []

        try:
            self.interface.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
        self.enter(login_interface.LogoutPhase(self.server))


# start the server
class InterfaceServer(asyncore.dispatcher, threading.Thread):
    def __init__(self, port, name):
        threading.Thread.__init__(self)
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.name = name
        self.users = {}

        # make a local copy of the control database
        self.db = shelve.open(MASTER_SHELVE, "rw")

        # make an instance of the interface for each client
        self.client_interface = user_interface.ClientInterface(self)
        self.amcp_interface = amcp_interface.AmcpInterface(self)
        self.mce_interface = mce_interface.MCEInterface(self)
        self.generic_interface = generic_interface.GenericInterface(self)

    def handle_accept(self):
        connection, addr = self.accept()
        InterfaceSession(self, connection)

if __name__ == '__main__':
    if DAEMONIZE == 'yes':
        # fork this to be a daemon
        retCode = daemonize.Daemonize()
        pidfp = open("/var/run/interface_server.pid", "w")
        pidfp.write(repr(os.getpid()) + "\n")

    s = InterfaceServer(INTERFACE_PORT, NAME)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print 'interrupted'
