import sys
from rq import Connection, Worker, Queue
import redis
# Preload libraries
import functions

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
listen = ['high', 'default', 'low']
with Connection():
    qs = 'redis://:83uaf_1313n_3r3-wfbu3bsih3-23urbkjbfu3b@128.118.192.79:6379/0'
    conn = redis.from_url(qs)
    with Connection(conn):
        w = Worker(map(Queue, listen))
        w.work()
