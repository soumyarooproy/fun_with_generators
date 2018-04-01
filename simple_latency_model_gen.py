from collections import deque

def channel(delay):
    '''Model a delay using a coroutine

    This implementation uses a double-ended queue to buffer the payloads.
    '''
    q = deque(None for _ in range(delay + 1))
    while True:
        payload = q.popleft()
        payload = yield payload
        q.append(payload)

class SimpleLatencyModel:
    ''' Simple latency modeling - no bandwidth restrictions

    Producers generate payloads, which are consumed/processed by
    downstream modules/processes.
    '''
    def __init__(self, latency):
        self._cycle = 0
        self._latency = latency
        self._channel = channel(latency)
        self._channel.send(None)
        
    def _gen_payload(self, num_payloads):
        for i in range(num_payloads):
            print(f'Cycle {self._cycle}: Generate payload {i}')
            yield i

    def _process_payload(self, payload):
        if payload is not None:
            print(f'Cycle {self._cycle}: Process payload {payload}')
        else:
            print(f'Cycle {self._cycle}: Idle')

    def simulate(self, num_payloads):
        for payload in self._gen_payload(num_payloads):
            self._process_payload(self._channel.send(payload))
            self._cycle += 1
        print(f'Cycle {self._cycle}: Flush the channel')
        for _ in range(self._latency):
            self._process_payload(self._channel.send(None))
            self._cycle += 1
        print(f'Simulated {self._cycle} cycles')
        
if __name__ == '__main__':
    model = SimpleLatencyModel(4)
    model.simulate(10)
