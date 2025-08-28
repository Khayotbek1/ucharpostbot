import asyncio
from datetime import datetime, timedelta
import pytz
from aiogram import Bot
from bot.utils.storage import load_products
from bot.config import CHANNEL_ID

# Mahsulot indexini saqlash
counter = 0

# Tashkent timezone
TASHKENT_TZ = pytz.timezone("Asia/Tashkent")


def format_price(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return "Noma'lum"


async def start_scheduler(bot: Bot):
    global counter
    while True:
        now = datetime.now(TASHKENT_TZ)
        hour = now.hour

        # Faqat 08:00 - 20:00 oralig'ida ishlaydi
        if 8 <= hour <= 20:
            products = load_products()
            if not products:
                # Mahsulot bo'lmasa keyingi soatgacha kutadi
                next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                wait_seconds = (next_hour - datetime.now(TASHKENT_TZ)).total_seconds()
                await asyncio.sleep(wait_seconds)
                continue

            product = products[counter % len(products)]
            counter += 1

            title = product.get("title", "Nomsiz mahsulot")
            description = product.get("description", "")
            photo = product.get("photo")
            price = format_price(product.get("price"))

            installment_3 = format_price(product.get("monthly_3"))
            installment_6 = format_price(product.get("monthly_6"))
            installment_12 = format_price(product.get("monthly_12"))

            text = (
                f"🆔 <b>{product['id']}</b>\n\n"
                f"🛒 <b>{title}</b>\n\n"
                f"{description}\n\n"
                f"💰 Narxi: <b>{price} so'm</b>\n\n"
                f"📆 To‘lovlar:\n"
                f"▫️ 3 oyga: <b>{installment_3} so'm</b>\n"
                f"▫️ 6 oyga: <b>{installment_6} so'm</b>\n"
                f"▫️ 12 oyga: <b>{installment_12} so'm</b>\n\n"
                f"🧑‍💻 Murojat uchun: @ucharmarket_admin1"
            )

            try:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo,
                    caption=text,
                    parse_mode="HTML"
                )
                print(f"✅ {hour}:00 dagi post yuborildi ({title})")
            except Exception as e:
                print(f"❌ Post yuborishda xatolik: {e}")

            # Keyingi soat boshigacha kutish
            next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            wait_seconds = (next_hour - datetime.now(TASHKENT_TZ)).total_seconds()
            await asyncio.sleep(wait_seconds)

        else:
            # 20:00 dan keyin ertasi 08:00 gacha kutadi
            if hour >= 20:
                next_start = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            else:  # 08:00 dan oldin
                next_start = now.replace(hour=8, minute=0, second=0, microsecond=0)

            wait_seconds = (next_start - now).total_seconds()
            print(f"⏸️ Postlash vaqt oralig'ida emas ({hour}:00). {wait_seconds/3600:.1f} soat kutadi...")
            await asyncio.sleep(wait_seconds)
