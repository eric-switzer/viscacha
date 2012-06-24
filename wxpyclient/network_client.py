import wx
import redis
import datetime
import shlex
import time
import threading
from wx.lib.pubsub import Publisher
import pyredis_monitor


class RedisSubscribe(threading.Thread):
    """Connect to redis and subscribe to a channel, wx-publishing msg"""
    def __init__(self, pool, client_id,
                 subname="housekeeping_ack",
                 pubchan="redis_incoming"):
        """
        `pool`: the redis connection pool for this instance
        `client_id`: identifier that allows the server to send information
                to this specific client.
        `subname`: subscriber channel on the redis server for the thread
        `pubchan`: publisher channel within wxwindows for GUI events
        """
        threading.Thread.__init__(self)
        self.pool = pool
        self.client_id = client_id
        self.redis_conn = redis.Redis(connection_pool=self.pool)

        self.redis_pubsub = self.redis_conn.pubsub()
        # subscribe to both the general and specific client channels
        self.redis_pubsub.subscribe([subname, self.client_id])
        self.pubchan = pubchan
        self.start()

    def run(self):
        # generator stops (killing thread) when no channels are subscribed
        for msg in self.redis_pubsub.listen():
            self.handle_msg(msg)

    def handle_msg(self, msg):
        if msg['channel'] == self.client_id:
            # if the server tells the client to terminate its connection
            if msg['data'] == 'terminate':
                self.redis_pubsub.unsubscribe()
            else:
                wx.CallAfter(self.postmsg, msg)

    def postmsg(self, msg):
        """Send time to GUI"""
        Publisher().sendMessage(self.pubchan, msg)


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
        if (message_parse[0] == "PUBLISH") and \
           (message_parse[1] == self.client_id) and \
           (message_parse[2] == "terminate"):
            return False
        else:
            print "%s > %s" % (timestamp, message)
            return True
