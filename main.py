import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

from config import config
from handlers.basic import router as basic_router
from handlers.ranobe import router as novel_router

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
session = AiohttpSession(
    api=TelegramAPIServer.from_base('http://api:8081', is_local=True)
)


async def main():
    bot = Bot(config.bot_token.get_secret_value(), session=session)
    dp = Dispatcher()

    logger.info("Bot started.")
    dp.include_router(basic_router)
    dp.include_router(novel_router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
