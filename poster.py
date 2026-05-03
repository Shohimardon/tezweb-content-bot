"""
TezWeb.uz — AI Content Bot
Telegram API ga to'g'ridan-to'g'ri requests orqali murojaat qiladi.
"""

import json
import logging
import os
import schedule
import time
import pytz
import requests
import threading
from datetime import datetime
from pathlib import Path

import anthropic

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
OFFSET_FILE   = "offset.txt"

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Telegram API funksiyalari
# ──────────────────────────────────────────────

def tg_send_message(chat_id, text, parse_mode="Markdown"):
    try:
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        r = requests.post(f"{API}/sendMessage", json=payload, timeout=30)
        return r.json()
    except Exception as e:
        logger.error("sendMessage xatosi: %s", e)
        return None

def tg_send_photo(chat_id, photo_path, caption):
    try:
        with open(photo_path, "rb") as f:
            r = requests.post(f"{API}/sendPhoto", data={
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "Markdown"
            }, files={"photo": f}, timeout=60)
        return r.json()
    except Exception as e:
        logger.error("sendPhoto xatosi: %s", e)
        return None

def tg_get_updates(offset=0):
    try:
        r = requests.post(f"{API}/getUpdates", json={
            "offset": offset,
            "timeout": 30,
            "allowed_updates": ["message", "chat_member"]
        }, timeout=40)
        return r.json()
    except Exception as e:
        logger.error("getUpdates xatosi: %s", e)
        return {"ok": False, "result": []}

def tg_send_chat_action(chat_id, action="typing"):
    try:
        requests.post(f"{API}/sendChatAction", json={
            "chat_id": chat_id,
            "action": action
        }, timeout=10)
    except Exception:
        pass

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

def get_next_topic():
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

def generate_post(topic):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    hours  = datetime.now(TASHKENT_TZ).hour
    if hours < 12:
        vaqt = "ertalab"
    elif hours < 17:
        vaqt = "kunduz"
    else:
        vaqt = "kechqurun"

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": f"""Sen TezWeb.uz kompaniyasining Telegram kanal menejerisisan.
TezWeb.uz — Uzbekistonda tez yuklanadigan saytlar, Telegram botlar va reklama xizmatlarini taqdim etuvchi IT kompaniya.

Mavzu: {topic}

Talablar:
- Til: O'zbek tili (lotin alifbosi)
- Uzunlik: 150-250 so'z
- Qiziqarli fakt yoki savol bilan boshlang
- Qisqa paragraflar, emojilar ishlatilsin
- Oxirida TezWeb.uz ni tabiiy tarzda tavsiya qil
- Eng oxirgi qator: "tezweb.uz | @tezweb_uz | @Shohdollar22"
- Faqat post matnini yoz"""}]
    )
    return msg.content[0].text


def generate_reply(question, username):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": f"""Sen TezWeb.uz kompaniyasining aqlli yordamchisisisan.
TezWeb.uz xizmatlari va narxlari:
- Minimal sayt: 5 000 000 so'mdan
- Biznes sayt: 8 000 000 so'mdan
- Sayt + reklama: 18 000 000 so'mdan
- Boshlangich bot: 6 000 000 so'mdan
- Biznes bot: 14 000 000 so'mdan
- AI bot: 22 000 000 so'mdan
- Reklama (Direkt/Ads): 4 000 000 so'm/oydan

Foydalanuvchi @{username} savol berdi: "{question}"

