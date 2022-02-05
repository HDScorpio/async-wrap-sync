from setuptools import setup

setup(
    name='async-wrap-sync',
    version='0.0.1',
    packages=['async_wrap_sync'],
    url='https://github.com/HDScorpio/async-wrap-sync',
    license='MIT',
    author='Andrey Ulagashev',
    author_email='ulagashev.andrey@gmail.com',
    description='Example of asyncio wrapper for synced code',
    install_requires=[
        'aiohttp',
        'requests',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            "aws-server = async_wrap_sync.cli:server",
            "aws-client = async_wrap_sync.cli:client",
            "aws-test = async_wrap_sync.cli:test",
        ]
    }
)
