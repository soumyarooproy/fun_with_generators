# Fun with Python Generators and Coroutines

## Use coroutines to model message pipes/channels with latency

Message pipes with delays are frequently used in performance modeling of
systems.

As depicted in the simple block diagram below, a producer produces payloads
to be consumed by the consumer over a channel with a delay of `d` units.
```
______________                      ______________
|  Producer  |        Payload       |  Consumer  |
|____________|   ---------------->  |____________|
                  Channel Delay d
```
A straightforward way to model this would be to use a FIFO queue. The producer
would push a payload on one end of the queue and the consumer would extract
payloads from the other end of the queue.

That would result in this kind of a code structure:
```
# channel is a deque of size (delay d + 1)

for payload in payload_generator():
    channel.append(payload)
    consume(channel.popleft())

# Flush the channel to process the rest of the payloads
```

In [this example](./simple_latency_model_gen.py), such a system
is modeled using a coroutine modeling the channel latency.

```
def channel(delay):
    q = deque(None for _ in range(delay + 1))
    while True:
        payload = q.popleft()
        payload = yield payload
        q.append(payload)
```

With this, the earlier code now looks like the following:
```
# channel is now the coroutine above

for payload in payload_generator():
    consume(channel.send(payload))

# Flush the channel to process the rest of the payloads
```
The method `send()` method is used to feed datum to a couroutine.

[The example](./simple_latency_model_gen.py) code generates the following output:
```
Cycle 0: Generate payload 0
Cycle 0: Idle
Cycle 1: Generate payload 1
Cycle 1: Idle
Cycle 2: Generate payload 2
Cycle 2: Idle
Cycle 3: Generate payload 3
Cycle 3: Idle
Cycle 4: Generate payload 4
Cycle 4: Process payload 0
Cycle 5: Generate payload 5
Cycle 5: Process payload 1
Cycle 6: Generate payload 6
Cycle 6: Process payload 2
Cycle 7: Generate payload 7
Cycle 7: Process payload 3
Cycle 8: Generate payload 8
Cycle 8: Process payload 4
Cycle 9: Generate payload 9
Cycle 9: Process payload 5
Cycle 10: Flush the channel
Cycle 10: Process payload 6
Cycle 11: Process payload 7
Cycle 12: Process payload 8
Cycle 13: Process payload 9
Simulated 14 cycles
```

