`Viscacha`
==========
`viscacha` is a command/monitor GUI which uses Redis as an intermediary.

The client and the GUI take commands from a JSON specification accessible over http. The GUI is built from the JSON specification. There is a distinction between "actions" and "variables" on the device client end. For example, a variable may be a parameter in a servo loop as opposed to an action. The GUI treats everything as a command and leaves the device to decide whether that command is a variable or an action. In either case, the client device sends an acknowledgment of the requested value.
The acknowledgment procedure is:

1. The GUI publishes `variable_name new_value` to the `commanding` channel and sets acknowledgment indicator to yellow.
2. A client subscribed to `commanding` handles this message, sends an acknowledgment and sets the Redis key (if success).
3. The GUI receives the acknowledgment and compares with the request. If success, set the acknowledgment indicator to green, otherwise red.

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

Getting started: `device-client.py` is a client for a mock device to be controlled. Start a copy of that and also an instance of `redis-cli` running `monitor` to see the exchange. Next start the client, `python client.py`.

The interface:
--------------

When `client.py` starts, it opens a window titled `Command Window`. This has buttons `Refresh` (get most recent values from redis for each variable), `Who` (see what clients are registered) and `Send comment` (publish a comment that all clients can see and log). Under `Monitor` in the menu bar, you can select systems and pull up a window that only shows current values. The same system can be pulled up under `Command` in the menu bar to extend each variable to allow control.

When a control system window comes up, it will have sub-system tabs, and within those, a list of variables. Each variable has a description, a current value indicator, and a method of sending a new value. When the value gets sent, the indicator box becomes yellow until it hears an ack from the device client that the command has been received and acted on. If the ack returns the requested value (success), the box turns green and if not, it turns red.

Configuration:
--------------

The configuration is managed in a json file.

* system: one window has all the control for one system
* category: is a tab of sub-systems under the main system window
* destination: name to publish `redis` command to
* displayorder: order of how the variable/action buttons appear (linear)
* type: The `type` field indicates the kind of entry for the variable/action. Allowed values are `input_onoff`, `input_value`, and `input_select`. The on/off type gives a toggle switch that switches between 0 and 1. The value type allows the user to set a variable to a numerical value. The "select" type does not send a value be instead triggers some action on the device.
* confirm: an optional keyword that requires user confirmation before sending a command
