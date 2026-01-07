import random, re
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant # Required for the check
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from lib.util.file_properties import get_name, get_hash, get_media_file_size
from lib.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink

# --- CONFIGURATION ---
FORCE_SUB_CHANNEL_ID = -1002581367215  # Replace with your Channel ID
FORCE_SUB_LINK = "https://t.me/+DBG5puvRFy9lNDY9" # Replace with your Link

# --- GLOBAL FORCE SUB CHECK (Runs Before Everything) ---
@Client.on_message(filters.private, group=-1)
async def force_sub_check(client, message):
    try:
        # Check if user is a member
        await client.get_chat_member(FORCE_SUB_CHANNEL_ID, message.from_user.id)
    except UserNotParticipant:
        # If not a member, send the warning and STOP processing
        await message.reply_text(
            text="<b>📢 Ultras Developer: 🔒 Join this channel to use the bot.</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url=FORCE_SUB_LINK)]
            ]),
            parse_mode=enums.ParseMode.HTML
        )
        await message.stop_propagation() # <--- THIS STOPS THE USER HERE
    except Exception as e:
        # If bot is not admin or other error, print it but allow access
        print(f"Force Sub Error: {e}")
        # We do NOT stop propagation here, so the bot works if the check fails due to error

# --- NORMAL BOT COMMANDS ---
# (Notice we don't need the check inside these functions anymore)

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    rm = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me/ultrasdeveloper")
        ]] 
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
    return

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def stream_start(client, message):
    try:
        file = getattr(message, message.media.value)
        filename = file.file_name
        filesize = humanize.naturalsize(file.file_size) 
        fileid = file.file_id
        user_id = message.from_user.id
        username =  message.from_user.mention 

        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )
        
        edited_name = get_name(log_msg)
        edited_name = re.sub(r'[^\w\.-]', '', edited_name) 
        edited_name = edited_name.replace(" ", ".") 
        fileName = quote_plus(edited_name)
        
        if SHORTLINK == False:
            stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
            download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
        else:
            stream = await get_shortlink(f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")
            download = await get_shortlink(f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")
            
        await log_msg.reply_text(
            text=f"•• Lɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• File Name : {edited_name}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=download), 
                                                InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)]]) 
        )
        rm=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Sᴛʀᴇᴀᴍ 🖥", url=stream),
                    InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ 📥", url=download)
                ]
            ] 
        )
        msg_text = f"""<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲ʀ𝗮𝘁𝗲𝗱 !</u></i>\n
<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{edited_name}</i>\n
<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{humanbytes(get_media_file_size(message))}</i>\n
<b>📥 Download Link: </b><code>{download}</code>\n
<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

        await message.reply_text(
            text=msg_text,
            quote=True,
            disable_web_page_preview=True,
            reply_markup=rm
        )
    except Exception as e:
        await message.reply_text(f"Sorry, an error occurred while generating the link: {str(e)}")
        print(f"Error in stream_start: {e}")
