#!/usr/bin/env python3
# coding: utf-8

import datetime
import enum
import json
import logging
import sys

from typing import Any, Callable, List, Optional, TypeVar, Union

import aiohttp

T = TypeVar("T")

if sys.version_info < (3, 6):
    raise ImportError("aiotg requires Python 3.6+")


class ParseMode(enum.Enum):
    """
    https://core.telegram.org/bots/api#formatting-options
    """
    default = None
    markdown = "Markdown"
    html = "HTML"


class ChatAction(enum.Enum):
    """
    https://core.telegram.org/bots/api#sendchataction
    """
    typing = "typing"
    upload_photo = "upload_photo"
    record_video = "record_video"
    upload_video = "upload_video"
    record_audio = "record_audio"
    upload_audio = "upload_audio"
    upload_document = "upload_document"
    find_location = "find_location"


class ChatType(enum.Enum):
    """
    https://core.telegram.org/bots/api#chat
    """
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = "channel"


class MessageEntityType(enum.Enum):
    """
    https://core.telegram.org/bots/api#messageentity
    """
    mention = "mention"
    hashtag = "hashtag"
    bot_command = "bot_command"
    url = "url"
    email = "email"
    bold = "bold"
    italic = "italic"
    code = "code"
    pre = "pre"
    text_link = "text_link"
    text_mention = "text_mention"


class ResponseBase:
    """
    Base response object.
    """
    __slots__ = ()

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ", ".join(
            "%s: %r" % (name, getattr(self, name))
            for name in self.__slots__
            if getattr(self, name)
        ))


class User(ResponseBase):
    """
    This object represents a Telegram user or bot.
    https://core.telegram.org/bots/api#user
    """
    __slots__ = ("id", "first_name", "last_name", "username")

    def __init__(self, user: dict):
        self.id: int = user["id"]
        self.first_name: str = user["first_name"]
        self.last_name: Optional[str] = user.get("last_name")
        self.username: Optional[str] = user.get("username")


class Chat(ResponseBase):
    """
    This object represents a chat.
    https://core.telegram.org/bots/api#chat
    """
    __slots__ = ("id", "type", "title", "username", "first_name", "last_name")

    def __init__(self, chat: dict):
        self.id: int = chat["id"]
        self.type = ChatType(chat["type"])
        self.title: Optional[str] = chat.get("title")
        self.username: Optional[str] = chat.get("username")
        self.first_name: Optional[str] = chat.get("first_name")
        self.last_name: Optional[str] = chat.get("last_name")


class MessageEntity(ResponseBase):
    """
    This object represents one special entity in a text message. For example, hashtags, usernames, URLs, etc.
    https://core.telegram.org/bots/api#messageentity
    """
    __slots__ = ("type", "offset", "length", "url", "user")

    def __init__(self, message_entity: dict):
        self.type = MessageEntityType(message_entity["type"])
        self.offset: int = message_entity["offset"]
        self.length: int = message_entity["length"]
        self.url: Optional[str] = message_entity.get("url")
        self.user = get_optional(message_entity, "user", User)

    def __len__(self):
        return self.length


class Audio(ResponseBase):
    """
    This object represents an audio file to be treated as music by the Telegram clients.
    https://core.telegram.org/bots/api#audio
    """
    __slots__ = ("file_id", "duration", "performer", "title", "mime_type", "file_size")

    def __init__(self, audio: dict):
        self.file_id: str = audio["file_id"]
        self.duration = datetime.timedelta(seconds=audio["duration"])
        self.performer: Optional[str] = audio.get("performer")
        self.title: Optional[str] = audio.get("title")
        self.mime_type: Optional[str] = audio.get("mime_type")
        self.file_size: Optional[int] = audio.get("file_size")


class PhotoSize(ResponseBase):
    """
    This object represents one size of a photo or a file / sticker thumbnail.
    https://core.telegram.org/bots/api#photosize
    """
    def __init__(self, photo_size: dict):
        self.file_id: str = photo_size["file_id"]
        self.width: int = photo_size["width"]
        self.height: int = photo_size["height"]
        self.file_size: Optional[int] = photo_size.get("file_size")


