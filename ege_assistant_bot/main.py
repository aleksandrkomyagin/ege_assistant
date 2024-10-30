import asyncio
import logging

from aiogram import Bot

from commands.menu import menu
from config.config import config
from dispatcher.dispatcher import create_dispatcher

logger = logging.getLogger("bot")


async def start():
    bot = Bot(token=config.tg_bot.token)
    dp = await create_dispatcher(config)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(menu)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Start bot")
    asyncio.run(start())
