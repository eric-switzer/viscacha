#!/usr/bin/python
import redis
import sys

r_server = redis.Redis("localhost")
json_spec = open(sys.argv[1], 'r').read()
r_server.set("command_specification", json_spec)
