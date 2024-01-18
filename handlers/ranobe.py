import re

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from config import config
from data.states import CurrentState
from utils.info import verify_book_folder, get_files
from utils.parse import concat_to_epub

router = Router(name="ranobe-parser")


@router.message()
async def download_novel(message: Message, state: FSMContext):
    pattern = config.regex
    if re.fullmatch(pattern, message.text):
        if verify_book_folder(message.text):
            print("book already parsed")
            filepaths = get_files(message.text)
            for f in filepaths:
                fin = FSInputFile(f)
                await message.reply_document(document=fin)
            await state.set_state(CurrentState.available)
        else:
            await message.reply("Начинаю сбор глав в файлы формата ePub...")
            await state.set_state(CurrentState.in_progress)
            filepaths = concat_to_epub(message.text)
            for f in filepaths:
                fin = FSInputFile(f)
                await message.reply_document(document=fin)
            await state.set_state(CurrentState.available)
            await state.set_state(CurrentState.in_progress)
    else:
        await message.reply(text="Incorrect format of URL")
        await state.set_state(CurrentState.available)
