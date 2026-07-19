import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- CONFIG ----------
BOT_TOKEN = os.getenv("BOT_TOKEN", "7548994106:AAFBPGoBru3eySUhCWipFVhJxZpLPyzzXBg")
ADMIN_ID = int(os.getenv("8341253470", "7255726546"))  # Your Telegram user ID

API_URL_TEMPLATE = "http://like-api-star.vercel.app/like?uid=UID&server_name=ind&key=STAR"
CHAT_IDS_FILE = "chat_ids.json"

# ---------- CHANNEL & DEVELOPER INFO ----------
CHANNEL_URL = "https://t.me/TREKOL_69"          # <-- Change to your channel link
DEVELOPER_LINK = "https://t.me/brrajasrc1"      # <-- Change to your Telegram username link
# Bot username is auto-fetched, no need to set here.

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- CHAT ID STORAGE ----------
def load_chat_ids():
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, "w") as f:
        json.dump(list(chat_ids), f)

chat_ids = load_chat_ids()

def add_chat_id(chat_id):
    if chat_id not in chat_ids:
        chat_ids.add(chat_id)
        save_chat_ids(chat_ids)

def is_admin(user_id):
    return user_id == ADMIN_ID

# ---------- API HELPER ----------
async def like_player(uid, region):
    url = API_URL_TEMPLATE.format(uid=uid, region=region)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"API error: {e}")
        return None

def format_like_response(data):
    if not data:
        return "❌ API error or no response."
    if data.get("status") != 2:
        return f"❌ Something went wrong. Status: {data.get('status')}"
    return (
        f"✅ 𝐋𝐢𝐤𝐞 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥 𝐅𝐫𝐨𝐦 𝐁𝐑 𝐑𝐀𝐉𝐀!\n"
        f"👤 𝐏𝐥𝐚𝐲𝐞𝐫: {data.get('PlayerNickname', 'Unknown')}\n"
        f"🆔 𝐔𝐢𝐝: {data.get('UID', 'N/A')}\n"
        f"📊 𝐋𝐢𝐤𝐞𝐬 𝐁𝐞𝐟𝐨𝐫𝐞: {data.get('LikesbeforeCommand', 0)}\n"
        f"📈 𝐋𝐢𝐤𝐞𝐬 𝐀𝐟𝐭𝐞𝐫: {data.get('LikesafterCommand', 0)}\n"
        f"💖 𝐆𝐢𝐯𝐞𝐧 by API: {data.get('LikesGivenByAPI', 0)}\n"
        f"🔄 𝐑𝐞𝐦𝐚𝐢𝐧𝐬: {data.get('remains', 'N/A')}"
    )

# ---------- COMMAND HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_chat_id(chat_id)

    # Get bot username for "Add to Group" link
    bot_username = context.bot.username
    add_group_url = f"https://t.me/BRFFLIKEBOT?startgroup=start"

    keyboard = [
        [
            InlineKeyboardButton("📢 Channel", url=CHANNEL_URL),
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_LINK),
        ],
        [
            InlineKeyboardButton("➕ Add to Group", url=add_group_url),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐁𝐑 𝐑𝐀𝐉𝐀 𝐋𝐈𝐊𝐄 𝐁𝐎𝐓!\n\n"
        "𝐒𝐞𝐧𝐝 `/like <uid>` (default region: India)\n"
        "𝐎𝐫 `/like <region> <uid>` (region: `ind` or `bd`)\n"
        "𝐄𝐱𝐚𝐦𝐩𝐥𝐞: `/like 16426629440` or `/like bd 16426629440`\n\n"
        "📢 Stay updated via our channel!\n"
        "👨‍💻 For support, contact developer.\n"
        "➕ Add me to your group and enjoy!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show about info with buttons."""
    chat_id = update.effective_chat.id
    add_chat_id(chat_id)

    bot_username = context.bot.username
    add_group_url = f"https://t.me/{bot_username}?startgroup=start"

    keyboard = [
        [
            InlineKeyboardButton("📢 Channel", url=CHANNEL_URL),
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_LINK),
        ],
        [
            InlineKeyboardButton("➕ Add to Group", url=add_group_url),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "ℹ️ About this Bot\n\n"
        "🤖 Like Bot – Give free likes to Free Fire players.\n"
        "🌐 Region: India (ind) or Bangladesh (bd).\n"
        f"📢 **Channel:** [Join Now]({CHANNEL_URL})\n"
        f"👨‍💻 **Developer:** [Contact]({DEVELOPER_LINK})\n\n"
        "Use `/like` to start!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_chat_id(update.effective_chat.id)
    args = context.args

    if not args:
        await update.message.reply_text(
            "❌ **Usage:** `/like <uid>` or `/like <region> <uid>`\n"
            "Region: `ind` (default) or `bd`",
            parse_mode="Markdown"
        )
        return

    if len(args) == 1:
        region = "ind"
        uid_str = args[0]
    else:
        region = args[0].lower()
        uid_str = args[1]

    if region not in ("ind", "bd"):
        await update.message.reply_text("❌ Invalid region. Use `ind` or `bd`.", parse_mode="Markdown")
        return

    if not uid_str.isdigit():
        await update.message.reply_text("❌ UID must be a number.")
        return

    uid = int(uid_str)

    processing = await update.message.reply_text("⏳ Sending like... Please wait.")
    data = await like_player(uid, region)

    if data is None:
        await processing.edit_text("❌ API error. Try again later.")
        return

    await processing.edit_text(format_like_response(data), parse_mode="Markdown")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("📢 Usage: `/broadcast <message>`", parse_mode="Markdown")
        return

    message = " ".join(context.args)
    status_msg = await update.message.reply_text(f"📤 Broadcasting to {len(chat_ids)} chats...")

    sent = failed = 0
    for cid in chat_ids:
        try:
            await context.bot.send_message(chat_id=cid, text=message)
            sent += 1
        except Exception as e:
            logger.error(f"Failed to {cid}: {e}")
            failed += 1

    await status_msg.edit_text(
        f"✅ Broadcast finished!\n📨 Sent: {sent}\n❌ Failed: {failed}\n📋 Total: {len(chat_ids)}"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_chat_id(update.effective_chat.id)
    await update.message.reply_text("❓ Unknown command. Use /start for help.")

# ---------- MAIN ----------
def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Please set BOT_TOKEN environment variable or hardcode it.")
        return
    if ADMIN_ID == 0:
        logger.warning("ADMIN_ID not set – broadcast will not work.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("like", like_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()