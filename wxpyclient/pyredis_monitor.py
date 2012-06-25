r"""MONITOR redis command functionality from dougk7's pyredis fork
Note: this should enter the pyredis main branch in a future revision
"""
import redis
import unittest
from redis.connection import ConnectionPool, UnixDomainSocketConnection
from redis.exceptions import (
    ConnectionError,
    DataError,
    RedisError,
    ResponseError,
    WatchError,
)


class Monitor(object):
    """
    Monitor is useful for handling the MONITOR command to the redis server.

    After calling the monitor() method, the listen() method blocks until
    the server receives a message and that message will be returned.
    """
    def __init__(self, connection_pool, shard_hint=None):
        self.connection_pool = connection_pool
        self.shard_hint = shard_hint
        self.connection = None
        self.monitor_command = set(('monitor',))

    def execute_command(self, *args, **kwargs):
        "Execute a Monitor command"
        if self.connection is None:
            self.connection = self.connection_pool.get_connection(
                'monitor',
                self.shard_hint
                )
        connection = self.connection
        try:
            connection.send_command(*args)
            return self.parse_response()
        except ConnectionError:
            connection.disconnect()
            connection.send_command(*args)
            return self.parse_response()

    def parse_response(self):
        "Parse the response from a monitor command"
        response = self.connection.read_response()
        # This part with the OK is only needed when we connect initially.
        if response == 'OK':
            return response
        time, command = response.split(' ',1)
        return float(time), command

    def listen(self):
        "Listen for commands coming to the server."
        while 1:
            r = self.parse_response()
            msg = {
                'time': r[0],
                'command': r[1]
            }
            yield msg

    def monitor(self):
        "Start the monitoring."
        return self.execute_command('MONITOR')


class MonitorTestCase(unittest.TestCase):
    def setUp(self):
        self.connection_pool = redis.ConnectionPool()
        self.client = redis.Redis(connection_pool=self.connection_pool)
        self.monitor = self.client.monitor()

    def tearDown(self):
        self.connection_pool.disconnect()

    def test_monitor(self):
        self.assertEquals(self.monitor.monitor(), 'OK')

    def test_listen(self):
        self.monitor.monitor()
        self.assertEquals(self.monitor.listen().next()['command'], '"MONITOR"')
        self.client.set('foo', 'bare')
        self.assertEquals(self.monitor.listen().next()['command'], '"SET" "foo" "bar"')
