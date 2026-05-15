import asyncio
import logging
import os
import datetime
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ═══════════════════════════════════════════════════
# НАЛАШТУВАННЯ
# ═══════════════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN", "8632705238:AAGBhG6i1hEIAorOvvj2NYNVL5hSl5dNtO8")
CHANNEL_URL = "https://t.me/nrgcoffee"
BARISTA_CHAT_ID = -1003640317407

# ═══════════════════════════════════════════════════
# МЕНЮ
# ═══════════════════════════════════════════════════

MENU = {
    "espresso":        {"name": "Еспресо",              "sizes": ["S"],     "prices": {"S": 70},            "emoji": "☕", "has_milk": False},
    "doppio":          {"name": "Доппіо",               "sizes": ["S"],     "prices": {"S": 85},            "emoji": "☕", "has_milk": False},
    "americano":       {"name": "Американо",            "sizes": ["M"],     "prices": {"M": 80},            "emoji": "☕", "has_milk": False},
    "filter":          {"name": "Фільтр кава",          "sizes": ["M","L"], "prices": {"M": 90,  "L": 105}, "emoji": "☕", "has_milk": False},
    "flatwhite":       {"name": "Флетвайт",             "sizes": ["M"],     "prices": {"M": 120},           "emoji": "☕", "has_milk": True},
    "cappuccino":      {"name": "Капучино",             "sizes": ["M","L"], "prices": {"M": 95,  "L": 110}, "emoji": "☕", "has_milk": True},
    "latte":           {"name": "Лате",                 "sizes": ["M","L"], "prices": {"M": 100, "L": 115}, "emoji": "☕", "has_milk": True},
    "raf":             {"name": "Раф",                  "sizes": ["M"],     "prices": {"M": 120},           "emoji": "☕", "has_milk": True},
    "kapu_orange":     {"name": "Капуоранж",            "sizes": ["M"],     "prices": {"M": 125},           "emoji": "🍊", "has_milk": True},
    "cocoa":           {"name": "Какао",                "sizes": ["M","L"], "prices": {"M": 90,  "L": 105}, "emoji": "🍫", "has_milk": True},
    "matcha":          {"name": "Матча лате",           "sizes": ["M"],     "prices": {"M": 115},           "emoji": "🍵", "has_milk": True},
    "matcha_or":       {"name": "Матча оранж",          "sizes": ["M"],     "prices": {"M": 135},           "emoji": "🍵", "has_milk": True},
    "tea":             {"name": "Чай",                  "sizes": ["M"],     "prices": {"M": 100},           "emoji": "🍵", "has_milk": False},
    "ice_latte":       {"name": "Айс лате",             "sizes": ["M"],     "prices": {"M": 135},           "emoji": "🧊", "has_milk": True},
    "ice_cocoa":       {"name": "Айс какао",            "sizes": ["M"],     "prices": {"M": 105},           "emoji": "🧊", "has_milk": True},
    "ice_cocoa_or":    {"name": "Айс какао оранж",     "sizes": ["M"],     "prices": {"M": 130},           "emoji": "🧊", "has_milk": True},
    "ice_kapu":        {"name": "Айс капуоранж",        "sizes": ["M"],     "prices": {"M": 135},           "emoji": "🧊", "has_milk": True},
    "ice_matcha":      {"name": "Айс матча",            "sizes": ["M"],     "prices": {"M": 125},           "emoji": "🧊", "has_milk": True},
    "ice_matcha_or":   {"name": "Айс матча оранж",     "sizes": ["M"],     "prices": {"M": 150},           "emoji": "🧊", "has_milk": True},
    "ice_matcha_berry":{"name": "Айс матча ягода",     "sizes": ["M"],     "prices": {"M": 170},           "emoji": "🧊", "has_milk": True},
    "jungle":          {"name": "Джангл Джус",          "sizes": ["M"],     "prices": {"M": 145},           "emoji": "🌿", "has_milk": False},
    "juice_pine":      {"name": "Джусік ананас-кокос", "sizes": ["S"],     "prices": {"S": 35},            "emoji": "🥥", "has_milk": False},
    "espresso_tonic":  {"name": "Еспресо тонік",        "sizes": ["M"],     "prices": {"M": 110},           "emoji": "✨", "has_milk": False},
    "lemonade":        {"name": "Лимонад",              "sizes": ["M"],     "prices": {"M": 115},           "emoji": "🍋", "has_milk": False},
    "mojito":          {"name": "Мохіто б/а",           "sizes": ["M"],     "prices": {"M": 145},           "emoji": "🌿", "has_milk": False},
    "pina":            {"name": "Піна колада б/а",      "sizes": ["M"],     "prices": {"M": 145},           "emoji": "🥥", "has_milk": False},
}

