import heapq
import threading
import time
from typing import Callable, NamedTuple

Task = Callable[[], None]


class Job(NamedTuple):
    execution_time: float
    task: Task


class Scheduler:
    def __init__(self, delay: float = 0) -> None:
        # defaults
        self._delay = delay
        # all tasks
        self.jobs = list[Job]()
        # sync condition
        self.condition = threading.Condition()
        # start in a new daemon thread
        threading.Thread(target=self._worker, daemon=True).start()

    def add_task(self, task: Task, *, delay: float | None = None) -> None:
        # default delay
        delay = delay if delay is not None else self._delay
        # calc the precise timestamp of execution
        execution_time = time.monotonic() + delay
        # sync condition
        with self.condition:
            # push task to in the exact tree position so it is already sorted
            heapq.heappush(self.jobs, Job(execution_time, task))
            # Wake up the worker
            self.condition.notify()

    def _worker(self) -> None:
        # worker loop always ready for tasks
        while True:
            # sync condition
            with self.condition:
                # block until add_task notify
                while not self.jobs:
                    self.condition.wait()

                # get next job, the top one is always the smallest execution time
                execution_time = self.jobs[0].execution_time
                now = time.monotonic()

                # time is not up, wait for it and loop again
                if now <= execution_time:
                    self.condition.wait(execution_time - now)
                    continue

                # time is up, pop the job
                job = heapq.heappop(self.jobs)
                # and then execute the task
                job.task()
