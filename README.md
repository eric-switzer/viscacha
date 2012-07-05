`Viscacha`
==========
`viscacha` is a command/monitor GUI which uses Redis as an intermediary.

The client and the GUI take commands from a JSON specification accessible over http. The GUI is built from the JSON specification. There is a distinction between "actions" and "variables" on the device client end. For example, a variable may be a parameter in a servo loop as opposed to an action. The GUI treats everything as a command and leaves the device to decide whether that command is a variable or an action. In either case, the client device sends an acknowledgment of the requested value.
The acknowledgment procedure is:

1. The GUI publishes `variable_name new_value` to the `commanding` channel and sets acknowledgment indicator to red.
2. A client subscribed to `commanding` handles this message, sends an acknowledgment and sets the Redis key (if success).
3. The GUI receives the acknowledgment and compares with the request. If success, set the acknowledgment indicator to green, otherwise yellow.

The GUI never sets Redis keys, and the device client is responsible for keeping its variables syncronized with Redis. The client device may access or set some internal variables at a rate too high for Redis. An example here could be a group of high-rate servo loops. These driver may also need to be controlled open-loop. In this case, the device client keeps an internal dictionary of variables rather than accessing Redis. In open loop, these can be reported/set on Redis, and in closed loop a value indicating that could be set on Redis rather than the live actuator value.

