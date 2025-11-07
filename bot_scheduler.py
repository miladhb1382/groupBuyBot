import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")
INTERVAL_MINUTES = int(os.environ.get("INTERVAL_MINUTES", 10))

MESSAGE_TEXT = """
📣 خریدار گروه قدیمی شما هستیم

✅فقط تاریخ ساخت گروه مهمه
❌تعداد عضو اصلا مهم نیست

💰لیست خرید گروه :

1402 • 2023  = 500,000 تومن
1401 • 2022  = 600,000 تومن
1400 • 2021  = 700,000 تومن
1399 • 2020  = 750,000 تومن
1398 • 2019  = 750,000 تومن
1397 • 2018  = 750,000 تومن
1396 • 2017  = 750,000 تومن
1395 • 2016  = 750,000 تومن

﻿سال 2024 پیوی تشریف بیارین

💳پرداخت به صورت آنی با کارت به کارت

دوستانی که نمیدونید چه گروه های مالک هستین حتی اگه لفت دادین پیوی تشریف بیارید راهنمایی کنم
id: @MrHBVpn
"""

group_ids = set()

# Handler وقتی بات اضافه شد
async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.my_chat_member.chat
    if chat.type in ["group", "supergroup"]:
        group_ids.add(chat.id)
        try:
            await context.bot.send_message(chat.id, MESSAGE_TEXT)
            print(f"پیام اولیه به گروه {chat.title} ارسال شد")
        except Exception as e:
            print(f"خطا در ارسال اولیه به {chat.id}: {e}")

# Task دوره‌ای پیام‌ها
async def send_periodic_messages(app):
    await asyncio.sleep(10)  # صبر اولیه قبل از اولین ارسال
    while True:
        for chat_id in list(group_ids):
            try:
                await app.bot.send_message(chat_id, MESSAGE_TEXT)
                print(f"پیام دوره‌ای به {chat_id} ارسال شد")
            except Exception as e:
                print(f"خطا در ارسال دوره‌ای به {chat_id}: {e}")
        await asyncio.sleep(INTERVAL_MINUTES * 60)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))
    # اجرای Task دوره‌ای
    asyncio.create_task(send_periodic_messages(app))
    print("بات آماده است و پیام‌ها ارسال می‌شوند.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
