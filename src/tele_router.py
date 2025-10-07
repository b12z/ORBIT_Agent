import os, re, json, asyncio, time
from dotenv import load_dotenv
from telegram import Bot
from requests.exceptions import RequestException
from src.reply_writer import write_reply
from src.x_fetch import get_tweet_text
from src.poster import post_tweet
from src.telegram_bot import send_drafts_async

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
bot = Bot(token=TOKEN)

OFFSET_FILE = ".tele_offset.json"
X_STATUS_RE = re.compile(r"(?:https?://)?(?:x|twitter)\.com/[^/]+/status/(\d+)")


def _load_offset():
    if os.path.exists(OFFSET_FILE):
        try:
            return json.load(open(OFFSET_FILE)).get("offset")
        except Exception:
            return None
    return None


def _save_offset(offset):
    try:
        json.dump({"offset": offset}, open(OFFSET_FILE, "w"))
    except Exception:
        pass


async def _process_text(msg_text: str):
    m = X_STATUS_RE.search(msg_text or "")
    if m:
        tweet_id = m.group(1)
        tweet_text = (
            get_tweet_text(tweet_id)
            or "Author discusses Web3/KOL/growth—reply with a witty, constructive one-liner."
        )
        draft = write_reply(tweet_text)
        approved = await send_drafts_async([
            {"tweet_id": tweet_id, "author": "manual", "text": draft}
        ])
        if approved.get("action") == "approve":
            try:
                resp = post_tweet(approved["text"], in_reply_to=tweet_id)
                await bot.send_message(chat_id=CHAT_ID, text=f"✅ Replied to tweet {tweet_id}")
            except RequestException as e:
                await bot.send_message(chat_id=CHAT_ID, text=f"❌ Post failed: {e}")
        else:
            await bot.send_message(chat_id=CHAT_ID, text="⏭️ Skipped.")
    else:
        # Plain text → compose an original tweet
        draft = write_reply(msg_text)
        approved = await send_drafts_async([
            {"tweet_id": None, "author": "self", "text": draft}
        ])
        if approved.get("action") == "approve":
            try:
                resp = post_tweet(approved["text"]) 
                await bot.send_message(chat_id=CHAT_ID, text=f"✅ Posted original tweet.")
            except RequestException as e:
                await bot.send_message(chat_id=CHAT_ID, text=f"❌ Post failed: {e}")
        else:
            await bot.send_message(chat_id=CHAT_ID, text="⏭️ Skipped.")


async def run_telegram_router_once():
    """Polls Telegram once, processes any new messages from CHAT_ID, updates offset, then returns."""
    offset = _load_offset()
    updates = await bot.get_updates(offset=offset, timeout=10)
    if not updates:
        return
    new_offset = offset
    for upd in updates:
        new_offset = max(new_offset or 0, upd.update_id + 1)
        msg = getattr(upd, "message", None)
        if not msg or msg.chat.id != CHAT_ID:
            continue
        if msg.text:
            await _process_text(msg.text)
    if new_offset is not None:
        _save_offset(new_offset)


def run_once():
    asyncio.run(run_telegram_router_once())
