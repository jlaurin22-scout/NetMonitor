#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor


class Executor:

    def __init__(self, modules, workers=25):

        self.modules = modules
        self.workers = workers

    def enrich(self, devices):

        with ThreadPoolExecutor(max_workers=self.workers) as pool:

            futures = []

            for device in devices:

                futures.append(
                    pool.submit(self._process_device, device)
                )

            #
            # Wait for completion.
            #
            for future in futures:
                future.result()

    def _process_device(self, device):

        for module in self.modules:
            module.enrich(device)
