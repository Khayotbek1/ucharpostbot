import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN
from bot.handlers.admin import admin_router
from bot.scheduler import start_scheduler

print("✅ Bot ishga tushdi... kutyapti...")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin_router)

    asyncio.create_task(start_scheduler(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
