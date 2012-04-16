import sys, time, shelve, threading, Queue
import Tkinter, Pmw
import socket, telnetlib
import interface
from param import *
##
# \namespace network_client
# Thread that connects to a server, spawns client interface

class ClientNetworkInterface:
  """------------------------------------------------------------------------------
     Network client class
     ------------------------------------------------------------------------------
     model: 
       Two threads sit on the open connection and listen for incoming messages and
       outgoing commands on a stack.  If there are incoming messages, push them
       to the Queue object, messagequeue.  If there are outgoing commands, pop them
       from the stack and send them to the server.
     methods:
       __init__: given the connection 'options', log in and check the connection
                 if the connection is good, then either start a GUI or process the 
                 command line to interact with the server
       connect: connect or reconnect to the server (in this case through telnet)
       disconnect: close up shop
       check_connection: ping the server after logged in to check for life
       listener: a function to check if there are new messages from the server
                 either called by periodicCall (using Tk's after), or by 
                 whileCall for the command line interface.
       workerPull/Push: threads that sit around pulling/pushing from the server
  """ 

  def __init__(self, parent, options):
    # set up the queues and start the GUI
    self.announce = 'ClientNetworkInterface: '
    self.options = options
    self.parent = parent
    self.db = shelve.open(MASTER_SHELVE,"r")
    self.versionnumber = '%s' % self.db['version']['version']
    self.messagequeue = Queue.Queue()
    self.commandqueue = Queue.Queue()

    print self.announce + 'instance initialized with host: '+self.options['SERVER_NAME']
    print self.announce + 'version: '+self.versionnumber
 
    # log on to the server, check connection
    self.connected = 0
    if self.connect():
      if not self.check_connection():
        print self.announce + 'instance has bad connection' 
        raise SystemExit
      else:
        # if the user is running from the shell, and only 
        # wants to send one command -- send it and log out
        # otherwise, start the full commanding GUI
        if self.options['ARGV_CMDLINE']:
          self.commandqueue.put(self.options['ARGV_CMDLINE'])
          self.commandqueue.put('logout')
        else: 
          self.gui = interface.MainInterface(parent, \
                                 self.options, \
                                 self.messagequeue, \
                                 self.commandqueue, \
                                 self.exitClient)

        # start the push/pull command threads
        self.thread1 = threading.Thread(target=self.workerPull)
        self.thread1.start()
        self.thread2 = threading.Thread(target=self.workerPush)
        self.thread2.start()
        # start the listener loop
        if parent == None:
          self.whileCall()
        else:
          self.periodicCall()
    else:   
      print self.announce + 'unable to connect'
      raise SystemExit

  # log on to the server
  def connect(self):
    if self.connected:
      print self.announce + 'instance is already connected'
      return 0
    else:
      try:
        self.tn = telnetlib.Telnet(self.options['SERVER_NAME'],self.options['SERVER_PORT'])  
        try:
          self.tn.read_until('ready')
          self.tn.write('login ' + self.options['CLIENT_NAME'] + " human " + self.versionnumber + "\r\n")
          response = self.tn.read_until('\r\n')
          response = self.tn.read_until('\r\n')
          if response.find('successful') != -1:
            print self.announce + 'login successful'
            self.connected = 1
            return 1
          else: 
            print self.announce + 'login failure'
            return 0
        except AttributeError:
          print self.announce + 'communication object failure'
      except socket.error:
        print self.announce + 'socket connection failure'
        return 0
 
  def check_connection(self):
    if self.connected:
      self.tn.write('ping\r\n')
      response = self.tn.read_some()
      #response =  self.tn.read_until('\r\n',timeout=None)
      #if response.rstrip() != '> alive':
      if response.find('alive') != -1:
        print self.announce + 'check_connection: connected'
        return 1
      else:
        print self.announce + 'check_connection: server side error no ping response'
        return 0
    else:
      print self.announce + 'client not connected'
      return 0

  def disconnect(self):
    self.tn.close()
    self.connected=0

  # listener loop
  def listener(self):
    # try to parse the incoming stream from the server
    # if it fails, just print it
    try:
      self.gui.IncomingStream()
    except AttributeError:
      while self.messagequeue.qsize():
        try:
          msg = self.messagequeue.get(0)
          print 'mangled incoming server message: ' + msg
        except Queue.Empty:
          pass
    if not self.connected:
      print self.announce + 'no longer connected, exiting'
      # wait for the threads to die
      time.sleep(0.5)
      self.tn.close()
      raise SystemExit

  # Tkinter provides the after 
  def periodicCall(self):
    self.listener()
    self.parent.after(10, self.periodicCall)

  # without Tkinter, juse use a time.sleep
  def whileCall(self):
    while 1:
      time.sleep(0.001)
      self.listener()

  # pull messages from the server, put them in message queue
  def workerPull(self):
    while self.connected:
      try:
        response =  self.tn.read_until('\r',timeout=1)
        response = response.strip()
      except EOFError:
        print self.announce + 'workerPull thread: disconnection'
        self.disconnect()
      try: 
        if not response == '':
          self.messagequeue.put(response)
      except UnboundLocalError:
        print 'Local connection unbound'

  # push commands in the command queue to the server
  def workerPush(self):
    while self.connected:
      time.sleep(0.1)
      try:
        cmd = self.commandqueue.get(0)
        self.tn.write(cmd+'\r\n')
      except Queue.Empty:
        pass

  def __del__(self):
    print self.announce + 'killed'
    if self.connected:
      self.disconnect()

  def exitClient(self):
    print self.announce + 'exit'
    if self.connected:
      self.disconnect()

