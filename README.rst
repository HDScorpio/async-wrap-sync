*async-wrap-sync* - попытка обернуть синхронный код асинхронными примитивами asyncio.

Задача
------

Имеется HTTP сервер (``server.py``), принимающий PUT запросы на загрузку данных.

.. code-block:: console

   $ aws-server
   Start server: receive chunk=1024
   ======== Running on http://127.0.0.1:8080 ========
   (Press CTRL+C to quit)

.. code-block:: console

   $ curl -XPUT --data-binary @some.file http://127.0.0.1:8080
   {"bytes": 1306, "count": 2, "min": 282, "max": 1024, "requests": 1, "md5": "73bcc85b6b01a33a5ede83e239579f9f"}


Имеется клиентский код (``client.py``), выполняющий многопоточное (``threading``)
копирование данных с одного файлового объекта (``producer.py:Producer``) в
другой (``consumer.py:Consumer``).

.. code-block:: console

   $ aws-client -t 10 -w 2
   Start copying: workers=2, tasks=10, write chunk=1024, url=http://127.0.0.1:8080
   Bytes per task: 1048576
   Total write bytes: 10485760
   Start workers

   Progress tasks
   100%|███████████████████████████████████████| 10/10 [00:00<00:00, 14.53 tasks/s]

   Finish workers
   Total time: 1.122833, best: 0.178985, worst: 0.243505


При получении данных ``Consumer`` отправляет данные на сервер с помощью
вызова синхронной функции ``requests.put``. Так как эта функция является
блокирующей, это ограничение обходится с помощью отправки её в поток
``threading.Thread``. Реализация выполнена в классе ``consumer.py::TConsumer``.


**Вопрос?**

Возможно ли реализовать асинхронный вариант ``consumer.py::Consumer`` на базе
``asyncio``, используя синхронную функцию ``requests.put``?

То есть требуется реализовать класс ``consumer.py::AConsumer`` и использовать
его в клиенте ``client.py``, импортировав следующим образом:

.. code-block:: python

   #from async_wrap_sync.consumer import TConsumer as Consumer
   from async_wrap_sync.consumer import AConsumer as Consumer

Остальной код в клиенте менять нельзя.


Установка
---------

.. code-block:: console

   $ pip install -e git+https://github.com/HDScorpio/async-wrap-sync


Использование
-------------

Пакет предоставляет три исполняемых скрипта:

- ``aws-server`` - асинхронный HTTP сервер на базе ``aiohttp``
- ``aws-client`` - многопоточный HTTP клиент на базе ``requests``
- ``aws-test`` - запуск сервера и клиента с базовыми параметрами

Доступные опции сервера и клиента можно посмотреть с помощью опции ``-h/--help``.
