#!/usr/bin/env python3
# coding: utf-8

import setuptools

setuptools.setup(
    name="aiotg",
    version="0.3",
    description="Telegram Bot API wrapper for aiohttp.",
    author="Pavel Perestoronin",
    author_email="eigenein@gmail.com",
    url="https://github.com/eigenein/aiotg",
    packages=setuptools.find_packages(),
    zip_safe=True,
    entry_points={
        "console_scripts": ["aiotg = aiotg.__main__:main"],
    },
    license="MIT",
    install_requires=["aiohttp"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="telegram aiohttp async",
)
