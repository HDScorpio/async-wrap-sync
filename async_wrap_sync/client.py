
import hashlib
import queue
import threading
import time

from tqdm import trange

from async_wrap_sync.consumer import TConsumer as Consumer
# from async_wrap_sync.consumer import AConsumer as Consumer
from async_wrap_sync.producer import Producer


class CopyTask:
    def __init__(self, url, chunk_size=1024, count1k=1024):
        self._src = Producer(count1k)
        self._dst = Consumer(url)
        self._chunk_size = chunk_size

    def __call__(self):
        md5 = hashlib.md5()
        start = time.time()
        while True:
            chunk = self._src.read(self._chunk_size)
            if not chunk:
                break

            md5.update(chunk)
            self._dst.write(chunk)

        elapsed = time.time() - start
        result = self._dst.close()

        return elapsed, result['md5'] == md5.hexdigest()


class Worker(threading.Thread):
    result_lock = threading.Lock()

    def __init__(self, q: queue.Queue, results: list):
        super().__init__()
        self._q = q
        self._res = results
        self.daemon = True

    def run(self) -> None:
        while True:
            task = self._q.get()
            try:
                if task is None:
                    break
                self.save_result(task())
            except Exception as e:
                self.save_result(e)
            finally:
                self._q.task_done()

    def save_result(self, res):
        with self.result_lock:
            self._res.append(res)


def run_client(number_workers, number_tasks, url, chunk_size=1024, count1k=1024):
    """
    Запуск клиентского кода

    :param number_workers: количество потоков
    :param number_tasks: количество задач
    :param url: URL адрес сервера
    :param chunk_size: размер отправляемых чанков
    :param count1k: размер генерируемых данных в КиБ
    :return:
    """
    print('Start copying: workers=%d, tasks=%d, write chunk=%d, url=%s' % (
        number_workers, number_tasks, chunk_size, url))
    print('Bytes per task: %d' % (count1k * 1024))
    print('Total write bytes: %d' % (count1k * 1024 * number_tasks))

    q = queue.Queue(maxsize=number_workers)

    results = []
    workers = []
    print('Start workers')
    for w in range(number_workers):
        worker = Worker(q, results)
        worker.start()
        workers.append(worker)

    print('\nProgress tasks')
    start = time.time()
    for i in trange(number_tasks, ncols=80, unit=' tasks'):
        q.put(CopyTask(url, chunk_size, count1k))
    print('')

    print('Finish workers')
    for w in range(number_workers):
        q.put(None)
    q.join()
    total = time.time() - start

    for w in workers:
        w.join()

    best = 10**6
    worst = 0
    for r in results:
        if not isinstance(r, tuple) or not r[1]:
            print(r)
            continue
        elapsed = r[0]
        best = min(elapsed, best)
        worst = max(elapsed, worst)

    print('Total time: %.6f, best: %.6f, worst: %.6f' % (total, best, worst))
