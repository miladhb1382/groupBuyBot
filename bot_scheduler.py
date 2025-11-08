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
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            groups = set(json.load(f))
            print(f"✅ فایل {GROUPS_FILE} با {len(groups)} گروه بارگذاری شد")
            return groups
    except FileNotFoundError:
        print(f"⚠️ فایل {GROUPS_FILE} یافت نشد - لیست خالی ایجاد شد")
        return set()
    except json.JSONDecodeError:
        print(f"❌ خطا در خواندن فایل {GROUPS_FILE} - لیست خالی ایجاد شد")
        return set()
    except Exception as e:
        print(f"❌ خطای غیرمنتظره در بارگذاری گروه‌ها: {e} - لیست خالی ایجاد شد")
        return set()

def save_groups(groups):
    """ذخیره لیست گروه‌ها در فایل"""
    try:
        with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(groups), f, ensure_ascii=False)
        print(f"✅ لیست {len(groups)} گروه در {GROUPS_FILE} ذخیره شد")
    except Exception as e:
        print(f"❌ خطا در ذخیره‌سازی گروه‌ها: {e}")

# لیست گروه‌ها
group_ids = load_groups()

async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی بات به گروه اضافه شد"""
    chat = update.my_chat_member.chat
    if chat.type in ["group", "supergroup"]:
        group_ids.add(chat.id)
        save_groups(group_ids)  # ذخیره فوری
        
        try:
            await context.bot.send_message(chat.id, MESSAGE_TEXT)
            print(f"✅ پیام اولیه به {chat.title} ({chat.id}) ارسال شد")
        except Exception as e:
            print(f"❌ خطا در ارسال اولیه به {chat.id}: {e}")
            # اگر مشکل دائمی داره، گروه رو حذف کن
            if any(error in str(e).lower() for error in ["forbidden", "kicked", "blocked"]):
                group_ids.discard(chat.id)
                save_groups(group_ids)

async def periodic_task(context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام هر X دقیقه به همه گروه‌ها"""
    if not group_ids:
        print("📭 هیچ گروهی برای ارسال پیام پیدا نشد")
        return

    print(f"🔄 ارسال پیام دوره‌ای به {len(group_ids)} گروه...")
    
    failed_groups = []
    successful_count = 0
    
    for chat_id in list(group_ids):
        try:
            await context.bot.send_message(chat_id, MESSAGE_TEXT)
            print(f"✅ پیام به {chat_id} ارسال شد")
            successful_count += 1
        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ خطا در ارسال به {chat_id}: {e}")
            
            # اگر بات از گروه حذف شده یا مسدود شده
            if any(error in error_msg for error in ["chat not found", "bot was blocked", "kicked", "forbidden"]):
                failed_groups.append(chat_id)

    # حذف گروه‌های مشکل‌دار
    if failed_groups:
        for chat_id in failed_groups:
            group_ids.discard(chat_id)
        save_groups(group_ids)
        print(f"🗑️ {len(failed_groups)} گروه مشکل‌دار حذف شدند")
    
    print(f"📊 نتیجه ارسال: {successful_count} موفق, {len(failed_groups)} حذف شده")

async def main():
    """اجرای اصلی بات - async"""
    try:
        app = ApplicationBuilder().token(TOKEN).build()

        # هندلر اضافه شدن بات
        app.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))

        # تنظیم job برای ارسال دوره‌ای
        app.job_queue.run_repeating(
            callback=periodic_task,
            interval=5 * 60,
            first=10  # اولین ارسال بعد از 10 ثانیه
        )

        print(f"🤖 بات فعال شد!")
        print(f"⏰ ارسال پیام هر {5} دقیقه")
        print(f"👥 تعداد گروه‌های فعال: {len(group_ids)}")
        print(f"💾 فایل ذخیره‌سازی: {GROUPS_FILE}")
        
        # شروع polling
        await app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"🚫 خطای критиاد در اجرای بات: {e}")

if __name__ == "__main__":
    asyncio.run(main())
