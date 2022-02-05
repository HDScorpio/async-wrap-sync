# coding: utf-8
""" Простой асинхронный HTTP сервер на базе aiohttp. """
import hashlib

from aiohttp import web
from aiohttp.web_runner import GracefulExit


routes = web.RouteTableDef()


@routes.get('/')
async def pong(_):
    return web.Response(text='Pong')


@routes.delete('/')
async def shutdown(r: web.Request):
    print('Stop server')
    # FIXME: клиенту не возвращается ответ, соединение обрывается
    raise GracefulExit


@routes.put('/')
async def upload(request: web.Request):
    bytes_ = 0
    count = 0
    min_ = 10**6
    max_ = 0
    req_count = request.app['ctx']['requests']
    request.app['ctx']['requests'] = req_count + 1
    chunk_size = request.app['chunk_size']

    reader = request.content
    md5 = hashlib.md5()
    while True:
        chunk = await reader.read(chunk_size)
        if not chunk:
            break

        # some workload
        md5.update(chunk)
        len_ = len(chunk)
        bytes_ += len_
        count += 1
        min_ = min(min_, len_)
        max_ = max(max_, len_)

    return web.json_response({
        'bytes': bytes_,  # количество полученный байт
        'count': count,  # количество принятых чанков
        'min': min_ if count else 0,  # минимальный размер чанка
        'max': max_,  # максимальный размер чанка
        'requests': req_count,  # количество обработанных сервером запросов
        'md5': md5.hexdigest()  # MD5 контрольная сумма
    }, status=201)


def run_server(bind='127.0.0.1', port=8080, chunk_size=1024):
    """
    Запуск сервера

    :param bind: адрес интерфейса
    :param port: прослушиваемый порт
    :param chunk_size: размер принимаемых чанков
    """
    print('Start server: receive chunk=%d' % chunk_size)
    app = web.Application()
    app['ctx'] = {'requests':  0}
    app['chunk_size'] = chunk_size
    app.add_routes(routes)
    web.run_app(app, host=bind, port=port)


def main():
    run_server()


if __name__ == '__main__':
    main()
