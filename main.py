import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Читаем токены из переменных окружения Render
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALERTS_API_TOKEN = os.getenv("ALERTS_API_TOKEN")

user_subscriptions = {}
current_alerts_state = {}

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

def get_cities_keyboard():
    builder = InlineKeyboardBuilder()
    regions = [
        "Одесская область", "Киевская область", "Харьковская область",
        "Николаевская область", "Днепропетровская область", "Львовская область"
    ]
    for region in regions:
        builder.button(text=region, callback_data=f"set_region:{region}")
    builder.adjust(2)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Выберите вашу область, чтобы получать уведомления о тревогах и типе опасности:",
        reply_markup=get_cities_keyboard()
    )

@dp.callback_query(F.data.startswith("set_region:"))
async def process_region_choice(callback: types.CallbackQuery):
    region = callback.data.split(":")[1]
    user_subscriptions[callback.from_user.id] = region
    await callback.message.edit_text(f"✅ Уведомления успешно подвязаны для: **{region}**.")
    await callback.answer()

async def check_alerts_loop():
    url = "https://alerts.in.ua/api/v1/alerts/active.json"
    headers = {"Authorization": f"Bearer {ALERTS_API_TOKEN}"}

    async with aiohttp.ClientSession() as http_session:
        while True:
            try:
                # На Render прокси не нужны, прямые запросы работают идеально
                async with http_session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        alerts = data.get("alerts", [])

                        active_regions = {}
                        for alert in alerts:
                            if alert.get("location_type") == "state":
                                title = alert.get("location_title")
                                notes = alert.get("notes") or "Угроза обстрела / БПЛА / баллистика"
                                active_regions[title] = notes

                        for user_id, user_region in list(user_subscriptions.items()):
                            is_active = user_region in active_regions
                            was_active = current_alerts_state.get(user_region, False)

                            # 🚨 Тревога началась
                            if is_active and not was_active:
                                threat_details = active_regions[user_region]
                                await bot.send_message(
                                    user_id,
                                    f"🚨 **ВОЗДУШНАЯ ТРЕВОГА!**\n\n"
                                    f"📍 **Регион:** {user_region}\n"
                                    f"⚠️ **Угроза:** {threat_details}\n\n"
                                    f"Пройдите в укрытие!"
                                )

                            # 🟢 Отбой тревоги
                            elif not is_active and was_active:
                                await bot.send_message(
                                    user_id,
                                    f"🟢 **ОТБОЙ ВОЗДУШНОЙ ТРЕВОГИ**\n\n"
                                    f"📍 **Регион:** {user_region}"
                                )

                        for reg in set(user_subscriptions.values()):
                            current_alerts_state[reg] = reg in active_regions

                    else:
                        logging.error(f"Код ответа API: {response.status}")

            except Exception as e:
                logging.error(f"Ошибка проверки API: {e}")

            await asyncio.sleep(15)

async def main():
    asyncio.create_task(check_alerts_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