CATEGORIES = {
    "coffee":   {"label": "☕ Кава",         "items": ["espresso","doppio","americano","filter","flatwhite","cappuccino","latte","raf","kapu_orange"]},
    "nocoffee": {"label": "🍵 Без кофеїну", "items": ["cocoa","matcha","matcha_or","tea"]},
    "ice":      {"label": "🧊 Айс",          "items": ["ice_latte","ice_cocoa","ice_cocoa_or","ice_kapu","ice_matcha","ice_matcha_or","ice_matcha_berry","espresso_tonic"]},
    "other":    {"label": "🌿 Інше",         "items": ["lemonade","mojito","pina","jungle","juice_pine"]},
}

POPULAR = ["latte","cappuccino","raf","flatwhite","ice_latte","matcha"]

EXTRAS = {
    "cream":       {"name": "Вершки",         "price": 10},
    "decaf":       {"name": "Декаф",          "price": 10},
    "marshmallow": {"name": "Маршмеллоу",     "price": 25},
    "syrup_van":   {"name": "Сироп ваніль",   "price": 10},
    "syrup_car":   {"name": "Сироп карамель", "price": 10},
    "syrup_nut":   {"name": "Сироп горіх",    "price": 10},
}

MILK_OPTIONS = {
    "regular":     {"name": "🥛 Звичайне",                               "price": 0},
    "bez_lactose": {"name": "🥛 Безлактозне",                            "price": 15},
    "plant":       {"name": "🌿 Рослинне (вівсяне/мигдальне/кокосове)",  "price": 25},
}

EVENTS = [
    {
        "date":  "16 травня, 15:00",
        "title": "Скільки грошей тобі потрібно для стабільності?",
        "desc":  "Юлія Новіцька - фінансовий консультант. Energy Space, Осокорки, ЖК RiverStone",
    },
]

# ═══════════════════════════════════════════════════
# FSM СТАНИ
# ═══════════════════════════════════════════════════

class OrderState(StatesGroup):
    choosing_category = State()
    choosing_item     = State()
    choosing_size     = State()
    choosing_milk     = State()
    choosing_sugar    = State()
    choosing_extras   = State()
    adding_comment    = State()
    confirming        = State()

class FeedbackState(StatesGroup):
    waiting = State()

user_history: dict = {}

# ═══════════════════════════════════════════════════
# КЛАВІАТУРИ
# ═══════════════════════════════════════════════════

def main_menu_kb(has_history=False):
    rows = [[KeyboardButton(text="☕ Замовити каву")]]
    row2 = []
    if has_history:
        row2.append(KeyboardButton(text="🧡 Як завжди"))
    row2.append(KeyboardButton(text="⭐ Популярне"))
    rows.append(row2)
    rows.append([KeyboardButton(text="📅 Анонси подій"), KeyboardButton(text="📢 Наш канал")])
    rows.append([KeyboardButton(text="💬 Залишити відгук")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def categories_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="☕ Кава"), KeyboardButton(text="🍵 Без кофеїну")],
        [KeyboardButton(text="🧊 Айс"), KeyboardButton(text="🌿 Інше")],
        [KeyboardButton(text="← Назад")],
    ], resize_keyboard=True)

