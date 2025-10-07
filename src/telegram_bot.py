import os, asyncio, time
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
bot = Bot(token=TOKEN)

async def send_ping(text: str):
    await bot.send_message(chat_id=CHAT_ID, text=text)
    print("Message sent successfully:", text)

async def send_drafts_async(drafts: list[dict]) -> dict:
    text = "🚀 *ORBIT Agent Drafts*\n\n"
    for d in drafts:
        text += f"• `{d['tweet_id']}` — {d['text']}\n"
    keyboard = [
        [InlineKeyboardButton("Approve ✅", callback_data=f"approve:{drafts[0]['tweet_id']}"),
         InlineKeyboardButton("Skip ❌", callback_data=f"skip:{drafts[0]['tweet_id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown", reply_markup=reply_markup)

    print("Waiting for approval in Telegram...")
    start = time.time()
    offset = None
    while time.time() - start < 60:
        updates = await bot.get_updates(offset=offset, timeout=10)
        for upd in updates:
            offset = upd.update_id + 1
            if upd.callback_query and upd.callback_query.message.message_id == msg.message_id:
                data = upd.callback_query.data
                await bot.answer_callback_query(upd.callback_query.id, "Got it ✅")
                if data.startswith("approve"):
                    return {"action": "approve", "tweet_id": data.split(":")[1], "text": drafts[0]["text"]}
                elif data.startswith("skip"):
                    return {"action": "skip"}
        await asyncio.sleep(2)
    return {"action": "timeout"}

def send_drafts(drafts: list[dict]) -> dict:
    """sync wrapper for convenience"""
    return asyncio.run(send_drafts_async(drafts))