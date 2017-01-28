#!/usr/bin/env python3

import argparse
import asyncio
import importlib
import logging
import socket
import sys

import aiohttp

import aiotg


def main():
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        description="Run specified class as a bot.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-t", "--token",
        required=True,
        help="Telegram bot token",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="long-polling updates limit (default: 100)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="long-polling timeout in seconds (default: 5)",
    )
    parser.add_argument(
        "-v", "--verbosity",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="logging level (default: INFO)",
    )
    parser.add_argument(
        "-l", "--log-file",
        type=argparse.FileType("wt", encoding="utf-8"),
        default=sys.stderr,
        help="log file (default: stderr)",
    )
    parser.add_argument(
        "class_",
        metavar="CLASS",
        default="aiotg.SimpleBot",
        help="fully qualified name of bot class (default: aiotg.SimpleBot)",
    )
    args = parser.parse_args()

    # Set up logging.
    logging.basicConfig(
        format="%(asctime)s [%(levelname).1s] %(message)s",
        level=getattr(logging, args.verbosity),
        stream=args.log_file,
        datefmt="%m-%d %H:%M:%S",
    )

    # Instantiate bot.
    try:
        module_name, class_name = args.class_.split(".", maxsplit=1)
        module = importlib.import_module(module_name)
        bot_class = getattr(module, class_name)
    except ValueError:
        parser.error("fully qualified class name is expected")
    except ImportError as ex:
        parser.error(f"failed to import '{module_name}': {ex}")
    except AttributeError:
        parser.error(f"class '{class_name}' is not found in module '{module_name}'")
    # noinspection PyUnboundLocalVariable
    if not issubclass(bot_class, aiotg.Bot):
        logging.warning("'%s' is not a subclass of '%s'", bot_class.__name__, aiotg.Bot.__name__)

    # Set up connection and runner.
    connector = aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)
    telegram = aiotg.Telegram(args.token, connector=connector)
    runner = aiotg.LongPollingRunner(telegram, bot_class(), limit=args.limit, timeout=args.timeout)

    # Run the bot.
    try:
        asyncio.get_event_loop().run_until_complete(async_main(runner))
    except KeyboardInterrupt:
        runner.stop()
    finally:
        logging.info("Waiting until all tasks are complete…")
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
        asyncio.get_event_loop().close()


async def async_main(runner: aiotg.LongPollingRunner):
    """
    Runs the runner asynchronously.
    """
    async with runner:
        await runner.run()