def items_kb(cat_key):
    items = CATEGORIES[cat_key]["items"]
    rows = []
    for i in range(0, len(items), 2):
        pair = items[i:i+2]
        row = []
        for key in pair:
            it = MENU[key]
            prices = "/".join(str(v) for v in it["prices"].values())
            row.append(KeyboardButton(text=it["emoji"] + " " + it["name"] + " (" + prices + "₴)"))
        rows.append(row)
    rows.append([KeyboardButton(text="← Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def popular_kb():
    rows = []
    for i in range(0, len(POPULAR), 2):
        pair = POPULAR[i:i+2]
        row = []
        for key in pair:
            it = MENU[key]
            prices = "/".join(str(v) for v in it["prices"].values())
            row.append(KeyboardButton(text=it["emoji"] + " " + it["name"] + " (" + prices + "₴)"))
        rows.append(row)
    rows.append([KeyboardButton(text="← Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def sizes_kb(item_key):
    it = MENU[item_key]
    row = [KeyboardButton(text=("M" if s == "M" else "L") + " — " + str(it["prices"][s]) + "₴") for s in it["sizes"]]
    return ReplyKeyboardMarkup(keyboard=[row, [KeyboardButton(text="← Назад")]], resize_keyboard=True)

def milk_kb():
    rows = [[KeyboardButton(text=v["name"])] for v in MILK_OPTIONS.values()]
    rows.append([KeyboardButton(text="← Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def sugar_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Без цукру")],
        [KeyboardButton(text="1 ч.л."), KeyboardButton(text="2 ч.л."), KeyboardButton(text="3 ч.л.")],
        [KeyboardButton(text="← Назад")],
    ], resize_keyboard=True)

def extras_inline(selected):
    buttons = []
    for key, val in EXTRAS.items():
        check = "✅ " if key in selected else ""
        buttons.append([InlineKeyboardButton(
            text=check + val["name"] + " +" + str(val["price"]) + "₴",
            callback_data="extra_" + key
        )])
    buttons.append([InlineKeyboardButton(text="Далі →", callback_data="extras_done")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def comment_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✍️ Додати коментар")],
        [KeyboardButton(text="Без коментаря →")],
        [KeyboardButton(text="← Назад")],
    ], resize_keyboard=True)

def confirm_inline():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_order"),
        InlineKeyboardButton(text="✏️ Змінити",    callback_data="edit_order"),
    ]])

def channel_inline():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📢 Підписатись на канал", url=CHANNEL_URL)
    ]])

def back_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="← На головну")]], resize_keyboard=True)

# ═══════════════════════════════════════════════════
# ХЕЛПЕРИ
# ═══════════════════════════════════════════════════

def calc_price(order):
    item = MENU.get(order.get("item", ""))
    if not item:
        return 0
    size = order.get("size", list(item["prices"].keys())[0])
    price = item["prices"].get(size, list(item["prices"].values())[0])
    milk_key = order.get("milk")
    if milk_key and milk_key in MILK_OPTIONS:
        price += MILK_OPTIONS[milk_key]["price"]
    for e in order.get("extras", []):
        if e in EXTRAS:
            price += EXTRAS[e]["price"]
    return price

def order_summary(order):
    item = MENU.get(order.get("item", ""))
    if not item:
        return "Замовлення порожнє"
    size = order.get("size", list(item["prices"].keys())[0])
    size_label = "M" if size == "M" else "L"
    lines = [item["emoji"] + " <b>" + item["name"] + "</b> (" + size_label + ")"]
    milk_key = order.get("milk")
    if milk_key and milk_key in MILK_OPTIONS:
        lines.append("🥛 " + MILK_OPTIONS[milk_key]["name"])
    sugar = order.get("sugar", 0)
    lines.append("🍬 " + ("Без цукру" if sugar == 0 else str(sugar) + " ч.л. цукру"))
    extras = order.get("extras", [])
    if extras:
        lines.append("✨ " + ", ".join(EXTRAS[e]["name"] for e in extras if e in EXTRAS))
    comment = order.get("comment", "")
    if comment:
        lines.append("💬 " + comment)
    lines.append("\n💳 <b>" + str(calc_price(order)) + "₴</b>")
    return "\n".join(lines)

def find_item_by_text(text):
    for key, item in MENU.items():
        if text.startswith(item["emoji"] + " " + item["name"]):
            return key
    return None

