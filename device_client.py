import os
import redis
import control_parse
import threading
from Queue import Queue
import time
# TODO: have ctrl-C kill this more gracefully


class RedisSubscribeQueue(threading.Thread):
    """Connect to redis and subscribe to a channel, wx-publishing msg"""
    def __init__(self, pool, command_queue, subname="commanding"):
        """
        `pool`: the redis connection pool for this instance
        `subname`: subscriber channel on the redis server for the thread
        """
        threading.Thread.__init__(self)
        self.pool = pool
        self.subname = subname
        self.redis_conn = redis.Redis(connection_pool=self.pool)
        self.command_queue = command_queue

        json_spec = open("example.json", 'r').read()
        self.redis_conn.set("command_specification", json_spec)

        self.redis_pubsub = self.redis_conn.pubsub()
        # subscribe to both the general and specific client channels
        self.redis_pubsub.subscribe([subname])
        self.start()

    def run(self):
        for msg in self.redis_pubsub.listen():
            self.handle_msg(msg)

    def handle_msg(self, msg):
        r"""Do simple parsing of the message from the server"""
        self.command_queue.put(msg)
        print msg['data']


class DeviceClient(object):
    def __init__(self, subname="test_code", ackname="commanding_ack"):
        configaddr = "example.json"
        self.command_queue = Queue()
        self.config = control_parse.ControlSpec(configaddr=configaddr,
                                                silent=False)

        self.pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
        self.redis_conn = redis.Redis(connection_pool=self.pool)

        self.commandsub = RedisSubscribeQueue(self.pool, self.command_queue,
                                              subname=subname)

        while True:
            item = self.command_queue.get()
            print "starting on: ", item
            # working really hard now:
            time.sleep(0.5)
            print "done"
            command = item['data'].split()

            # optional call to simulate a device that does not reply with a
            # value
            #reply = [command[0]]
            reply = command

            if len(command) == 2:
                self.redis_conn.set(command[0], command[1])
                self.redis_conn.publish(ackname, " ".join(reply))
            else:
                print "malformed command: ", " ".join(command)

            self.command_queue.task_done()


if __name__ == "__main__":
    devclient = DeviceClient()
