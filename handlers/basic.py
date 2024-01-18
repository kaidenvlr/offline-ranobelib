from contextlib import suppress
from textwrap import dedent

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from utils.consts import START_MESSAGE, STOP_MESSAGE

router = Router(name="basic-commands")


@router.message(Command("start"))
async def cmd_start(message: Message):
    with suppress(TelegramBadRequest):
        await message.answer(dedent(START_MESSAGE))


@router.message(Command("stop"))
async def cmd_stop(message: Message):
    with suppress(TelegramBadRequest):
        await message.answer(dedent(STOP_MESSAGE))