def get_event_block():
    if not EVENTS:
        return ""
    ev = EVENTS[0]
    return "\n\n📅 <b>Найближча подія:</b>\n<b>" + ev["title"] + "</b>\n🕐 " + ev["date"] + "\n" + ev["desc"]

CAT_LABEL_MAP = {"☕ Кава": "coffee", "🍵 Без кофеїну": "nocoffee", "🧊 Айс": "ice", "🌿 Інше": "other"}
MILK_TEXT_MAP  = {v["name"]: k for k, v in MILK_OPTIONS.items()}
SUGAR_MAP      = {"Без цукру": 0, "1 ч.л.": 1, "2 ч.л.": 2, "3 ч.л.": 3}

# ═══════════════════════════════════════════════════
# ХЕНДЛЕРИ
# ═══════════════════════════════════════════════════

router = Router()

@router.message(Command("chatid"))
async def cmd_chatid(message: Message):
    await message.answer("Chat ID цього чату: " + str(message.chat.id))

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await message.answer(
        "Привіт! 👋 Це бот <b>Energy Space</b>.\n\n"
        "Поки ти йдеш у ліфті — твоя кава вже готується ☕\n\n"
        "Тут ти можеш:\n"
        "• <b>Замовити каву</b> за 2–3 кліки\n"
        "• Дізнатись про <b>найближчі події</b> у нашому просторі\n"
        "• Підписатись на наш <b>Telegram-канал</b>"
        + get_event_block(),
        parse_mode="HTML",
        reply_markup=main_menu_kb(uid in user_history)
    )
    await message.answer(
        "📢 Підписуйся на наш канал — анонси подій, реєстрація на заходи, нові напої та акції:",
        reply_markup=channel_inline()
    )

@router.message(F.text == "← На головну")
async def go_home(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await message.answer(
        "Головне меню ☕" + get_event_block(),
        parse_mode="HTML",
        reply_markup=main_menu_kb(uid in user_history)
    )

@router.message(F.text == "⭐ Популярне")
async def show_popular(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderState.choosing_item)
    await state.update_data(category="popular")
    await message.answer("Ось що найчастіше замовляють:", reply_markup=popular_kb())

@router.message(F.text == "🧡 Як завжди")
async def repeat_order(message: Message, state: FSMContext):
    uid = message.from_user.id
    history = user_history.get(uid)
    if not history:
        await message.answer("Ще немає збереженого замовлення. Зроби перше! ☕")
        return
    await state.update_data(**history)
    await state.set_state(OrderState.confirming)
    await message.answer(
        "🧡 Повторюю твоє замовлення:\n\n" + order_summary(history),
        parse_mode="HTML", reply_markup=confirm_inline()
    )

@router.message(F.text == "📅 Анонси подій")
async def show_events(message: Message):
    if not EVENTS:
        await message.answer("Найближчих подій поки немає 🙂", reply_markup=channel_inline())
        return
    lines = ["📅 <b>Найближчі події в Energy Space:</b>\n"]
    for ev in EVENTS:
        lines.append("<b>" + ev["title"] + "</b>\n🕐 " + ev["date"] + "\n" + ev["desc"] + "\n")
    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=back_kb())
    await message.answer(
        "📢 Підписуйся на наш канал — анонси подій, реєстрація на заходи, нові напої та акції:",
        reply_markup=channel_inline()
    )

@router.message(F.text == "📢 Наш канал")
async def show_channel(message: Message):
    await message.answer(
        "📢 <b>Energy Space</b> у Telegram\n\n"
        "Там ми публікуємо:\n"
        "• Анонси подій і майстер-класів\n"
        "• Реєстрація на заходи\n"
        "• Нові напої в меню\n"
        "• Акції та знижки",
        parse_mode="HTML", reply_markup=channel_inline()
    )

@router.message(F.text == "💬 Залишити відгук")
async def ask_feedback(message: Message, state: FSMContext):
    await state.set_state(FeedbackState.waiting)
    await message.answer(
        "💬 Напиши свій відгук — ми читаємо все 🤍\n\n<i>Що сподобалось? Що покращити?</i>",
        parse_mode="HTML", reply_markup=back_kb()
    )

