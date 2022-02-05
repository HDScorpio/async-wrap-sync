# coding=utf-8
import threading
from queue import Queue

import requests


class _Consumer:
    def __init__(self, url):
        self.url = url
        # Сюда требуется сохранить ответ PUT запроса
        self.resp = None

    def write(self, data):
        raise NotImplemented

    def close(self):
        if self.resp:
            if self.resp.ok:
                return self.resp.json()
            return self.resp.status_code, self.resp.text


class WrongConsumer(_Consumer):
    """ Не рабочая версия Consumer

    На каждый вызов метода self.write() выполняется PUT запрос, а требуется
    выполнить один PUT запрос на несколько вызовов метода self.write().
    """

    def write(self, data):
        # Будет выполнено несколько запросов вместо одного
        self.resp = requests.put(self.url, data=data)


class TConsumer(_Consumer):
    """
    Версия Consumer на потоках.

    Функция requests.put() запускается в потоке threading.Thread().
    На вход функции передается итератор, который возвращает данные из очереди
    queue.Queue(). Очередь пополняется в основном потоке при каждом вызове
    метода self.write().
    """
    def __init__(self, url):
        super().__init__(url)

        self._queue = Queue(maxsize=1)
        self._putter = threading.Thread(target=self._requests_put,
                                        daemon=True)
        self._putter.start()

    def _requests_put(self):
        # выполняется в потоке
        self.resp = requests.put(self.url, data=self._iter())

    def _iter(self):
        # выполняется в потоке, вызываясь методом requests.put()
        while True:
            try:
                chunk = self._queue.get()
                if chunk is None:
                    break
                yield chunk
            finally:
                self._queue.task_done()

    def write(self, data):
        self._queue.put(data)
        self._queue.join()

    def close(self):
        self._queue.put(None)
        self._putter.join()

        return super().close()


class AConsumenr(_Consumer):
    """ Асинхронная версия Consumer

    Можно ли это реализовать с помощью asyncio, используя синхронную функцию
    requests.put()?
    """
    # TODO: требуется реализовать
    pass
