import asyncio
import os
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# 🔑 Отримуємо токен зі змінних оточення (Variables в Railway)
BOT_TOKEN = os.getenv("8521645193:AAEzg-qS9O3nuK-ZLVrHXlTfkaWlVbgktUQ")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

REGION_ALARM_STATUS = {}

# Список областей та міст
DATA = {
    "Вінницька область": ["Вінниця", "Жмеринка", "Могилів-Подільський", "Хмільник", "Вся область"],
    "Волинська область": ["Луцьк", "Ковель", "Нововолинськ", "Володимир", "Вся область"],
    "Дніпропетровська область": ["Дніпро", "Кривий Ріг", "Кам'янське", "Нікополь", "Павлоград", "Вся область"],
    "Донецька область": ["Краматорськ", "Слов'янськ", "Покровськ", "Бахмут", "Вся область"],
    "Житомирська область": ["Житомир", "Бердичів", "Коростень", "Новоград-Волинський", "Вся область"],
    "Закарпатська область": ["Ужгород", "Мукачево", "Хуст", "Берегове", "Вся область"],
    "Запорізька область": ["Запоріжжя", "Мелітополь", "Бердянськ", "Вся область"],
    "Івано-Франківська область": ["Івано-Франківськ", "Калуш", "Коломия", "Вся область"],
    "Київська область": ["Біла Церква", "Бровари", "Бориспіль", "Ірпінь", "Буча", "Фастів", "Вся область"],
    "м. Київ": ["м. Київ"],
    "Кіровоградська область": ["Кропивницький", "Олександрія", "Світловодськ", "Вся область"],
    "Луганська область": ["Сєвєродонецьк", "Лисичанськ", "Вся область"],
    "Львівська область": ["Львів", "Дрогобич", "Стрий", "Самбір", "Червоноград", "Вся область"],
    "Миколаївська область": ["Миколаїв", "Первомайськ", "Вознесенськ", "Южноукраїнськ", "Вся область"],
    "Одеська область": ["Одеса", "Чорноморськ", "Ізмаїл", "Подільськ", "Білгород-Дністровський", "Вся область"],
    "Полтавська область": ["Полтава", "Кременчук", "Лубни", "Миргород", "Вся область"],
    "Рівненська область": ["Рівне", "Вараш", "Дубно", "Сарни", "Вся область"],
    "Сумська область": ["Суми", "Конотоп", "Шостка", "Охтирка", "Ромни", "Вся область"],
    "Тернопільська область": ["Тернопіль", "Чортків", "Кременець", "Вся область"],
    "Харківська область": ["Харків", "Ізюм", "Лозова", "Куп'янськ", "Чугуїв", "Вся область"],
    "Херсонська область": ["Херсон", "Нова Каховка", "Олешки", "Вся область"],
    "Хмельницька область": ["Хмельницький", "Кам'янець-Подільський", "Шепетівка", "Вся область"],
    "Черкаська область": ["Черкаси", "Умань", "Сміла", "Золотоноша", "Вся область"],
    "Чернівецька область": ["Чернівці", "Новодністровськ", "Вся область"],
    "Чернігівська область": ["Чернігів", "Ніжин", "Прилуки", "Вся область"],
    "АР Крим": ["Сімферополь", "Севастополь", "Ялта", "Вся область"]
}