@router.message(FeedbackState.waiting)
async def receive_feedback(message: Message, state: FSMContext):
    if message.text == "← На головну":
        await state.clear()
        uid = message.from_user.id
        await message.answer(
            "Головне меню ☕" + get_event_block(),
            parse_mode="HTML",
            reply_markup=main_menu_kb(uid in user_history)
        )
        return
    await state.clear()
    uid = message.from_user.id
    await message.answer("✅ Дякуємо за відгук! 🧡", reply_markup=main_menu_kb(uid in user_history))

@router.message(F.text == "☕ Замовити каву")
async def start_order(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderState.choosing_category)
    await message.answer("Що будемо пити? Обирай категорію:", reply_markup=categories_kb())

@router.message(OrderState.choosing_category)
async def choose_category(message: Message, state: FSMContext):
    if message.text == "← Назад":
        await state.clear()
        uid = message.from_user.id
        await message.answer(
            "Головне меню ☕" + get_event_block(),
            parse_mode="HTML",
            reply_markup=main_menu_kb(uid in user_history)
        )
        return
    cat_key = CAT_LABEL_MAP.get(message.text)
    if not cat_key:
        await message.answer("Обери категорію з кнопок 👇")
        return
    await state.update_data(category=cat_key)
    await state.set_state(OrderState.choosing_item)
    await message.answer("Обирай напій:", reply_markup=items_kb(cat_key))

@router.message(OrderState.choosing_item)
async def choose_item(message: Message, state: FSMContext):
    if message.text == "← Назад":
        await state.set_state(OrderState.choosing_category)
        await message.answer("Обирай категорію:", reply_markup=categories_kb())
        return
    item_key = find_item_by_text(message.text)
    if not item_key:
        await message.answer("Обери напій з кнопок 👇")
        return
    await state.update_data(item=item_key, extras=[])
    item = MENU[item_key]
    if len(item["sizes"]) > 1:
        await state.set_state(OrderState.choosing_size)
        await message.answer(item["emoji"] + " " + item["name"] + ". Який розмір?", reply_markup=sizes_kb(item_key))
    else:
        await state.update_data(size=item["sizes"][0])
        if item["has_milk"]:
            await state.set_state(OrderState.choosing_milk)
            await message.answer("Яке молоко?", reply_markup=milk_kb())
        else:
            await state.set_state(OrderState.choosing_sugar)
            await message.answer("Цукор?", reply_markup=sugar_kb())

@router.message(OrderState.choosing_size)
async def choose_size(message: Message, state: FSMContext):
    if message.text == "← Назад":
        data = await state.get_data()
        cat = data.get("category", "coffee")
        await state.set_state(OrderState.choosing_item)
        kb = popular_kb() if cat == "popular" else items_kb(cat)
        await message.answer("Обирай напій:", reply_markup=kb)
        return
    size_key = "M" if message.text.startswith("M") else "L" if message.text.startswith("L") else None
    if not size_key:
        await message.answer("Обери розмір з кнопок 👇")
        return
    await state.update_data(size=size_key)
    data = await state.get_data()
    item = MENU[data["item"]]
    if item["has_milk"]:
        await state.set_state(OrderState.choosing_milk)
        await message.answer("Яке молоко?", reply_markup=milk_kb())
    else:
        await state.set_state(OrderState.choosing_sugar)
        await message.answer("Цукор?", reply_markup=sugar_kb())

@router.message(OrderState.choosing_milk)
async def choose_milk(message: Message, state: FSMContext):
    if message.text == "← Назад":
        data = await state.get_data()
        item = MENU[data["item"]]
        if len(item["sizes"]) > 1:
            await state.set_state(OrderState.choosing_size)
            await message.answer("Який розмір?", reply_markup=sizes_kb(data["item"]))
        else:
            cat = data.get("category", "coffee")
            await state.set_state(OrderState.choosing_item)
            await message.answer("Обирай напій:", reply_markup=popular_kb() if cat == "popular" else items_kb(cat))
        return
    milk_key = MILK_TEXT_MAP.get(message.text)
    if not milk_key:
        await message.answer("Обери молоко з кнопок 👇")
        return
    await state.update_data(milk=milk_key)
    await state.set_state(OrderState.choosing_sugar)
    await message.answer("Цукор?", reply_markup=sugar_kb())

