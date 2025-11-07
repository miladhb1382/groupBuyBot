import os
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes, Job
import asyncio

TOKEN = os.environ.get("TOKEN")
INTERVAL_MINUTES = int(os.environ.get("INTERVAL_MINUTES", 10))


# پیام شما (رشته چندخطی)
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
# لیست گروه‌ها
group_ids = set()

# Handler وقتی بات اضافه شد
async def on_bot_added(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE):
    chat = update.my_chat_member.chat
    if chat.type in ["group", "supergroup"]:
        group_ids.add(chat.id)
        await context.bot.send_message(chat_id=chat.id, text=MESSAGE_TEXT)
        print(f"پیام اولیه به گروه {chat.title} ارسال شد")

# Job دوره‌ای برای ارسال پیام
async def send_scheduled_messages(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(group_ids):
        try:
            await context.bot.send_message(chat_id=chat_id, text=MESSAGE_TEXT)
            print(f"پیام دوره‌ای به {chat_id} ارسال شد")
        except Exception as e:
            print(f"خطا در ارسال به {chat_id}: {e}")

# ساخت Application
app = ApplicationBuilder().token(TOKEN).build()

# ثبت Handler
app.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

# اضافه کردن Job دوره‌ای به JobQueue
app.job_queue.run_repeating(send_scheduled_messages, interval=INTERVAL_MINUTES*60, first=10)

print("بات آماده است و پیام‌ها ارسال می‌شوند.")
app.run_polling()
