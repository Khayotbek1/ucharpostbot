import json
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.storage import load_products, save_products
from aiogram.filters import Command
from bot.filters.admin_filter import AdminFilter

admin_router = Router()

admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())

@admin_router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Assalomu alaykum!", reply_markup=menu_buttons())

@admin_router.callback_query(F.data == "add")
async def callback_add_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProductFSM.waiting_for_title)
    await callback.message.edit_text("Mahsulot nomini kiriting:", reply_markup=bosh_menu_button())
    await callback.answer()

@admin_router.callback_query(F.data == "view")
async def callback_view_products(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProductEditFSM.waiting_for_product_id_or_name)
    await callback.message.answer("Mahsulot nomi yoki ID sini kiriting:", reply_markup=bosh_menu_button())
    await callback.answer()


class ProductFSM(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_monthly_3 = State()
    waiting_for_monthly_6 = State()
    waiting_for_monthly_12 = State()
    waiting_for_photo = State()


class ProductEditFSM(StatesGroup):
    waiting_for_product_id_or_name = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_photo = State()

@admin_router.message(F.text.lower() == "mahsulotlar")
async def ask_for_product_id_or_name(message: Message, state: FSMContext):
    await state.set_state(ProductEditFSM.waiting_for_product_id_or_name)
    await message.answer("Mahsulot nomi yoki ID sini kiriting:", reply_markup=bosh_menu_button())

@admin_router.message(ProductEditFSM.waiting_for_product_id_or_name)
async def show_product_by_id_or_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Faqat matn ko'rinishida yuboring!")
        return
    user_input = message.text.strip()
    products = load_products()

    product = None
    for p in products:
        if str(p.get('id')) == user_input or p.get('title', '').lower() == user_input.lower():
            product = p
            break

    if not product:
        await message.answer("Mahsulot topilmadi. Qaytadan urinib ko‘ring.", reply_markup=bosh_menu_button())
        return

    await state.update_data(product=product, products=products)

    text = f"🛒 <b>{product['title']}</b>\n\n{product['description']}\n\n💰 Narxi: <b>{product['price']}</b> so'm"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_{product['id']}"),
            InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"delete_{product['id']}")
        ],
        [InlineKeyboardButton(text="🏠 Bosh menu", callback_data="main_menu")]
    ])
    await message.answer_photo(photo=product["photo"], caption=text, reply_markup=keyboard, parse_mode="HTML")

@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    products = load_products()
    updated_products = [p for p in products if p['id'] != product_id]
    save_products(updated_products)
    await callback.message.edit_caption("✅ Mahsulot o‘chirildi.", reply_markup=bosh_menu_button())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("edit_"))
async def start_editing(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        await callback.answer("Mahsulot topilmadi.", show_alert=True)
        return

    await state.update_data(product=product, products=products)
    await state.set_state(ProductEditFSM.waiting_for_title)
    await callback.message.answer("Yangi nomini kiriting:", reply_markup=bosh_menu_button())
    await callback.answer()

@admin_router.message(ProductEditFSM.waiting_for_title)
async def update_title(message: Message, state: FSMContext):
    await state.update_data(new_title=message.text)
    await state.set_state(ProductEditFSM.waiting_for_description)
    await message.answer("Yangi tavsifni kiriting:", reply_markup=bosh_menu_button())

@admin_router.message(ProductEditFSM.waiting_for_description)
async def update_description(message: Message, state: FSMContext):
    await state.update_data(new_description=message.text)
    await state.set_state(ProductEditFSM.waiting_for_price)
    await message.answer("Yangi narxni kiriting:", reply_markup=bosh_menu_button())

@admin_router.message(ProductEditFSM.waiting_for_price)
async def update_price(message: Message, state: FSMContext):
    await state.update_data(new_price=message.text)
    await state.set_state(ProductEditFSM.waiting_for_photo)
    await message.answer("Yangi rasmni yuboring:", reply_markup=bosh_menu_button())

@admin_router.message(ProductEditFSM.waiting_for_photo)
async def update_photo(message: Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer("Iltimos, rasm yuboring!")
        return

    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    product = data['product']
    products = data['products']

    product['title'] = data['new_title']
    product['description'] = data['new_description']
    product['price'] = data['new_price']
    product['photo'] = photo_file_id

    save_products(products)
    await state.clear()
    await message.answer("✅ Mahsulot tahrirlandi.", reply_markup=bosh_menu_button())

@admin_router.message(F.text.lower() == "mahsulot qo‘shish")
async def add_product_start(message: Message, state: FSMContext):
    await state.set_state(ProductFSM.waiting_for_title)
    await message.answer("Mahsulot nomini kiriting:", reply_markup=bosh_menu_button())

@admin_router.message(ProductFSM.waiting_for_title)
async def add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ProductFSM.waiting_for_description)
    await message.answer("Tavsifni kiriting:")

@admin_router.message(ProductFSM.waiting_for_description)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ProductFSM.waiting_for_price)
    await message.answer("Narxni kiriting:")

