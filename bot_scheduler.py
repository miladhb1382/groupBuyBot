import os
import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# تنظیمات از متغیرهای محیطی (Environment Variables)
TOKEN = os.environ.get("TOKEN")
INTERVAL_MINUTES = int(os.environ.get("INTERVAL_MINUTES", 10))

if not TOKEN:
    raise RuntimeError("TOKEN environment variable is required")

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

# راه‌اندازی
bot = Bot(token=TOKEN)
app = ApplicationBuilder().token(TOKEN).build()
scheduler = BackgroundScheduler()

# نگهداری شناسه گروه‌ها در حافظه (موقتی)
group_ids = set()

# وقتی بات به گروه اضافه می‌شود (یا وضعیتش تغییر می‌کند)
async def on_bot_added(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE):
    # update.my_chat_member اطلاعاتی درباره چت و وضعیت جدید/قدیم می‌دهد
    chat = update.my_chat_member.chat
    # فقط گروه‌ها (گروه و سوپرگروه)، کانال‌ها را نادیده می‌گیریم
    if chat.type in ["group", "supergroup"]:
        group_ids.add(chat.id)
        try:
            await context.bot.send_message(chat_id=chat.id, text=MESSAGE_TEXT)
            print(f"ارسال پیام اولیه به گروه: {chat.title} (id={chat.id})")
        except Exception as e:
            print(f"خطا در ارسال پیام اولیه به {chat.id}: {e}")

# ارسال دوره‌ای به همه گروه‌هایی که بات داخلشونه
async def send_scheduled_messages():
    if not group_ids:
        print("هیچ گروهی ثبت نشده؛ پیام دوره‌ای ارسال نمی‌شود.")
        return
    for chat_id in list(group_ids):
        try:
            await bot.send_message(chat_id=chat_id, text=MESSAGE_TEXT)
            print(f"ارسال دوره‌ای به {chat_id}")
        except Exception as e:
            print(f"خطا در ارسال دوره‌ای به {chat_id}: {e}")

def start_scheduler():
    scheduler.add_job(lambda: asyncio.run(send_scheduled_messages()), 'interval', minutes=INTERVAL_MINUTES)
    scheduler.start()
    print(f"زمان‌بندی فعال شد: هر {INTERVAL_MINUTES} دقیقه پیام ارسال می‌شود.")

# ثبت handler برای زمانی که وضعیت بات در یک چت (my_chat_member) تغییر کنه
app.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

if __name__ == "__main__":
    start_scheduler()
    print("بات آماده است و منتظر اضافه شدن به گروه‌ها...")
    app.run_polling()
