import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler,
    ContextTypes,
)

# تنظیمات
TOKEN = os.environ.get("TOKEN")
INTERVAL_MINUTES = int(os.environ.get("INTERVAL_MINUTES", 10))

MESSAGE_TEXT = """
📣 خریدار گروه قدیمی شما هستیم

✅ فقط تاریخ ساخت گروه مهمه
❌ تعداد عضو اصلا مهم نیست

💰 لیست خرید گروه :

1402 • 2023 = 500,000 تومن
1401 • 2022 = 600,000 تومن
1400 • 2021 = 700,000 تومن
1399 • 2020 = 750,000 تومن
1398 • 2019 = 750,000 تومن
1397 • 2018 = 750,000 تومن
1396 • 2017 = 750,000 تومن
1395 • 2016 = 750,000 تومن

💳 پرداخت به صورت آنی با کارت به کارت
id: @MrHBVpn
"""

group_ids = set()


async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی بات به گروه اضافه می‌شود"""
    chat = update.my_chat_member.chat
    if chat.type in ["group", "supergroup"]:
        group_ids.add(chat.id)
        try:
            await context.bot.send_message(chat.id, MESSAGE_TEXT)
            print(f"📤 پیام اولیه به گروه {chat.title} ارسال شد")
        except Exception as e:
            print(f"⚠️ خطا در ارسال اولیه به {chat.id}: {e}")


async def periodic_task(context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام هر X دقیقه به همه گروه‌ها"""
    for chat_id in list(group_ids):
        try:
            await context.bot.send_message(chat_id, MESSAGE_TEXT)
            print(f"✅ پیام دوره‌ای به {chat_id} ارسال شد")
        except Exception as e:
            print(f"⚠️ خطا در ارسال دوره‌ای به {chat_id}: {e}")


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # اضافه شدن بات به گروه
    app.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

    # JobQueue: ارسال دوره‌ای
    job_queue = app.job_queue
    job_queue.run_repeating(periodic_task, interval=INTERVAL_MINUTES * 60, first=10)

    print("🚀 بات فعال شد و هر", INTERVAL_MINUTES, "دقیقه پیام ارسال می‌کند.")
    await app.run_polling(close_loop=False)


if __name__ == "__main__":
    asyncio.run(main())
