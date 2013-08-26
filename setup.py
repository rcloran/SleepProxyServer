from setuptools import setup

setup(
    name="SleepProxyServer",
    description="An implementation of a sleep proxy server, "
        "which aims to be compatible with Apple's wake on demand",
    version="0.1",
    author="Russell Cloran",
    author_email="rcloran@gmail.com",
    url="https://github.com/rcloran/SleepProxyServer",
    packages=["sleepproxy"],
    scripts=["scripts/sleepproxyd"],
    install_requires=[
        # "dbus-python",  # Unfortunately not distributed with a setup.py
        "dnspython",
        "gevent",
        "IPy",
        "netifaces",
        "scapy",
    ],
    dependency_links=[
        "http://www.secdev.org/projects/scapy/files/",
    ]
)
