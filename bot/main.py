import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.handlers.admin import admin_router
from bot.config import BOT_TOKEN
from bot.scheduler import start_scheduler

print("✅ Bot ishga tushdi... kutyapti...")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin_router)

    # asyncio.create_task(start_scheduler(bot))
    TASHKENT_TZ = pytz.timezone("Asia/Tashkent")
    scheduler = AsyncIOScheduler(timezone=TASHKENT_TZ)
    scheduler.add_job(
        start_scheduler,
        trigger=CronTrigger(
            hour='8-20',  # 8:00 dan 20:00 gacha
            minute=0,  # Har soatning boshida
            second=0  # Sekund 0 da
        ),
        args = (bot,),
        id='hourly_async_task',
        name='Har soatda ishlaydigan async vazifa'
    )
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
