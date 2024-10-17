import asyncio
import time


class ProjectSaver:

    def __init__(self, save_fn, min_interval):
        self._last_saved = None
        self._save_fn = save_fn
        self._min_interval = min_interval
        self._save_job = None

    def save(self, force=False):
        t = _get_time()
        if not force and self._last_saved is not None and t - self._last_saved < self._min_interval:
            if self._save_job is not None:
                return
            loop = asyncio.get_running_loop()
            self._save_job = loop.create_task(self._async_save(t))
            return
        if self._save_job is not None:
            self._save_job.cancel()
        self._do_save()

    async def _async_save(self, t: float):
        await asyncio.sleep(self._min_interval - t + self._last_saved)
        if asyncio.current_task(asyncio.get_running_loop()).cancelled():
            return
        self._do_save()
        self._save_job = None

    def _do_save(self):
        self._last_saved = _get_time()
        self._save_fn()


def _get_time():
    return time.monotonic()
