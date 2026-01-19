import asyncio
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.types import Message

# === НАСТРОЙКИ ===
TOKEN = "8300703952:AAHV6rI-qDU_iVmVk78E_kLzo73D0tY29Pg"
CHAT_ID = -1002785980291
ANNOUNCEMENTS_THREAD_ID = 5

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "andreo.gor122@gmail.com"
SMTP_PASS = "wphm dkaa evmj zitx"  # ✅ App Password!

TEACHERS_EMAILS = [
    "kajshevakv@suitd.ru",
    "muraveva.kn@suitd.ru",
    "olsh2610@yandex.ru",
    "Oisann@yandex.ru",
    "aoch@yandex.ru",
    "vataga5047@mail.ru",
    "englira@mail.ru",
    "g.indira.smith@gmail.com",
    "tatbel42@mail.ru",
    "ksena311@yandex.ru",
    "Annamish111@mail.ru",
    "veronikaspb@gmail.com",
    "aribeth93@yandex.ru",
    "marinapopo@mail.ru",
    "Sinitsyna.V@list.ru",
    "priest-denis@yandex.ru",
    "tperel2003@mail.ru",
    "dmitrybalashov98@gmail.com",
    "natalimark18@mail.ru",
    "anne.mokrousova@gmail.com",
    "pavlovawholeworld@gmail.com",
    "nastya.turskova@mail.ru",
    "sportsforpro@yandex.com",
    "nastya91938@mail.ru",
    "liza1luiza@yandex.ru",
    "andreo.pro123@yandex.ru",
    "i@julyarivjer.ru"
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


async def send_to_teachers(subject: str, body: str, attachments=None):
    msg = MIMEMultipart()
    msg["Subject"] = f"📢 FLIPS: {subject}"
    msg["From"] = SMTP_USER

    # ✅ To: первый, Cc: остальные (Gmail одобряет!)
    if TEACHERS_EMAILS:
        msg["To"] = TEACHERS_EMAILS[0]
        if len(TEACHERS_EMAILS) > 1:
            msg["Cc"] = ", ".join(TEACHERS_EMAILS[1:])

    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Вложения
    if attachments:
        for file_info in attachments:
            try:
                file = await bot.get_file(file_info["file_id"])
                file_bytes = await bot.download_file(file.file_path)
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file_bytes.getvalue())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition",
                                f'attachment; filename="{file_info["filename"]}"')
                msg.attach(part)
                logging.info(f"📎 {file_info['filename']}")
            except Exception as e:
                logging.error(f"❌ Вложение: {e}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)  # ✅ ОДНО письмо всем!
            logging.info(f"✅ Рассылка {len(TEACHERS_EMAILS)} преподавателям")
    except Exception as e:
        logging.error(f"❌ SMTP: {e}")


@dp.message(
    F.chat.id == CHAT_ID,
    F.message_thread_id == ANNOUNCEMENTS_THREAD_ID
)
async def forward_message(message: Message):
    attachments = []
    if message.document:
        attachments.append({
            "file_id": message.document.file_id,
            "filename": message.document.file_name or "file.pdf"
        })
    if message.photo:
        attachments.append({
            "file_id": message.photo[-1].file_id,
            "filename": "photo.jpg"
        })

    author = message.from_user.full_name if message.from_user else "Админ"
    subject = (message.text or message.caption or "Объявление")[0:50] + "..."

    body = f"""📢 ОБЪЯВЛЕНИЕ FLIPS

📄 {message.text or message.caption or '[Медиа]'}

📎 Файлов: {len(attachments)}

───────────────────────────────────────
📅 Дата: {message.date}
🤖 Автоматически отправлено ботом FLIPS Рассылка
───────────────────────────────────────"""

    await send_to_teachers(subject, body, attachments)


async def main():
    print("🚀 Бот FLIPS | ТОЛЬКО ОБЪЯВЛЕНИЯ → 27 преподавателей + файлы")
    print(f"📊 Канал: {CHAT_ID} | Тема: {ANNOUNCEMENTS_THREAD_ID}")
    print(f"📧 {len(TEACHERS_EMAILS)} адресов")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
