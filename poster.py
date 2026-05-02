"""
TezWeb.uz — AI Content Bot
===========================
Har kuni 3 marta (9:00, 14:00, 19:00 Toshkent vaqti)
@tezweb_uz kanaliga rasm + matn yuboradi.
"""

import asyncio
import logging
import os
import schedule
import time
import pytz
from datetime import datetime
from pathlib import Path

import anthropic
from telegram import Bot

# ──────────────────────────────────────────────
# Sozlamalar
# ──────────────────────────────────────────────

BOT_TOKEN     = os.environ.get("CONTENT_BOT_TOKEN", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CHANNEL       = "@tezweb_uz"
TASHKENT_TZ   = pytz.timezone("Asia/Tashkent")
IMAGES_DIR    = Path("images")
TOPIC_FILE    = "topic_index.txt"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Mavzular va rasmlar (tartib bo'yicha)
# ──────────────────────────────────────────────

TOPICS = [
    ("Biznes uchun sayt yaratishning ahamiyati",          "card_01_Biznes_uchun_sayt.png"),
    ("Telegram bot biznes daromadini qanday oshiradi",    "card_02_Telegram_Bot.png"),
    ("Google'da birinchi bo'lish — SEO sirlari",          "card_03_Google_SEO.png"),
    ("Tez yuklanadigan sayt mijozlarni ushlab qoladi",    "card_04_Sayt_Tezligi.png"),
    ("Onlayn-do'kon uchun eng yaxshi texnologiyalar",     "card_05_Onlayn_Do'kon.png"),
    ("Yandex Direktda reklama qilishning afzalliklari",   "card_06_Yandex_Direkt.png"),
    ("Uzbekistonda internet biznes tendensiyalari",        "card_07_IT_Uzbekiston.png"),
    ("Sayt tezligi va konversiya o'rtasidagi bog'liqlik", "card_08_Konversiya.png"),
    ("AI botlar biznesni qanday avtomatlashtiradi",       "card_09_AI_Avtomatizatsiya.png"),
    ("Mobil versiya nima uchun muhim",                    "card_10_Mobil_Versiya.png"),
    ("Onlayn buyurtma tizimini qanday sozlash kerak",     "card_11_Onlayn_Buyurtma.png"),
    ("Raqamli marketing — kichik biznes uchun qo'llanma","card_12_Raqamli_Marketing.png"),
    ("Sayt orqali mijoz jalb qilish strategiyalari",      "card_13_Mijoz_Jalb_Qilish.png"),
    ("Telegram orqali savdo qilishning eng yaxshi usuli", "card_14_Telegram_Savdo.png"),
    ("IT sohasida Uzbekiston 2025-2026 yillarda",         "card_15_IT_2025-2026.png"),
    ("Biznes uchun brend identifikatsiyasi va dizayn",    "card_16_Brend_va_Dizayn.png"),
    ("Onlayn to'lov tizimlarini saytga ulash",            "card_17_Onlayn_To'lov.png"),
    ("Google Ads va Yandex Direkt — qaysi yaxshi",        "card_18_Google_vs_Yandex.png"),
    ("Google Analytics bilan biznesni boshqarish",        "card_19_Google_Analytics.png"),
    ("Mijoz ishonchini oshiruvchi sayt elementlari",      "card_20_Mijoz_Ishonchi.png"),
]

# ──────────────────────────────────────────────
# Navbatdagi mavzu
# ──────────────────────────────────────────────

def get_next_topic() -> tuple:
    if Path(TOPIC_FILE).exists():
        idx = int(Path(TOPIC_FILE).read_text().strip() or "0")
    else:
        idx = 0

    topic, image = TOPICS[idx % len(TOPICS)]
    Path(TOPIC_FILE).write_text(str((idx + 1) % len(TOPICS)))
    return topic, image

# ──────────────────────────────────────────────
# AI post yaratish
# ──────────────────────────────────────────────

def generate_post(topic: str) -> str:
    client  = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    hours   = datetime.now(TASHKENT_TZ).hour

    if hours < 12:
        greeting = "Xayrli tong!"
    elif hours < 17:
        greeting = "Xayrli kun!"
    else:
        greeting = "Xayrli kech!"

    prompt = f"""Sen TezWeb.uz kompaniyasining Telegram kanal menejerisisan.
TezWeb.uz — Uzbekistonda tez yuklanadigan saytlar, Telegram botlar va reklama xizmatlarini taqdim etuvchi IT kompaniya.

Mavzu: {topic}

Talablar:
- Til: O'zbek tili (lotin alifbosi)
- Uzunlik: 150-250 so'z
- "{greeting}" bilan emas, qiziqarli fakt yoki savol bilan boshlang
- Qisqa paragraflar, emojilar ishlatilsin
- Oxirida TezWeb.uz ni tabiiy tarzda tavsiya qil
- Eng oxirgi qator aynan shu bo'lsin: "🔗 tezweb.uz | 📢 @tezweb_uz | 📩 @Shohdollar22"
- Faqat post matnini yoz"""

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

# ──────────────────────────────────────────────
# Kanalga yuborish
# ──────────────────────────────────────────────

async def send_post_async():
    topic, image_file = get_next_topic()
    image_path = IMAGES_DIR / image_file

    logger.info("Post yaratilmoqda: %s", topic)

    try:
        caption = generate_post(topic)
        bot = Bot(token=BOT_TOKEN)

        if image_path.exists():
            with open(image_path, "rb") as photo:
                await bot.send_photo(
                    chat_id=CHANNEL,
                    photo=photo,
                    caption=caption,
                    parse_mode="Markdown"
                )
        else:
            await bot.send_message(
                chat_id=CHANNEL,
                text=caption,
                parse_mode="Markdown"
            )

        logger.info("✅ Post yuborildi: %s", topic)

    except Exception as e:
        logger.error("❌ Xato: %s", e)


def send_post():
    asyncio.run(send_post_async())

# ──────────────────────────────────────────────
# Jadval
# ──────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        print("❌ CONTENT_BOT_TOKEN ni Railway Variables ga kiriting")
        return
    if not ANTHROPIC_KEY:
        print("❌ ANTHROPIC_API_KEY ni Railway Variables ga kiriting")
        return

    # Toshkent UTC+5
    # 9:00  → 04:00 UTC
    # 14:00 → 09:00 UTC
    # 19:00 → 14:00 UTC
    schedule.every().day.at("04:00").do(send_post)
    schedule.every().day.at("09:00").do(send_post)
    schedule.every().day.at("14:00").do(send_post)

    logger.info("✅ TezWeb Content Bot ishga tushdi!")
    logger.info("📢 Kanal: %s | Vaqtlar: 9:00, 14:00, 19:00 (Toshkent)", CHANNEL)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
