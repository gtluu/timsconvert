from redis import Redis
from rq import Queue, Worker, Connection


if __name__ == '__main__':
    with Connection(Redis()):
        worker = Worker(list(map(Queue, ['default'])))
        worker.work()
