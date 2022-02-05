# coding: utf-8
import argparse
import time
from multiprocessing import Process

import requests

from async_wrap_sync.client import run_client
from async_wrap_sync.server import run_server


DEFAULT_URL = 'http://127.0.0.1:8080'


def parse_args(description=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-w', '--workers', type=int, default=1,
                        help='number of workers, default is 1')
    parser.add_argument('-t', '--tasks', type=int, default=1,
                        help='number of tasks, default is 1')
    parser.add_argument('-u', '--url', type=str, default=DEFAULT_URL,
                        help='URL address of server, default is "%s"' %
                             DEFAULT_URL)
    parser.add_argument('-c', '--chunk-size', type=int, default=1024,
                        help='send chunk size, default is 1024 bytes')
    parser.add_argument('-s', '--data-size', type=int, default=1024,
                        dest='count1k',
                        help='size of produced data in KiB, '
                             'default is 1024 (i.e. 1 MiB)')

    return parser.parse_args()


def parse_url(url):
    ip_port = url.split('//')[1]
    ip, port = ip_port.split(':')
    return ip, int(port)


def client(args=None):
    """ Запуск клиента """
    args = args or parse_args('Run HTTP client.')
    run_client(args.workers, args.tasks, args.url, args.chunk_size, args.count1k)


def server():
    """ Запуск сервера """
    parser = argparse.ArgumentParser(description='Run async HTTP server.')
    parser.add_argument('-c', '--chunk-size', type=int, default=1024,
                        help='receive chunk size, default is 1024 bytes')
    parser.add_argument('url', nargs='?', default=DEFAULT_URL, metavar='URL',
                        help='URL address of server, default is "%s"' %
                             DEFAULT_URL)
    args = parser.parse_args()

    ip, port = parse_url(args.url)

    run_server(ip, port, args.chunk_size)


def test():
    """
    Тестовый запуск локального сервера и клиента с фиксированными параметрами.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080,
                        help='port number, default is 8080')
    args = parser.parse_args()

    workers = 3
    tasks = 100
    ip = '127.0.0.1'
    url = 'http://%s:%d' % (ip, args.port)
    print('Test run: url=%s' % url)

    # Запуск сервера в отдельном процессе
    server_p = Process(target=run_server, args=(ip, args.port), daemon=True)
    server_p.start()
    time.sleep(0.1)
    print()

    run_client(workers, tasks, url)
    print()

    # останавливаем сервер, отправляя запрос
    try:
        requests.delete(url)
    except:
        # игнорируем любые ошибки
        pass
    server_p.join()


if __name__ == '__main__':
    test()
