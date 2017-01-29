## `aiotg`

[Telegram Bot API](https://core.telegram.org/bots/api) wrapper for [`aiohttp`](https://aiohttp.readthedocs.io/en/stable/).

[![Build Status](https://travis-ci.org/eigenein/aiotg.svg?branch=master)](https://travis-ci.org/eigenein/aiotg)

## Features

* Supports [long polling](https://core.telegram.org/bots/api#getupdates).
* Supports [type hinting](https://docs.python.org/3/library/typing.html).
* Provides [command-line utility](#running-module-or-package-as-a-bot) to run a bot.

## Library Installation

```sh
pip install git+https://github.com/eigenein/aiotg.git
```

You may want to state the library in `requirements.txt`:

```sh
git+https://github.com/eigenein/aiotg.git
```

## Getting Started

### Low-level API

Receiving updates:

```python
offset = 0
async with aiotg.Telegram(token) as telegram:  # type: aiotg.Telegram
    while True:
        updates = await telegram.get_updates(offset, limit=100, timeout=5)
        if not updates:
            continue
        for update in updates:
            logging.debug("Got update: %s", update)
        offset = updates[-1].id + 1
```

### High-level API

Define a class to receive bot updates:

```python
class SimpleBot(aiotg.Bot):
    async def on_update(self, telegram: aiotg.Telegram, update: aiotg.Update):
        logging.info("Received update: %r", update)
```

Then use one of the runners to start receiving updates:

#### Long-polling Runner

```python
token = "…"  # Telegram bot API token
connector = aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)
telegram = aiotg.Telegram(token, connector=connector)
runner = aiotg.LongPollingRunner(telegram, SimpleBot())

asyncio.get_event_loop().run_until_complete(runner.run())
```

#### Webhook Runner

Not implemented yet.

#### Running module or package as a bot

To avoid writing boilerplate code to set up logging, connection and runner – you can simply run `aiotg` command with the fully-qualified class name: 

```sh
aiotg --token <TOKEN> aiotg.SimpleBot
```

See `aiotg --help` for more options.

### Pattern Matching

Not implemented yet.

#### States

TODO

## Examples

These bots are built with `aiotg`:

* [eigenein/loggerbot](https://github.com/eigenein/loggerbot)

## Source Code

The project is hosted on [GitHub](https://github.com/eigenein/aiotg).

Please feel free to [submit an issue](https://github.com/eigenein/aiotg/issues) if you have found a bug or have some suggestion in order to improve the library.

## Dependencies

* Python 3.6+
* [`aiohttp`](https://aiohttp.readthedocs.io/en/stable/) library
