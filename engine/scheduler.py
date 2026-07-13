#!/usr/bin/env python3

import time
from jobs import run


class Scheduler:

    def __init__(self):
        self.jobs = []

    def add_job(self, job):
        job["next_run"] = time.time()
        self.jobs.append(job)

    def run(self):

        while True:

            now = time.time()

            for job in self.jobs:

                if now >= job["next_run"]:

                    run(job)

                    job["next_run"] = now + job["interval"]

            time.sleep(1)