@admin_router.message(ProductFSM.waiting_for_price)
async def add_price(message: Message, state: FSMContext):
    if not message.text.replace(" ", "").isdigit():
        await message.answer("Narx faqat son bo‘lishi kerak.")
        return

    price = int(message.text.replace(" ", ""))
    await state.update_data(price=price)
    await state.set_state(ProductFSM.waiting_for_monthly_3)
    await message.answer("3 oylik to‘lovni kiriting:")

@admin_router.message(ProductFSM.waiting_for_monthly_3)
async def add_monthly_3(message: Message, state: FSMContext):
    if not message.text.replace(" ", "").isdigit():
        await message.answer("Iltimos, faqat son kiriting.")
        return

    await state.update_data(monthly_3=int(message.text.replace(" ", "")))
    await state.set_state(ProductFSM.waiting_for_monthly_6)
    await message.answer("6 oylik to‘lovni kiriting:")


@admin_router.message(ProductFSM.waiting_for_monthly_6)
async def add_monthly_6(message: Message, state: FSMContext):
    if not message.text.replace(" ", "").isdigit():
        await message.answer("Iltimos, faqat son kiriting.")
        return

    await state.update_data(monthly_6=int(message.text.replace(" ", "")))
    await state.set_state(ProductFSM.waiting_for_monthly_12)
    await message.answer("12 oylik to‘lovni kiriting:")


@admin_router.message(ProductFSM.waiting_for_monthly_12)
async def add_monthly_12(message: Message, state: FSMContext):
    if not message.text.replace(" ", "").isdigit():
        await message.answer("Iltimos, faqat son kiriting.")
        return

    await state.update_data(monthly_12=int(message.text.replace(" ", "")))
    await state.set_state(ProductFSM.waiting_for_photo)
    await message.answer("Rasmni yuboring:")



@admin_router.message(ProductFSM.waiting_for_photo)
async def add_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Iltimos, rasm yuboring.")
        return

    data = await state.get_data()
    products = load_products()

    new_id = (products[-1]['id'] + 1) if products else 1
    new_product = {
        "id": new_id,
        "title": data['title'],
        "description": data['description'],
        "price": data['price'],
        "monthly_3": data['monthly_3'],
        "monthly_6": data['monthly_6'],
        "monthly_12": data['monthly_12'],
        "photo": message.photo[-1].file_id
    }
    products.append(new_product)
    save_products(products)

    await message.answer("✅ Mahsulot qo‘shildi.", reply_markup=bosh_menu_button())
    await state.clear()


@admin_router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=menu_buttons())
    await callback.answer()

def bosh_menu_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Bosh menu", callback_data="main_menu")]
    ])

def menu_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Mahsulot qo‘shish", callback_data="add")],
        [InlineKeyboardButton(text="📦 Mahsulotlar", callback_data="view")]
    ])