@router.message(OrderState.choosing_sugar)
async def choose_sugar(message: Message, state: FSMContext):
    if message.text == "← Назад":
        data = await state.get_data()
        item = MENU[data["item"]]
        if item["has_milk"]:
            await state.set_state(OrderState.choosing_milk)
            await message.answer("Яке молоко?", reply_markup=milk_kb())
        else:
            await state.set_state(OrderState.choosing_size)
            await message.answer("Який розмір?", reply_markup=sizes_kb(data["item"]))
        return
    sugar = SUGAR_MAP.get(message.text)
    if sugar is None:
        await message.answer("Обери варіант з кнопок 👇")
        return
    await state.update_data(sugar=sugar)
    await state.set_state(OrderState.choosing_extras)
    data = await state.get_data()
    await message.answer("Додатки (можна кілька або натисни Далі):", reply_markup=extras_inline(data.get("extras", [])))

@router.callback_query(F.data.startswith("extra_"), OrderState.choosing_extras)
async def toggle_extra(cb: CallbackQuery, state: FSMContext):
    key = cb.data.replace("extra_", "")
    data = await state.get_data()
    extras = data.get("extras", [])
    if key in extras:
        extras.remove(key)
    else:
        extras.append(key)
    await state.update_data(extras=extras)
    await cb.message.edit_reply_markup(reply_markup=extras_inline(extras))
    await cb.answer()

@router.callback_query(F.data == "extras_done", OrderState.choosing_extras)
async def extras_done(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await state.set_state(OrderState.adding_comment)
    await cb.message.answer(
        "✍️ Додай коментар до замовлення\n<i>Наприклад: додайте кориці або буду за 10 хвилин</i>",
        parse_mode="HTML", reply_markup=comment_kb()
    )
    await cb.answer()

@router.message(OrderState.adding_comment)
async def add_comment(message: Message, state: FSMContext):
    if message.text == "← Назад":
        data = await state.get_data()
        await state.set_state(OrderState.choosing_extras)
        await message.answer("Додатки:", reply_markup=extras_inline(data.get("extras", [])))
        return
    if message.text == "✍️ Додати коментар":
        await message.answer("Напиши коментар у наступному повідомленні:")
        return
    comment = "" if message.text == "Без коментаря →" else message.text
    await state.update_data(comment=comment)
    await state.set_state(OrderState.confirming)
    data = await state.get_data()
    await message.answer(
        "Твоє замовлення:\n\n" + order_summary(data),
        parse_mode="HTML", reply_markup=confirm_inline()
    )

@router.callback_query(F.data == "confirm_order", OrderState.confirming)
async def confirm_order(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_history[cb.from_user.id] = dict(data)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        "✅ <b>Замовлення прийнято!</b>\n\n"
        "☕️ Починаємо варити твою каву.\n"
        "Готово через: <b>3–5 хв</b>\n\n"
        "⏳ Статус: <i>Готується...</i>",
        parse_mode="HTML", reply_markup=back_kb()
    )
    await cb.message.answer(
        "Поки чекаєш — підписуйся на наш канал 🧡",
        reply_markup=channel_inline()
    )
    # Сповіщення баристі
    try:
        time_now = datetime.datetime.now().strftime("%H:%M")
        barista_text = "☕ НОВЕ ЗАМОВЛЕННЯ!\n\n" + order_summary(data) + "\n\n⏰ " + time_now
        await cb.bot.send_message(BARISTA_CHAT_ID, barista_text, parse_mode="HTML")
    except Exception as e:
        logging.error("Barista notification error: " + str(e))
    await state.clear()
    await cb.answer("Замовлення прийнято! ☕")

@router.callback_query(F.data == "edit_order", OrderState.confirming)
async def edit_order(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup(reply_markup=None)
    await state.set_state(OrderState.choosing_category)
    await cb.message.answer("Починаємо заново. Обери категорію:", reply_markup=categories_kb())
    await cb.answer()

# ═══════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Бот запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