class Document(ResponseBase):
    """
    This object represents a general file (as opposed to photos, voice messages and audio files).
    https://core.telegram.org/bots/api#document
    """
    __slots__ = ("file_id", "thumbnail", "file_name", "mime_type", "file_size")

    def __init__(self, document: dict):
        self.file_id: str = document["file_id"]
        self.thumbnail = get_optional(document, "thumb", PhotoSize)
        self.file_name: Optional[str] = document.get("file_name")
        self.mime_type: Optional[str] = document.get("mime_type")
        self.file_size: Optional[int] = document.get("file_size")


class Sticker(ResponseBase):
    """
    This object represents a sticker.
    https://core.telegram.org/bots/api#sticker
    """
    __slots__ = ("file_id", "width", "height", "thumbnail", "emoji", "file_size")

    def __init__(self, sticker: dict):
        self.file_id: str = sticker["file_id"]
        self.width: int = sticker["width"]
        self.height: int = sticker["height"]
        self.thumbnail = get_optional(sticker, "thumb", PhotoSize)
        self.emoji: Optional[str] = sticker.get("emoji")
        self.file_size: Optional[int] = sticker.get("file_size")


class Video(ResponseBase):
    """
    This object represents a video file.
    https://core.telegram.org/bots/api#video
    """
    __slots__ = ("file_id", "width", "height", "duration", "thumbnail", "mime_type", "file_size")

    def __init__(self, video: dict):
        self.file_id: str = video["file_id"]
        self.width: int = video["width"]
        self.height: int = video["height"]
        self.duration = datetime.timedelta(seconds=video["duration"])
        self.thumbnail = get_optional(video, "thumb", PhotoSize)
        self.mime_type: Optional[str] = video.get("mime_type")
        self.file_size: Optional[int] = video.get("file_size")


class Voice(ResponseBase):
    """
    This object represents a voice note.
    https://core.telegram.org/bots/api#voice
    """
    __slots__ = ("file_id", "duration", "mime_type", "file_size")

    def __init__(self, voice: dict):
        self.file_id: str = voice["file_id"]
        self.duration = datetime.timedelta(seconds=voice["duration"])
        self.mime_type: Optional[str] = voice.get("mime_type")
        self.file_size: Optional[int] = voice.get("file_size")


class Contact(ResponseBase):
    """
    This object represents a voice note.
    https://core.telegram.org/bots/api#contact
    """
    __slots__ = ("phone_number", "first_name", "last_name", "user_id")

    def __init__(self, contact: dict):
        self.phone_number: str = contact["phone_number"]
        self.first_name: str = contact["first_name"]
        self.last_name: Optional[str] = contact.get("last_name")
        self.user_id: Optional[int] = contact.get("user_id")


class Location(ResponseBase):
    """
    This object represents a point on the map.
    https://core.telegram.org/bots/api#location
    """
    __slots__ = ("longitude", "latitude")

    def __init__(self, location: dict):
        self.longitude: float = location["longitude"]
        self.latitude: float = location["latitude"]


class Venue(ResponseBase):
    """
    This object represents a venue.
    https://core.telegram.org/bots/api#venue
    """
    __slots__ = ("location", "title", "address", "foursquare_id")

    def __init__(self, venue: dict):
        self.location = Location(venue["location"])
        self.title: str = venue["title"]
        self.address: str = venue["address"]
        self.foursquare_id: str = venue.get("foursquare_id")


class InlineQuery(ResponseBase):
    """
    This object represents an incoming inline query.
    When the user sends an empty query, your bot could return some default or trending results.
    https://core.telegram.org/bots/api#inlinequery
    """
    __slots__ = ("id", "from_", "location", "query", "offset")

    def __init__(self, inline_query: dict):
        self.id: str = inline_query["id"]
        self.from_ = User(inline_query["from"])
        self.location = get_optional(inline_query, "location", Location)
        self.query: str = inline_query["query"]
        self.offset: str = inline_query["offset"]  # type: str


