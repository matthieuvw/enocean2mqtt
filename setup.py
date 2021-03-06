#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='enocean2mqtt',
    version='0.2.0',
    keywords = ['enocean', 'mqtt'],
    description='EnOcean to MQTT bridge',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Matthieu Van Wynsberghe',
    author_email='matthieu.vw@disroot.org',
    url='https://github.com/matthieuvw/enocean2mqtt',
    packages=['enocean2mqtt'],
    install_requires=[
        'jsonschema==3.2.0',
        'enocean==0.60.0',
        'pyyaml==5.4.1',
        'paho-mqtt==1.5.1',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'enocean2mqtt = enocean2mqtt:launch',
        ],
    }
)