Qoidalar:
- Faqat sayt, bot, IT, biznes, reklama mavzularida javob ber
- Boshqa mavzularda: "Kechirasiz, men faqat IT va biznes mavzularida yordam bera olaman"
- Javob qisqa va aniq (max 150 so'z), o'zbek tilida
- Oxirida: "Batafsil: @Shohdollar22"
- Faqat javob matnini yoz"""}]
    )
    return msg.content[0].text

# ──────────────────────────────────────────────
# Post yuborish
# ──────────────────────────────────────────────

def send_post():
    topic, image_file = get_next_topic()
    image_path = IMAGES_DIR / image_file
    logger.info("Post yaratilmoqda: %s", topic)

    try:
        caption = generate_post(topic)
        if image_path.exists():
            result = tg_send_photo(CHANNEL, image_path, caption)
        else:
            result = tg_send_message(CHANNEL, caption)

        if result and result.get("ok"):
            logger.info("✅ Post yuborildi: %s", topic)
        else:
            logger.error("❌ Post yuborishda xato: %s", result)
    except Exception as e:
        logger.error("❌ Post xatosi: %s", e)

# ──────────────────────────────────────────────
# Guruhni polling orqali kuzatish
# ──────────────────────────────────────────────

def get_offset():
    if Path(OFFSET_FILE).exists():
        return int(Path(OFFSET_FILE).read_text().strip() or "0")
    return 0

def save_offset(offset):
    Path(OFFSET_FILE).write_text(str(offset))

def handle_updates():
    """Guruhdan kelgan xabarlarni qayta ishlaydi."""
    offset = get_offset()

    # Bot username ni bir marta olamiz
    try:
        bot_info = requests.get(f"{API}/getMe", timeout=10).json()
        bot_username = bot_info.get("result", {}).get("username", "")
        logger.info("Bot username: @%s", bot_username)
    except Exception:
        bot_username = ""
        logger.error("Bot username olishda xato")

    while True:
        try:
            data = tg_get_updates(offset)
            if not data.get("ok"):
                logger.error("getUpdates xato: %s", data)
                time.sleep(5)
                continue

            results = data.get("result", [])
            if results:
                logger.info("Yangi yangilanishlar: %d ta", len(results))

            for update in results:
                offset = update["update_id"] + 1
                save_offset(offset)

                # Yangi a'zo
                chat_member = update.get("chat_member")
                if chat_member:
                    old = chat_member.get("old_chat_member", {}).get("status", "")
                    new = chat_member.get("new_chat_member", {}).get("status", "")
                    if old in ("left", "kicked") and new == "member":
                        user = chat_member["new_chat_member"]["user"]
                        name = f"@{user.get('username', '')}" if user.get("username") else user.get("first_name", "")
                        chat_id = chat_member["chat"]["id"]
                        welcome = (
                            f"Xush kelibsiz, {name}!\n\n"
                            f"Bu TezWeb.uz rasmiy muhokama guruhimiz.\n\n"
                            f"Bu yerda siz:\n"
                            f"Sayt va bot yaratish haqida savol bera olasiz\n"
                            f"Biznes va IT yangiliklar muhokama qila olasiz\n"
                            f"Mutaxassislarimizdan maslahat ola olasiz\n\n"
                            f"Kanalimizga obuna bo'ling: @tezweb_uz\n"
                            f"Saytimiz: tezweb.uz\n"
                            f"Buyurtma: @Shohdollar22"
                        )
                        tg_send_message(chat_id, welcome)
                        logger.info("Yangi a'zo kutib olindi: %s", name)

                # Yangi a'zo (new_chat_members orqali)
                message_raw = update.get("message", {})
                new_members = message_raw.get("new_chat_members", [])
                if new_members:
                    chat_id = message_raw["chat"]["id"]
                    for user in new_members:
                        if user.get("is_bot"):
                            continue
                        name = f"@{user['username']}" if user.get("username") else user.get("first_name", "")
                        welcome = (
                            f"Xush kelibsiz, {name}!\n\n"
                            f"Bu TezWeb.uz rasmiy muhokama guruhimiz.\n\n"
                            f"Bu yerda siz sayt, bot, IT va biznes mavzularida\n"
                            f"savol berishingiz mumkin.\n\n"
                            f"Savol berish uchun xabar oxiriga ? belgisini qoyish yoki\n"
                            f"botning xabariga reply qilish kifoya — men javob beraman!\n\n"
                            f"Kanalimiz: @tezweb_uz\n"
                            f"Saytimiz: tezweb.uz\n"
                            f"Buyurtma: @Shohdollar22"
                        )
                        result = tg_send_message(chat_id, welcome, parse_mode=None)
                        logger.info("Yangi azu kutib olindi: %s | chat_id: %s | result: %s", name, chat_id, result)

                # Guruhda xabar
                message = update.get("message", {})
                if message and message.get("text"):
                    text     = message["text"]
                    chat     = message.get("chat", {})
                    # Barcha guruhlar uchun ishlaydi

                    from_user = message.get("from", {})
                    user_name = from_user.get("username", from_user.get("first_name", "user"))
                    chat_id   = chat["id"]
                    msg_id    = message["message_id"]
                    chat_type = chat.get("type", "")

                    logger.info("Chat type: %s, text: %s", chat_type, text[:20])

                    reply_to     = message.get("reply_to_message", {})
                    is_reply     = reply_to.get("from", {}).get("is_bot", False)
                    is_mention   = bot_username and f"@{bot_username}" in text
                    has_question = "?" in text and len(text.strip()) > 1

                    logger.info("Xabar tekshirilmoqda: is_reply=%s, is_mention=%s, has_question=%s, text=%s", is_reply, is_mention, has_question, text[:30])

                    if not is_reply and not is_mention and not has_question:
                        continue

                    # Botdan xabar emas, oddiy savol
                    if from_user.get("is_bot"):
                        continue

                    question = text.replace(f"@{bot_username}", "").strip()
                    if not question:
                        continue

                    logger.info("Javob tayyorlanmoqda: %s | savol: %s", user_name, question[:30])
                    tg_send_chat_action(chat_id)
                    try:
                        reply = generate_reply(question, user_name)
                        result = requests.post(f"{API}/sendMessage", json={
                            "chat_id": chat_id,
                            "text": reply,
                            "reply_to_message_id": msg_id
                        }, timeout=30).json()
                        logger.info("Javob yuborildi: %s | ok=%s", user_name, result.get("ok"))
                    except Exception as reply_err:
                        logger.error("Javob yuborishda xato: %s", reply_err)

        except Exception as e:
            logger.error("handle_updates xatosi: %s", e)
            time.sleep(5)

# ──────────────────────────────────────────────
# Jadval va ishga tushirish
# ──────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        print("CONTENT_BOT_TOKEN ni Railway Variables ga kiriting")
        return
    if not ANTHROPIC_KEY:
        print("ANTHROPIC_API_KEY ni Railway Variables ga kiriting")
        return

    # Toshkent UTC+5: 9:00→04:00, 14:00→09:00, 19:00→14:00
    schedule.every().day.at("04:00").do(send_post)
    schedule.every().day.at("09:00").do(send_post)
    schedule.every().day.at("14:00").do(send_post)

    # Polling thread
    t = threading.Thread(target=handle_updates, daemon=True)
    t.start()

    logger.info("TezWeb Content Bot ishga tushdi!")
    logger.info("Kanal: %s | Guruh: %s", CHANNEL, GROUP)
    logger.info("Post vaqtlari: 9:00, 14:00, 19:00 (Toshkent)")

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