class ChosenInlineResult(ResponseBase):
    """
    Represents a result of an inline query that was chosen by the user and sent to their chat partner.
    https://core.telegram.org/bots/api#choseninlineresult
    """
    __slots__ = ("result_id", "from_", "location", "inline_message_id", "query")

    def __init__(self, chosen_inline_result: dict):
        self.result_id: str = chosen_inline_result["result_id"]
        self.from_ = User(chosen_inline_result["from"])
        self.location = get_optional(chosen_inline_result, "location", Location)
        self.inline_message_id: Optional[str] = chosen_inline_result.get("inline_message_id")
        self.query = chosen_inline_result["query"]


class CallbackQuery(ResponseBase):
    """
    This object represents an incoming callback query from a callback button in an inline keyboard.
    If the button that originated the query was attached to a message sent by the bot, the field message will be presented.
    If the button was attached to a message sent via the bot (in inline mode), the field inline_message_id will be presented.
    https://core.telegram.org/bots/api#callbackquery
    """
    __slots__ = ("id", "from_", "message", "inline_message_id", "data")

    def __init__(self, callback_query: dict):
        self.id: str = callback_query["id"]
        self.from_ = User(callback_query["from"])
        self.message = get_optional(callback_query, "message", Message)
        self.inline_message_id: Optional[str] = callback_query.get("inline_message_id")
        self.data: str = callback_query["data"]


class Message(ResponseBase):
    """
    This object represents a message.
    https://core.telegram.org/bots/api#message
    """
    __slots__ = (
        "id", "from_", "date", "chat", "forward_from", "forward_from_chat", "forward_date", "reply_to_message",
        "edit_date", "text", "entities", "audio", "document", "photo", "sticker", "video", "voice",
        "caption", "contact", "location", "venue", "new_chat_member", "left_chat_member", "new_chat_title",
        "new_chat_photo", "delete_chat_photo", "group_chat_created", "supergroup_chat_created",
        "channel_chat_created", "migrate_to_chat_id", "migrate_from_chat_id", "pinned_message",
    )

    def __init__(self, message: dict):
        self.id: int = message["message_id"]
        self.from_ = get_optional(message, "from", User)
        self.date = datetime.datetime.fromtimestamp(message["date"])
        self.chat = Chat(message["chat"])
        self.forward_from = get_optional(message, "forward_from", User)
        self.forward_from_chat = get_optional(message, "forward_from_chat", Chat)
        self.forward_date = get_optional(message, "forward_date", datetime.datetime.fromtimestamp)
        self.reply_to_message = get_optional(message, "reply_to_message", Message)
        self.edit_date = get_optional(message, "edit_date", datetime.datetime.fromtimestamp)
        self.text = message.get("text")  # type: Optional[str]
        self.entities = get_optional_array(message, "entities", MessageEntity)
        self.audio = get_optional(message, "audio", Audio)
        self.document = get_optional(message, "document", Document)
        self.photo = get_optional_array(message, "photo", PhotoSize)
        self.sticker = get_optional(message, "sticker", Sticker)
        self.video = get_optional(message, "video", Video)
        self.voice = get_optional(message, "voice", Voice)
        self.caption: Optional[str] = message.get("caption")
        self.contact = get_optional(message, "contact", Contact)
        self.location = get_optional(message, "location", Location)
        self.venue = get_optional(message, "venue", Venue)
        self.new_chat_member = get_optional(message, "new_chat_member", User)
        self.left_chat_member = get_optional(message, "left_chat_member", User)
        self.new_chat_title: Optional[str] = message.get("new_chat_title")
        self.new_chat_photo = get_optional_array(message, "new_chat_photo", PhotoSize)
        self.delete_chat_photo: bool = message.get("delete_chat_photo", False)
        self.group_chat_created: bool = message.get("group_chat_created", False)
        self.supergroup_chat_created: bool = message.get("supergroup_chat_created", False)
        self.channel_chat_created: bool = message.get("channel_chat_created", False)
        self.migrate_to_chat_id: Optional[int] = message.get("migrate_to_chat_id")
        self.migrate_from_chat_id: Optional[int] = message.get("migrate_from_chat_id")
        self.pinned_message = get_optional(message, "pinned_message", Message)


