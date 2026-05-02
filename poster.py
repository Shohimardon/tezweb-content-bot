"""
TezWeb.uz — AI Content Bot
===========================
1. Har kuni 3 marta kaналга post yuboradi
2. Guruhda yangi a'zolarni kutib oladi
3. Guruhda savollarga AI orqali javob beradi
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
from telegram import Update, ChatMember
from telegram.ext import (
    Application,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)

# ──────────────────────────────────────────────
# Sozlamalar
# ──────────────────────────────────────────────

BOT_TOKEN     = os.environ.get("CONTENT_BOT_TOKEN", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CHANNEL       = "@tezweb_uz"
GROUP         = "@tezweb_uz_chat"
TASHKENT_TZ   = pytz.timezone("Asia/Tashkent")
IMAGES_DIR    = Path("images")
TOPIC_FILE    = "topic_index.txt"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Mavzular
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
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    hours  = datetime.now(TASHKENT_TZ).hour

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


def generate_reply(question: str, username: str) -> str:
    """Guruh savoliga AI javobi."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    prompt = f"""Sen TezWeb.uz kompaniyasining aqlli yordamchisisisan.
TezWeb.uz — Uzbekistonda tez yuklanadigan saytlar, Telegram botlar va reklama xizmatlarini taqdim etuvchi IT kompaniya.

Xizmatlar va narxlar:
- Minimal sayt (lendos): 5 000 000 so'mdan
- Tezkor sayt (biznes): 8 000 000 so'mdan
- Sayt + reklama to'plami: 18 000 000 so'mdan
- To'liq to'plam: 24 000 000 so'mdan
- Boshlang'ich bot: 6 000 000 so'mdan
- Biznes bot: 14 000 000 so'mdan
- AI bot: 22 000 000 so'mdan
- Reklama (Direkt/Ads): 4 000 000 so'm/oy dan

Foydalanuvchi @{username} quyidagi savol berdi:
"{question}"

Qoidalar:
- Faqat sayt, bot, IT, biznes, reklama, marketing mavzularida javob ber
- Boshqa mavzularda: "Kechirasiz, men faqat IT va biznes mavzularida yordam bera olaman 😊"
- Javob qisqa va aniq bo'lsin (max 150 so'z)
- O'zbek tilida javob ber
- Agar narx so'rasa — narxlarni ayt va @Shohdollar22 ga murojaat qilishni tavsiya et
- Har doim do'stona va professional bo'l
- Oxirida har doim: "📩 Batafsil: @Shohdollar22" qo'sh"""

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

# ──────────────────────────────────────────────
# Kanalga post yuborish
# ──────────────────────────────────────────────

async def send_post_async(bot):
    topic, image_file = get_next_topic()
    image_path = IMAGES_DIR / image_file
    logger.info("Post yaratilmoqda: %s", topic)

    try:
        caption = generate_post(topic)

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
        logger.error("❌ Post xatosi: %s", e)

# ──────────────────────────────────────────────
# Guruhda yangi a'zolarni kutib olish
# ──────────────────────────────────────────────

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yangi a'zoni guruhda kutib oladi."""
    result = update.chat_member
    if result is None:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    # Yangi a'zo qo'shildi
    if old_status in ("left", "kicked") and new_status == "member":
        user = result.new_chat_member.user
        name = f"@{user.username}" if user.username else user.first_name

        welcome_text = (
            f"👋 Xush kelibsiz, {name}!\n\n"
            f"⚡ Bu *TezWeb.uz* rasmiy muhokama guruhimiz.\n\n"
            f"💡 Bu yerda siz:\n"
            f"• Sayt va bot yaratish haqida savol bera olasiz\n"
            f"• Biznes va IT yangiliklar muhokama qila olasiz\n"
            f"• Mutaxassislarimizdan maslahat ola olasiz\n\n"
            f"📢 Kanalimizga obuna bo'ling: @tezweb_uz\n"
            f"🌐 Saytimiz: tezweb.uz\n"
            f"📩 Buyurtma: @Shohdollar22"
        )

        await context.bot.send_message(
            chat_id=result.chat.id,
            text=welcome_text,
            parse_mode="Markdown"
        )
        logger.info("👋 Yangi a'zo kutib olindi: %s", name)

# ──────────────────────────────────────────────
# Guruhda savollarga javob berish
# ──────────────────────────────────────────────

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guruh xabarlariga AI orqali javob beradi."""
    message = update.message
    if not message or not message.text:
        return

    # Faqat guruhda ishlaydi
    if update.effective_chat.username != "tezweb_uz_chat":
        return

    # Botga reply yoki @mention bo'lsa javob ber
    is_reply_to_bot = (
        message.reply_to_message and
        message.reply_to_message.from_user and
        message.reply_to_message.from_user.is_bot
    )
    is_mention = context.bot.username and f"@{context.bot.username}" in message.text

    if not is_reply_to_bot and not is_mention:
        return

    user     = update.effective_user
    username = user.username or user.first_name
    question = message.text.replace(f"@{context.bot.username}", "").strip()

    if not question:
        return

    logger.info("Savol: %s | %s", username, question)

    try:
        # Yozmoqda ko'rsatish
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        reply = generate_reply(question, username)
        await message.reply_text(reply, parse_mode="Markdown")
        logger.info("✅ Javob yuborildi: %s", username)
    except Exception as e:
        logger.error("❌ Javob xatosi: %s", e)

# ──────────────────────────────────────────────
# Jadval
# ──────────────────────────────────────────────

def make_send_post(app):
    def send_post():
        asyncio.run(send_post_async(app.bot))
    return send_post

# ──────────────────────────────────────────────
# Ishga tushirish
# ──────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        print("❌ CONTENT_BOT_TOKEN ni Railway Variables ga kiriting")
        return
    if not ANTHROPIC_KEY:
        print("❌ ANTHROPIC_API_KEY ni Railway Variables ga kiriting")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Yangi a'zolarni kutib olish
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

    # Guruhda savollarga javob
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_group_message))

    # Jadval — Toshkent UTC+5
    # 9:00 → 04:00 UTC
    # 14:00 → 09:00 UTC
    # 19:00 → 14:00 UTC
    send_fn = make_send_post(app)
    schedule.every().day.at("04:00").do(send_fn)
    schedule.every().day.at("09:00").do(send_fn)
    schedule.every().day.at("14:00").do(send_fn)

    logger.info("✅ TezWeb Content Bot ishga tushdi!")
    logger.info("📢 Kanal: %s | Guruh: %s", CHANNEL, GROUP)
    logger.info("🕐 Post vaqtlari: 9:00, 14:00, 19:00 (Toshkent)")

    # Schedule ni alohida threadda ishlatish
    import threading
    t = threading.Thread(target=lambda: [schedule.run_pending() or time.sleep(30) for _ in iter(int, 1)], daemon=True)
    t.start()

    app.run_polling(allowed_updates=["message", "chat_member"])


if __name__ == "__main__":
    main()
