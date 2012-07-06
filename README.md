`Viscacha`
==========
`viscacha` is a command/monitor GUI which uses Redis as an intermediary.

The client and the GUI take commands from a JSON specification accessible over http. The GUI is built from the JSON specification. There is a distinction between "actions" and "variables" on the device client end. For example, a variable may be a parameter in a servo loop as opposed to an action. The GUI treats everything as a command and leaves the device to decide whether that command is a variable or an action. In either case, the client device sends an acknowledgment of the requested value.
The acknowledgment procedure is:

1. The GUI publishes `variable_name new_value` to the `commanding` channel and sets acknowledgment indicator to red.
2. A client subscribed to `commanding` handles this message, sends an acknowledgment and sets the Redis key (if success).
3. The GUI receives the acknowledgment and compares with the request. If success, set the acknowledgment indicator to green, otherwise yellow.

The GUI never sets Redis keys, and the device client is responsible for keeping its variables syncronized with Redis. The client device may access or set some internal variables at a rate too high for Redis. An example here could be a group of high-rate servo loops. These driver may also need to be controlled open-loop. In this case, the device client keeps an internal dictionary of variables rather than accessing Redis. In open loop, these can be reported/set on Redis, and in closed loop a value indicating that could be set on Redis rather than the live actuator value.

To tunnel through a gateway, issue:
`ssh  -l username -L 6379:redis_servername:6379  gateway_name  cat -`

Installing on a mac:
--------------------

1. `sudo port install py27-redis` or `git clone https://github.com/andymccurdy/redis-py.git`
2. `sudo port install py27-wxpython` or install the .dmg from the wxpython site
3. `sudo port install py27-simplejson`
4. the wxpython binaries from the .dmg installation are 32bit, so use `arch -i386 python2.7 client.py`
(Please update as needed.)

Installing on Ubuntu:
---------------------

1. get git `sudo apt-get install git-core`
2. `git clone https://github.com/eric-switzer/viscacha.git`
3. `sudo apt-get install python-wxgtk2.8`
4. Depending on your version of ubuntu, (new Ubuntu) `sudo apt-get install python-redis`, `git clone https://github.com/andymccurdy/redis-py.git` and `cd redis-py; sudo python setup.py install`; you may need to remove an old package version using `sudo apt-get remove python-redis` if it interferes.
