#!/usr/bin/env python3

import time
import traceback
from datetime import datetime

from jobs import run


class Scheduler:

    def __init__(self):
        self.jobs = []

    def add_job(self, job):

        job["next_run"] = time.time()

        self.jobs.append(job)

    def run(self):

        print("\nScheduler started.")
        print(f"Loaded {len(self.jobs)} monitoring jobs.\n")

        while True:

            now = time.time()

            for job in self.jobs:

                if now >= job["next_run"]:

                    try:

                        run(job)

                    except KeyboardInterrupt:
                        raise

                    except Exception as e:

                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        print(f"{timestamp}  ERROR    {job['name']}")
                        print(f"Reason: {e}")

                        traceback.print_exc()

                    finally:

                        job["next_run"] = now + job["interval"]

            time.sleep(1)
