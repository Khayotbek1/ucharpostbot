import asyncio
from aiogram import Bot
from bot.utils.storage import load_products
from bot.config import CHANNEL_ID

counter = 0

def format_price(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return "Noma'lum"

async def start_scheduler(bot: Bot):
    global counter
    while True:
        products = load_products()
        if not products:
            await asyncio.sleep(3600)
            continue

        product = products[counter % len(products)]
        counter += 1

        # Mahsulot ma'lumotlari
        title = product.get("title", "Nomsiz mahsulot")
        description = product.get("description", "")
        photo = product.get("photo")
        price = format_price(product.get("price"))

        installment_3 = format_price(product.get("installment_3"))
        installment_6 = format_price(product.get("installment_6"))
        installment_12 = format_price(product.get("installment_12"))

        # Matnni yig'ish
        text = (
            f"🆔 <b>{product['id']}</b>\n\n"
            f"🛒 <b>{product['title']}</b>\n\n"
            f"{product['description']}\n\n"
            f"💰 Narxi: <b>{product.get('price', 'Nomalum')} so'm</b>\n\n"
            f"📆 To‘lovlar:\n"
            f"▫️ 3 oyga: <b>{product.get('monthly_3', 'Nomalum')} so'm</b>\n"
            f"▫️ 6 oyga: <b>{product.get('monthly_6', 'Nomalum')} so'm</b>\n"
            f"▫️ 12 oyga: <b>{product.get('monthly_12', 'Nomalum')} so'm</b>"
        )

        try:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=text,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"❌ Post yuborishda xatolik: {e}")

        await asyncio.sleep(3600)  # 1 soat kutish
