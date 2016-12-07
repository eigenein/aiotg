#!/usr/bin/env python3
# coding: utf-8

import argparse
import asyncio
import logging
import socket
import sys

import aiohttp
import aiotg


class SimpleBot(aiotg.Bot):
    def on_update(self, telegram: aiotg.Telegram, update: aiotg.Update):
        logging.info("Received update: %r", update)


def main():
    parser = argparse.ArgumentParser(description="Run the simple bot that dumps every received update.")
    parser.add_argument("-t", "--token", required=True, help="Telegram bot token.")
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s [%(levelname).1s] %(message)s",
        level=logging.DEBUG,
        stream=sys.stderr,
        datefmt="%m-%d %H:%M:%S",
    )

    connector = aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)
    telegram = aiotg.Telegram(args.token, connector=connector)
    runner = aiotg.LongPollingRunner(telegram, SimpleBot())

    try:
        asyncio.get_event_loop().run_until_complete(async_main(runner))
    except KeyboardInterrupt:
        runner.stop()
    finally:
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
        asyncio.get_event_loop().close()


async def async_main(runner: aiotg.LongPollingRunner):
    async with runner:
        await runner.run()
