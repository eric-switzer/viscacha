import wx
import redis
from threading import Thread
from wx.lib.pubsub import Publisher

class RedisConnection(Thread):
    """Connect to redis and get all published messages"""

    def __init__(self):
        """Connect and subscribe"""
        Thread.__init__(self)
        self.redis_conn = redis.Redis(host='localhost', port=6379, db=0)

        self.redis_pubsub = self.redis_conn.pubsub()
        self.redis_pubsub.subscribe("housekeeping")
        self.start()    # start the thread

    def run(self):
        while True:
            msg = self.redis_pubsub.listen().next()
            wx.CallAfter(self.postmsg, msg)

    def postmsg(self, msg):
        """Send time to GUI"""
        Publisher().sendMessage("redis_incoming", msg)