class Update(ResponseBase):
    """
    This object represents an incoming update.
    Only one of the optional fields can be present in any given update.
    https://core.telegram.org/bots/api#update
    """
    __slots__ = ("id", "message", "edited_message", "inline_query", "chosen_inline_result", "callback_query")

    def __init__(self, update: dict):
        self.id: int = update["update_id"]
        self.message = get_optional(update, "message", Message)
        self.edited_message = get_optional(update, "edited_message", Message)
        self.inline_query = get_optional(update, "inline_query", InlineQuery)
        self.chosen_inline_result = get_optional(update, "chosen_inline_result", ChosenInlineResult)
        self.callback_query = get_optional(update, "callback_query", CallbackQuery)


class Telegram:
    """
    Telegram Bot API wrapper.
    """

    headers = {"Content-Type": "application/json"}
    logger = logging.getLogger(__name__)

    def __init__(self, token: str):
        self.url = f"https://api.telegram.org/bot{token}/{{}}"
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def get_updates(self, offset: int, limit: int, timeout: int):
        """
        Use this method to receive incoming updates using long polling.
        https://core.telegram.org/bots/api#getupdates
        """
        return [
            Update(update)
            for update in await self.post("getUpdates", offset=offset, limit=limit, timeout=timeout)
        ]

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode=ParseMode.default,
        disable_web_page_preview=False,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        params = {"chat_id": chat_id, "text": text}
        if parse_mode != ParseMode.default:
            params["parse_mode"] = parse_mode.value
        if disable_web_page_preview:
            params["disable_web_page_preview"] = disable_web_page_preview
        if reply_to_message_id is not None:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        return Message(await self.post("sendMessage", **params))

    async def edit_message_text(
        self,
        chat_id: Union[None, int, str],
        message_id: Optional[int],
        inline_message_id: Optional[str],
        text: str,
        parse_mode=ParseMode.default,
        disable_web_page_preview=False,
        reply_markup=None,
    ):
        """
        https://core.telegram.org/bots/api#editmessagetext
        """
        params = {"text": text}
        if chat_id:
            params["chat_id"] = chat_id
        if message_id:
            params["message_id"] = message_id
        if inline_message_id:
            params["inline_message_id"] = inline_message_id
        if parse_mode != ParseMode.default:
            params["parse_mode"] = parse_mode.value
        if disable_web_page_preview:
            params["disable_web_page_preview"] = disable_web_page_preview
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        result = await self.post("editMessageText", **params)
        return Message(result) if isinstance(result, dict) else result

    async def send_chat_action(self, chat_id: Union[int, str], action: ChatAction):
        """
        https://core.telegram.org/bots/api#sendchataction
        """
        await self.post("sendChatAction", chat_id=chat_id, action=action.value)

    async def answer_callback_query(self, callback_query_id: str, text=None, show_alert=False):
        """
        https://core.telegram.org/bots/api#answercallbackquery
        """
        params = {"callback_query_id": callback_query_id}
        if text:
            params["text"] = text
        if show_alert:
            params["show_alert"] = show_alert
        return await self.post("answerCallbackQuery", **params)

    async def send_location(
        self,
        chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        disable_notification=False,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        """
        https://core.telegram.org/bots/api#sendlocation
        """
        params = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
        if disable_notification:
            params["disable_notification"] = disable_notification
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            params["reply_markup"] = reply_markup
        return Message(await self.post("sendLocation", **params))

    async def post(self, method: str, **kwargs):
        """
        Posts the request to Telegram Bot API.
        """
        self.logger.debug("%s(%s)", method, kwargs)
        async with self.session.post(self.url.format(method), data=json.dumps(kwargs), headers=self.headers) as response:
            payload = await response.json()
            if payload["ok"]:
                self.logger.debug("%s: %s", method, payload)
                return payload["result"]
            else:
                self.logger.error("%s: %s", method, payload)
                raise TelegramException(payload["description"])

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)


class TelegramException(Exception):
    """
    Raised when Telegram API returns an error. Message contains the error description.
    """

    def __init__(self, message):
        super().__init__(message)


def get_optional(obj: dict, key: str, init: Callable[[Any], T]) -> Optional[T]:
    """
    Helper function to get an optional value from a response object.
    """
    return init(obj[key]) if key in obj else None


def get_optional_array(obj: dict, key: str, init: Callable[[Any], T]) -> Optional[List[T]]:
    """
    Helper function to get an optional array from a response object.
    """
    return [init(item) for item in obj[key]] if key in obj else None
