from aiogram import Bot, Dispatcher
from aiogram.utils.executor import Executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

try:
    from . import config
except ImportError:
    import config


storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
# dp.middleware.setup(LoggingMiddleware())
executor = Executor(dp, skip_updates=config.SKIP_UPDATES)