# Карта сусідніх областей
NEIGHBORS = {
    "Вінницька область": ["Житомирська область", "Київська область", "Черкаська область", "Кіровоградська область", "Одеська область", "Хмельницька область", "Чернівецька область"],
    "Волинська область": ["Рівненська область", "Львівська область"],
    "Дніпропетровська область": ["Полтавська область", "Харківська область", "Донецька область", "Запорізька область", "Херсонська область", "Миколаївська область", "Кіровоградська область"],
    "Донецька область": ["Харківська область", "Дніпропетровська область", "Запорізька область", "Луганська область"],
    "Житомирська область": ["Київська область", "Вінницька область", "Хмельницька область", "Рівненська область"],
    "Закарпатська область": ["Львівська область", "Івано-Франківська область"],
    "Запорізька область": ["Дніпропетровська область", "Донецька область", "Херсонська область"],
    "Івано-Франківська область": ["Закарпатська область", "Львівська область", "Тернопільська область", "Чернівецька область"],
    "Київська область": ["Чернігівська область", "Полтавська область", "Черкаська область", "Вінницька область", "Житомирська область", "м. Київ"],
    "м. Київ": ["Київська область"],
    "Кіровоградська область": ["Черкаська область", "Полтавська область", "Дніпропетровська область", "Миколаївська область", "Одеська область", "Вінницька область"],
    "Луганська область": ["Харківська область", "Донецька область"],
    "Львівська область": ["Волинська область", "Рівненська область", "Тернопільська область", "Івано-Франківська область", "Закарпатська область"],
    "Миколаївська область": ["Одеська область", "Кіровоградська область", "Дніпропетровська область", "Херсонська область"],
    "Одеська область": ["Вінницька область", "Кіровоградська область", "Миколаївська область"],
    "Полтавська область": ["Сумська область", "Харківська область", "Дніпропетровська область", "Кіровоградська область", "Черкаська область", "Київська область", "Чернігівська область"],
    "Рівненська область": ["Житомирська область", "Хмельницька область", "Тернопільська область", "Львівська область", "Волинська область"],
    "Сумська область": ["Чернігівська область", "Полтавська область", "Харківська область"],
    "Тернопільська область": ["Рівненська область", "Хмельницька область", "Чернівецька область", "Івано-Франківська область", "Львівська область"],
    "Харківська область": ["Сумська область", "Полтавська область", "Дніпропетровська область", "Донецька область", "Луганська область"],
    "Херсонська область": ["Миколаївська область", "Дніпропетровська область", "Запорізька область", "АР Крим"],
    "Хмельницька область": ["Рівненська область", "Житомирська область", "Вінницька область", "Чернівецька область", "Тернопільська область"],
    "Черкаська область": ["Київська область", "Полтавська область", "Кіровоградська область", "Вінницька область"],
    "Чернівецька область": ["Івано-Франківська область", "Тернопільська область", "Хмельницька область", "Вінницька область"],
    "Чернігівська область": ["Сумська область", "Полтавська область", "Київська область"],
    "АР Крим": ["Херсонська область"]
}

# --- БАЗА ДАНИХ ---
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            region TEXT,
            city TEXT
        )
    """)
    conn.commit()
    conn.close()

def set_user_location(user_id: int, region: str, city: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, region, city) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET region=excluded.region, city=excluded.city
    """, (user_id, region, city))
    conn.commit()
    conn.close()

def get_users_by_region(region: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    if region == "ALL":
        cursor.execute("SELECT user_id FROM users")
    else:
        cursor.execute("SELECT user_id FROM users WHERE region = ? OR region = 'ALL'", (region,))
    users = cursor.fetchall()
    conn.close()
    return list(set([u[0] for u in users]))

# --- КЛАВІАТУРИ ---
def get_regions_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🇺🇦 Усі області (Вся Україна)", callback_data="reg_all")]
    ]
    regions_list = list(DATA.keys())
    for i in range(0, len(regions_list), 2):
        row = [InlineKeyboardButton(text=regions_list[i], callback_data=f"reg:{i}")]
        if i + 1 < len(regions_list):
            row.append(InlineKeyboardButton(text=regions_list[i+1], callback_data=f"reg:{i+1}"))
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cities_keyboard(region_idx: int):
    region_name = list(DATA.keys())[region_idx]
    cities = DATA[region_name]
    buttons = []
    for i in range(0, len(cities), 2):
        row = [InlineKeyboardButton(text=cities[i], callback_data=f"city:{region_idx}:{i}")]
        if i + 1 < len(cities):
            row.append(InlineKeyboardButton(text=cities[i+1], callback_data=f"city:{region_idx}:{i+1}"))
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="⬅️ Назад до областей", callback_data="back_to_regions")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- ХЕНДЛЕРИ КОМАНД ТА КНОПОК ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 **Вітаю!**\n\nОбери свою **область** зі списку нижче або вибери **Усі області**:",
        reply_markup=get_regions_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "reg_all")
async def select_all_regions(callback: types.CallbackQuery):
    set_user_location(callback.from_user.id, "ALL", "Усі міста")
    await callback.answer()
    await callback.message.edit_text(
        "✅ **Успішно обрано:** 🇺🇦 Усі області України!\n\n"
        "Тепер ти отримуватимеш сповіщення про тривоги в усіх регіонах.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Змінити вибір", callback_data="back_to_regions")]
        ]),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("reg:"))
