import os
import json
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler,
    ContextTypes,
)

# تنظیمات از Environment
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN not found in environment variables!")

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

# فایل برای ذخیره دائمی گروه‌ها
GROUPS_FILE = "groups.json"

def load_groups():
    """بارگذاری لیست گروه‌ها از فایل"""
    try:
        with open(GROUPS_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_groups(groups):
    """ذخیره لیست گروه‌ها در فایل"""
    with open(GROUPS_FILE, 'w') as f:
        json.dump(list(groups), f)

# لیست گروه‌ها
group_ids = load_groups()
print(f"تعداد گروه‌های بارگذاری شده: {len(group_ids)}")

async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی بات به گروه اضافه شد"""
    chat = update.my_chat_member.chat
    if chat.type in ["group", "supergroup"]:
        group_ids.add(chat.id)
        save_groups(group_ids)  # ذخیره فوری
        try:
            await context.bot.send_message(chat.id, MESSAGE_TEXT)
            print(f"پیام اولیه به {chat.title} ({chat.id}) ارسال شد")
        except Exception as e:
            print(f"خطا در ارسال اولیه به {chat.id}: {e}")

async def periodic_task(context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام هر X دقیقه به همه گروه‌ها"""
    if not group_ids:
        print("هیچ گروهی پیدا نشد.")
        return

    print(f"ارسال پیام دوره‌ای به {len(group_ids)} گروه...")
    
    failed_groups = []
    for chat_id in list(group_ids):
        try:
            await context.bot.send_message(chat_id, MESSAGE_TEXT)
            print(f"✅ پیام دوره‌ای به {chat_id} ارسال شد")
        except Exception as e:
            print(f"❌ خطا در ارسال به {chat_id}: {e}")
            failed_groups.append(chat_id)
            # اگر بات از گروه حذف شده بود، آن را حذف کن
            if any(error in str(e).lower() for error in ["chat not found", "bot was blocked", "kicked", "forbidden"]):
                failed_groups.append(chat_id)

    # حذف گروه‌های مشکل‌دار
    if failed_groups:
        for chat_id in failed_groups:
            group_ids.discard(chat_id)
        save_groups(group_ids)  # ذخیره تغییرات
        print(f"حذف {len(failed_groups)} گروه مشکل‌دار")

async def main():
    """اجرای اصلی بات - async"""
    app = ApplicationBuilder().token(TOKEN).build()

    # هندلر اضافه شدن بات
    app.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

    # تنظیم job برای ارسال دوره‌ای
    app.job_queue.run_repeating(
        callback=periodic_task,
        interval=INTERVAL_MINUTES * 60,
        first=10  # اولین ارسال بعد از 10 ثانیه
    )

    print(f"بات فعال شد و هر {INTERVAL_MINUTES} دقیقه پیام ارسال می‌کند.")
    print(f"تعداد گروه‌های فعال: {len(group_ids)}")
    
    # شروع polling
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
