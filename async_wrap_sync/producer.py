# coding: utf-8
from random import shuffle


class Producer:
    def __init__(self, count1k=1024):
        self.count = count1k
        p = list(b'0123456789abcdef')
        shuffle(p)
        self.pattern = bytes(p) * 64  # 16 * 64 == 1024
        self._gen = self._data_generator()
        self._rest = b''

    def read(self, size=None):
        if size == 0 or self._gen is None:
            return b''

        if size is None:
            buf = self._rest + b''.join([chunk for chunk in self._gen])
            self._rest = b''
            return buf

        if len(self._rest) >= size:
            self._rest, buf = self._rest[size:], self._rest[:size]
            return buf

        self._rest, buf = b'', self._rest
        for chunk in self._gen:
            buf += chunk
            if len(buf) >= size:
                break
        else:
            # конец данных
            self._gen = None

        self._rest, buf = buf[size:], buf[:size]
        return buf

    def _data_generator(self):
        for i in range(self.count):
            yield self.pattern