async def select_region(callback: types.CallbackQuery):
    region_idx = int(callback.data.split(":")[1])
    region_name = list(DATA.keys())[region_idx]
    
    if region_name == "м. Київ":
        set_user_location(callback.from_user.id, region_name, "м. Київ")
        await callback.answer()
        await callback.message.edit_text(
            f"✅ **Успішно обрано:** м. Київ\n\n"
            f"Тепер ти отримуватимеш сповіщення про тривоги, відбої та тривоги у сусідній Київській області!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Змінити місто/регіон", callback_data="back_to_regions")]
            ]),
            parse_mode="Markdown"
        )
        return

    await callback.answer()
    await callback.message.edit_text(
        f"📍 **Область:** {region_name}\n\nТепер обери своє **місто**:",
        reply_markup=get_cities_keyboard(region_idx),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("city:"))
async def select_city(callback: types.CallbackQuery):
    _, region_idx_str, city_idx_str = callback.data.split(":")
    region_idx, city_idx = int(region_idx_str), int(city_idx_str)
    
    region_name = list(DATA.keys())[region_idx]
    city_name = DATA[region_name][city_idx]
    
    set_user_location(callback.from_user.id, region_name, city_name)
    
    await callback.answer()
    await callback.message.edit_text(
        f"✅ **Налаштування збережено!**\n\n"
        f"📍 **Регіон:** {region_name}\n"
        f"🏙 **Місто:** {city_name}\n\n"
        f"🔔 Бот надсилатиме сповіщення про тривоги у твоєму регіоні **та застерігатиме, якщо тривога у сусідніх областях!**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Змінити місто/регіон", callback_data="back_to_regions")]
        ]),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back_to_regions")
async def back_to_regions(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "👋 **Обери область або варіант 'Усі області':**",
        reply_markup=get_regions_keyboard(),
        parse_mode="Markdown"
    )

# --- МОНІТОРИНГ ТРИВОГ ТА СУСІДІВ ---
async def check_alerts_loop():
    url = "https://alerts.com.ua/api/states"

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        current_api_status = {
                            state["name"]: state.get("alert", False)
                            for state in data.get("states", [])
                        }

                        for region_name in DATA.keys():
                            is_currently_active = current_api_status.get(region_name, False)
                            was_active = REGION_ALARM_STATUS.get(region_name)

                            if was_active is None:
                                REGION_ALARM_STATUS[region_name] = is_currently_active
                                continue

                            # 🚨 1. ПОЧАТОК ТРИВОГИ В РЕГІОНІ
                            if not was_active and is_currently_active:
                                REGION_ALARM_STATUS[region_name] = True
                                text = (
                                    f"🚨 **ПОВІТРЯНА ТРИВОГА!**\n\n"
                                    f"📍 **{region_name}**\n\n"
                                    f"⚠️ *Прямуйте в укриття!*"
                                )
                                for u_id in get_users_by_region(region_name):
                                    try:
                                        await bot.send_message(chat_id=u_id, text=text, parse_mode="Markdown")
                                    except Exception:
                                        pass

                                # ⚠️ ПОПЕРЕДЖЕННЯ ДЛЯ СУСІДНІХ ОБЛАСТЕЙ
                                neighbor_regions = NEIGHBORS.get(region_name, [])
                                for n_region in neighbor_regions:
                                    if not current_api_status.get(n_region, False):
                                        warn_text = (
                                            f"⚠️ **УВАГА! ТРИВОГА В СУСІДНІЙ ОБЛАСТІ!**\n\n"
                                            f"📍 Тривогу оголошено в: **{region_name}**\n\n"
                                            f"🌩 *Загроза може поширитися на ваш регіон ({n_region}). Будьте готові йти в укриття!*"
                                        )
                                        for u_id in get_users_by_region(n_region):
                                            try:
                                                await bot.send_message(chat_id=u_id, text=warn_text, parse_mode="Markdown")
                                            except Exception:
                                                pass

                            # 🟢 2. ВІДБІЙ ТРИВОГИ
                            elif was_active and not is_currently_active:
                                REGION_ALARM_STATUS[region_name] = False
                                text = (
                                    f"🟢 **ВІДБІЙ ПОВІТРЯНОЇ ТРИВОГИ!**\n\n"
                                    f"📍 **{region_name}**\n\n"
                                    f"✅ *Можна залишати укриття.*"
                                )
                                for u_id in get_users_by_region(region_name):
                                    try:
                                        await bot.send_message(chat_id=u_id, text=text, parse_mode="Markdown")
                                    except Exception:
                                        pass

        except Exception as e:
            print(f"Помилка запиту: {e}")

        await asyncio.sleep(10)

# --- ЗАПУСК ДЛЯ СЕРВЕРА ---
async def main():
    init_db()
    asyncio.create_task(check_alerts_loop())
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
