import os
import redis
import control_parse
import threading
import queue
# connect to redis with subthread
# parse json file
# event handler for incoming: queue
# issue: sequenctial execution; may miss incoming command if sent during
# execution

class RedisSubscribeQueue(threading.Thread):
    """Connect to redis and subscribe to a channel, wx-publishing msg"""
    def __init__(self, pool, subname="commanding"):
        """
        `pool`: the redis connection pool for this instance
        `subname`: subscriber channel on the redis server for the thread
        """
        threading.Thread.__init__(self)
        self.pool = pool
        self.subname = subname
        self.redis_conn = redis.Redis(connection_pool=self.pool)

        self.redis_pubsub = self.redis_conn.pubsub()
        # subscribe to both the general and specific client channels
        self.redis_pubsub.subscribe([subname])
        self.start()

    def run(self):
        for msg in self.redis_pubsub.listen():
            self.handle_msg(msg)

    def handle_msg(self, msg):
        r"""Do simple parsinig of the message from the server"""
        print msg


class DeviceClient(object):
    def __init__(self, parent=None, id=-1):
        configaddr = "http://www.cita.utoronto.ca/~eswitzer/master.json"
        self.config = control_parse.ControlSpec(configaddr=configaddr,
                                                silent=False)

        self.pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
        self.redis_conn = redis.Redis(connection_pool=self.pool)

        self.acksub = network_client.RedisSubscribeQueue(self.pool,
                                                         self.client_id,
                                                subname="commanding_ack")

