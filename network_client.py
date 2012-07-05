import wx
import redis
import datetime
import shlex
import time
import threading
from wx.lib.pubsub import Publisher
import pyredis_monitor


def postmsg(msg):
    """Send to GUI"""
    (channel, command) = msg
    Publisher().sendMessage(channel, command)


class RedisSubscribe(threading.Thread):
    """Connect to redis and subscribe to a channel, wx-publishing msg"""
    def __init__(self, pool, client_id,
                 subname="commanding_ack"):
        """
        `pool`: the redis connection pool for this instance
        `client_id`: identifier that allows the server to send information
                to this specific client.
        `subname`: subscriber channel on the redis server for the thread
        """
        threading.Thread.__init__(self)
        self.pool = pool
        self.client_id = client_id
        self.subname = subname
        self.redis_conn = redis.Redis(connection_pool=self.pool)

        self.redis_pubsub = self.redis_conn.pubsub()
        # subscribe to both the general and specific client channels
        self.redis_pubsub.subscribe([subname, self.client_id])
        self.start()

    def run(self):
        # generator stops (killing thread) when no channels are subscribed
        for msg in self.redis_pubsub.listen():
            self.handle_msg(msg)

    def handle_msg(self, msg):
        r"""Do simple parsing of the message from the server"""
        if (msg['channel'] == self.client_id) or \
           (msg['channel'] == self.subname):
            # if the server tells the client to terminate its connection
            if msg['data'] == 'terminate':
                self.redis_pubsub.unsubscribe()
            else:
                try:
                    data = msg['data'].split()
                    if len(data) == 2:
                        channel = data[0]
                        value = data[1]

                    msg = (channel, value)

                    wx.CallAfter(postmsg, msg)
                except:
                    pass


class RedisMonitor(threading.Thread):
    """Connect to redis and get all published messages"""
    def __init__(self, pool, client_id):
        """
        `pool`: the redis connection pool for this instance
        `client_id`: identifier that allows the server to send information
                to this specific client.
        """
        threading.Thread.__init__(self)
        self.pool = pool
        self.client_id = client_id

        self.client = pyredis_monitor.Monitor(self.pool)
        self.client.monitor()
        self.start()

    def run(self):
        for msg in self.client.listen():
            if not self.handle_msg(msg):
                break

    def handle_msg(self, monitor_msg):
        ctime = monitor_msg['time']
        formatted = datetime.datetime.fromtimestamp(monitor_msg['time'])
        timestamp = formatted.strftime('%Y-%m-%d %H:%M')
        message = monitor_msg['command']
        message = " ".join(shlex.split(message))
        message_parse = message.split(" ")

        # if the server sends a termination signal to this client,
        # handle_message goes False and the thread dies
        if (message_parse[0].lower() == "publish") and \
           (message_parse[1] == self.client_id) and \
           (message_parse[2] == "terminate"):
            return False
        else:
            # ignore get requests (noise)
            if message_parse[0].lower() != "get":
                print "%s > %s" % (timestamp, message)

            # handle sets by pushing to the GUI
            if message_parse[0].lower() == "set":
                try:
                    if len(message_parse) == 3:
                        channel = message_parse[1]
                        value = message_parse[2]

                    msg = (channel, value)

                    wx.CallAfter(postmsg, msg)
                except:
                    pass

            return True
