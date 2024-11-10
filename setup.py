# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='BreadcrumbsLiveRecorder-1',
    version='4.0.1',
    author='SAOJSM',
    description='An easy tool for recording live streams',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SAOJSM/LiveRecorder-1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'PyExecJS',
        'loguru',
        'pycryptodome',
        'distro',
        'tqdm'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ]
)
