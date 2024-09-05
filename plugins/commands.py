import os
import sys
import logging
import random
import asyncio
import pytz
from Script import script
from pyrogram import Client, filters, enums
from datetime import datetime, timedelta
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
from info import *
from database.top_search import db3
from utils import get_settings, get_size, is_subscribed, reacts, save_group_settings, temp, verify_user, check_token, check_verification, get_token, send_all, get_tutorial, get_shortlink
from database.connections_mdb import active_connection
from utils import react_msg
import re
import json
import base64
logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"
BATCH_FILES = {}

async def check_premium_for_quality(message,  file_name: str):
    if not CHECK_PREMIUM_FOR_QUALITY:return True
    try:
        if '480p' in file_name.lower():
            return True
        else:
            if not await db.has_premium_access(message.from_user.id):
                btn = [[
                    InlineKeyboardButton('🍁 ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ 🍁', callback_data='seeplans')
                ]]
                reply_markup = InlineKeyboardMarkup(btn)
                message_text = f"<b>File Name : {file_name}\nYou Can Only Access 480p Quality Files !\nYᴏᴜ Cᴀɴ Oɴʟʏ Aᴄᴄᴇss 𝟺𝟾𝟶ᴘ Qᴜᴀʟɪᴛʏ Fɪʟᴇs !\nTᴏ Gᴇᴛ Aʟʟ Qᴜᴀʟɪᴛʏ Fɪʟᴇs Yᴏᴜ Nᴇᴇᴅ Tᴏ Tᴀᴋᴇ Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ !\nआप केवल 𝟺𝟾𝟶ᴘ Qᴜᴀʟɪᴛʏ वाली फ़ाइलों ही ले सकते हैं!\nसभी Qᴜᴀʟɪᴛʏ वाली फ़ाइलें प्राप्त करने के लिए आपको Pʀᴇᴍɪᴜᴍ लेनी होगी!</b>"
                await message.reply(message_text, reply_markup=reply_markup)
                return False
            return True
    except Exception as e:
        print("Error in preminum quality check : " , e)
        return True

@Client.on_message(filters.command('delete_user') & filters.user(ADMINS))
async def delete_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('giv me user id')
    user_id = message.command[1]
    try:
        user_id = int(user_id)
    except:
        user_id = user_id
    try:
        await db.delete_user(user_id)
        await message.reply("user removed in database")
    except Exception as e:
        await message.reply(f'Error - {e}')
        
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention, temp.U_NAME))
    send_count = await db.files_count(message.from_user.id, "send_all") or 0
    files_counts = await db.files_count(message.from_user.id, "files_count") or 0
    lifetime_files = await db.files_count(message.from_user.id, "lifetime_files")
    user_id = message.from_user.id
    user = await db.get_userr(user_id)
    last_reset = user.get("last_reset")
    kolkata = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now(kolkata)
    next_day = current_datetime + timedelta(days=1)
    next_day_midnight = datetime(next_day.year, next_day.month, next_day.day, tzinfo=kolkata)
    time_difference = next_day_midnight - current_datetime
    # Extract hours, minutes, and seconds
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    today = current_datetime.strftime("%Y-%m-%d")
    if last_reset != today:
        await db.reset_all_files_count()
        await db.reset_allsend_files()
    try:
        await react_msg(client, message)
    except:
        pass
    try:
        is_file = message.command[1]
        if is_file.startswith('files_'):
            file_id_ = is_file.split('_')[1]
            file_dets = await get_file_details(file_id_)
            if file_dets:
                file_name_ = file_dets[0]['file_name']
                chk = await check_premium_for_quality(message, file_name_)
                if not chk:
                    return
    except Exception as e:
        pass
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
                    InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('🍁 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ 🍁', url="https://t.me/{temp.U_NAME}?start=help")
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    
    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('🤞🏻 ᴇᴀʀɴ ᴍᴏɴᴇʏ 🤡', callback_data="shortlink_info"),
                    InlineKeyboardButton('♻️ ᴜᴘᴅᴀᴛᴇꜱ ♻️', callback_data='channels')
                ],[
                   InlineKeyboardButton('ɪɴsᴛᴀɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ 🌐', url=f'https://www.instagram.com/jaynath_vishwakarma_0143?igsh=MTZyMnBxYmJlaHRiZQ=='),
                   InlineKeyboardButton('ᴅᴏɴᴀᴛɪᴏɴ  💰', callback_data='donation')
                ],[
                    InlineKeyboardButton('📝 ᴄᴏᴍᴍᴀɴᴅꜱ 📝', callback_data='help'),
                    InlineKeyboardButton('🫠 ᴀʙᴏᴜᴛ 🫠', callback_data='about')
                ],[
                    InlineKeyboardButton('Tᴏᴘ Sᴇᴀʀᴄʜ 🔍', callback_data='topsearch'),
                    InlineKeyboardButton('✨ ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ✨', callback_data="premium_info")
                ],[
                    InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer')
                  ]]
        if IS_VERIFY or IS_SHORTLINK is True:
            buttons.append([
                InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer')
            ])
            buttons.append([
                InlineKeyboardButton('✨ ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ ✨', callback_data="premium_info")
            ])
        reply_markup = InlineKeyboardMarkup(buttons)
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "<b><i> ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ☕</i></b>" 
        elif curr_time < 17:
            gtxt = "<b><i>ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ 🌗</i></b>" 
        elif curr_time < 21:
            gtxt = "<b><i>ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌇</i></b>"
        else:
            gtxt = "<b><i>ɢᴏᴏᴅ ɴɪɢʜᴛ 🥱</i></b>"
        m=await message.reply_text("<i>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>ᴛʜᴇ ᴍᴏᴠɪᴇ ʙᴏᴛ</b>.\nʜᴏᴘᴇ ʏᴏᴜ'ʀᴇ ᴅᴏɪɴɢ ᴡᴇʟʟ...</i>")
        await asyncio.sleep(0.4)
        await m.edit_text("👀")
        await asyncio.sleep(0.5)
        await m.edit_text("⚡")
        await reacts(client, message)
        await asyncio.sleep(0.5)
        await m.edit_text("<b><i>ꜱᴛᴀʀᴛɪɴɢ...</i></b>")
        await asyncio.sleep(0.4)
        await m.delete()        
        m=await message.reply_sticker("CAACAgUAAxkBAAECWARmzhZHnxmFvDBdJPbEL0Pbs5oUsgACBxMAAr8wcFYDK-oDeSa1BR4E") 
        await asyncio.sleep(2)
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
     
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Mᴀᴋᴇ sᴜʀᴇ Bᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ Fᴏʀᴄᴇsᴜʙ ᴄʜᴀɴɴᴇʟ")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "❆ Jᴏɪɴ Oᴜʀ Bᴀᴄᴋ-Uᴘ Cʜᴀɴɴᴇʟ ❆", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**👉 पहले हमारे चेनल को जॉइन करे....😒\n👉 तभी मूवी मिलेगा....😏\n👉 फिर Try Again पर क्लिक करें....😎**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                    InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('🤞🏻 ᴇᴀʀɴ ᴍᴏɴᴇʏ 🤡', callback_data="shortlink_info"),
                    InlineKeyboardButton('♻️ ᴜᴘᴅᴀᴛᴇꜱ ♻️', callback_data='channels')
                ],[
                    InlineKeyboardButton('ɪɴsᴛᴀɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ 🌐', url=f'https://www.instagram.com/jaynath_vishwakarma_0143?igsh=MTZyMnBxYmJlaHRiZQ=='),
                    InlineKeyboardButton('ᴅᴏɴᴀᴛɪᴏɴ  💰', callback_data='donation')
                ],[
                    InlineKeyboardButton('📝 ᴄᴏᴍᴍᴀɴᴅꜱ 📝', callback_data='help'),
                    InlineKeyboardButton('🫠 ᴀʙᴏᴜᴛ 🫠', callback_data='about')
                ],[
                    InlineKeyboardButton('Tᴏᴘ Sᴇᴀʀᴄʜ 🔍', callback_data='topsearch'),
                    InlineKeyboardButton('✨ ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ✨', callback_data="premium_info")
                ],[
                    InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer')
                  ]]
        if IS_VERIFY or IS_SHORTLINK is True:
            buttons.append([
                InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer')
            ])
            buttons.append([
                InlineKeyboardButton('✨ ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ ✨', callback_data="premium_info")
            ])
        reply_markup = InlineKeyboardMarkup(buttons)
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "<b><i>ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ☕</i></b>" 
        elif curr_time < 17:
            gtxt = "<b><i>ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ 🌗</i></b>" 
        elif curr_time < 21:
            gtxt = "<b><i>ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌇</i></b>"
        else:
            gtxt = "<b><i>ɢᴏᴏᴅ ɴɪɢʜᴛ 🥱</i></b>"
        m=await message.reply_sticker("CAACAgUAAxkBAAECWARmzhZHnxmFvDBdJPbEL0Pbs5oUsgACBxMAAr8wcFYDK-oDeSa1BR4E") 
        await asyncio.sleep(2)
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if message.command[1] == "topsearch":
        m = await message.reply_text(f"<b>Finding Movie's List For You...😘</b>")
        top_messages = await db3.get_top_messages(30)

        truncated_messages = set()  # Use a set instead of a list
        for msg in top_messages:
            if len(msg) > 30:
                truncated_messages.add(msg[:30 - 3].lower().title() + "...")  # Convert to lowercase, capitalize and add to set
            else:
                truncated_messages.add(msg.lower().title())  # Convert to lowercase, capitalize and add to set

        keyboard = []
        for i in range(0, len(truncated_messages), 2):
            row = list(truncated_messages)[i:i+2]  # Convert set to list for indexing
            keyboard.append(row)
    
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, placeholder="Most searches of the day")
        sf=await message.reply_text(f"<b>ʜᴇʀᴇ ɪs ᴛʜʀ ʟɪsᴛ ᴏғ ᴍᴏᴠɪᴇ's ɴᴀᴍᴇ 👇👇</b>", reply_markup=reply_markup)
        await m.delete()
        await asyncio.sleep(60*60) 
        await sf.delete()
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("<b>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("Fᴀɪʟᴇᴅ")
                return await client.send_message(LOG_CHANNEL, "Uɴᴀʙʟᴇ Tᴏ Oᴘᴇɴ Fɪʟᴇ.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            chk = await check_premium_for_quality(message, title)
            if chk == False:
                continue
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                       ],[
                          InlineKeyboardButton('😍 Gʀᴏᴜᴘ 😍', url=GRP_LNK),
                          InlineKeyboardButton('🍀 Cʜᴀɴɴᴇʟ 🍀', url=CHNL_LNK)
                         ]
                        ]
                    )
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                          
                       ],[
                          InlineKeyboardButton('😍 Gʀᴏᴜᴘ 😍', url=GRP_LNK),
                          InlineKeyboardButton('🍀 Cʜᴀɴɴᴇʟ 🍀', url=CHNL_LNK)
                         ]
                        ]
                    )
                )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("<b>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()
        
    elif data.split("-", 1)[0] == "reff":
        user_id = int(data.split("-", 1)[1])
        if await db.has_premium_access(message.from_user.id):
            await message.reply("ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ 🌟💝,\nʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴏᴘᴇɴ ᴛʜᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋ. 🔗🚫") 
            return
        elif await db.save_invites(message.from_user.id):
            await message.reply("ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ɪɴᴠɪᴛᴇᴅ 🙅")
            return
        else:
            if await referal_add_user(user_id, message.from_user.id):
                await message.reply(f"<b>ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ ᴜsɪɴɢ ᴛʜᴇ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ ᴏғ ᴜsᴇʀ ᴡɪᴛʜ ɪᴅ {user_id},\n\nᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs 🎁🎉, ʏᴏᴜ ʜᴀᴠᴇ ɢᴏᴛ 1 ᴅᴀʏ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ᴛʀɪᴀʟ, ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴍᴏᴠɪᴇs ᴡɪᴛʜᴏᴜᴛ ᴀᴅs ғᴏʀ 1 ᴅᴀʏ.</b>") 
                await db.update_invited(message.from_user.id)
            num_referrals = await get_referal_users_count(user_id)
            await client.send_message(chat_id = user_id, text = "<b>{} sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴡɪᴛʜ ʏᴏᴜʀ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ\n\nᴛᴏᴛᴀʟ ʀᴇғᴇʀᴀʟs - {}</b>".format(message.from_user.mention, num_referrals))
            if await get_referal_users_count(user_id) == USERS_COUNT:
                await db.give_referal(user_id)
                await delete_all_referal_users(user_id)
                await client.send_message(chat_id = user_id, text = "<b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs 🎁🎉, ʏᴏᴜʀ ᴛᴏᴛᴀʟ ʀᴇғᴇʀʀᴀʟ ʜᴀs ʙᴇᴇɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.\n\nʏᴏᴜ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ ғᴏʀ 1 ᴍᴏɴᴛʜ</b>")
                return 
                
    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        fileid = data.split("-", 3)[3]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Iɴᴠᴀʟɪᴅ ʟɪɴᴋ ᴏʀ Exᴘɪʀᴇᴅ ʟɪɴᴋ !</b>",
                protect_content=True if PROTECT_CONTENT else False
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            if fileid == "send_all":
                btn = [[
                    InlineKeyboardButton("Gᴇᴛ Fɪʟᴇ", callback_data=f"checksub#send_all")
                ]]
                await verify_user(client, userid, token)
                await message.reply_text(
                    text=f"<b>Hᴇʏ {message.from_user.mention}, Yᴏᴜ ᴀʀᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ !\nNᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ғᴏʀ ᴀʟʟ ᴍᴏᴠɪᴇs ᴛɪʟʟ ᴛʜᴇ ɴᴇxᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴡʜɪᴄʜ ɪs ᴀғᴛᴇʀ 12 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ.</b>",
                    protect_content=True if PROTECT_CONTENT else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            btn = [[
                InlineKeyboardButton("Get File", url=f"https://telegram.me/{temp.U_NAME}?start=files_{fileid}")
            ]]
            await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, सफलतापूर्वक \nवेरिफाई हो गए हैं ! ✅\nअब आप 2 Days अनलिमिटेडमूवी ले सकते है।.</b>",
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await verify_user(client, userid, token)
            return
        else:
            return await message.reply_text(
                text="<b>Iɴᴠᴀʟɪᴅ ʟɪɴᴋ ᴏʀ Exᴘɪʀᴇᴅ ʟɪɴᴋ !</b>",
                protect_content=True if PROTECT_CONTENT else False
            )
    if data.startswith("Safaridev"):
        buttons = [[
                    InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ', url=f"https://t.me/Jaynath_Request_Group_bot")
                  ],[
                    InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=(SUBSCRIPTION),
            caption=script.PREMIUM_PM,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return  
    elif data.startswith("sendfiles"):
        chat_id = int("-" + file_id.split("-")[1])
        userid = message.from_user.id if message.from_user else None
        g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=allfiles_{file_id}")
        k = await client.send_message(chat_id=message.from_user.id,text=f"<b>Get All Files in a Single Click!!!\n\n📂 ʟɪɴᴋ ➠ : {g}\n\n<i>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 𝟷5 ᴍɪɴᴜᴛᴇs.</i></b>", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('📁 ᴍᴏᴠɪᴇ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📁', url=g)
                    ], [
                        InlineKeyboardButton('🤔 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🤔', url=await get_tutorial(chat_id))
                    ],[
                        InlineKeyboardButton("✨ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs : ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ✨", callback_data='seeplans')
                    ], [
                       InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer2')
                    ]
                ]
            )
        )
        await asyncio.sleep(900) 
        await k.edit_text("<b>Your message is successfully deleted!!!</b>")
        return
    elif data.startswith("short"):
        if await db.has_premium_access(message.from_user.id):
            files = await get_file_details(file_id)
            if not files:
                return await message.reply('<b><i>Nᴏ Sᴜᴄʜ Fɪʟᴇ Eᴇxɪsᴛ.</b></i>')
            filesarr = []
            for file in files:
                file_id = file.file_id
                files_ = await get_file_details(file_id)
                files = files_[0]
                title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))
                size=get_size(files.file_size)
                f_caption=files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))}"
            msg=await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup([[
                      InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")],
                      [InlineKeyboardButton('😍 Gʀᴏᴜᴘ 😍', url=GRP_LNK),
                      InlineKeyboardButton('🍀 Cʜᴀɴɴᴇʟ 🍀', url=CHNL_LNK)]]))
            del_msg=await message.reply("<b>⚠️ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 15 ᴍɪɴᴜᴛᴇs\n\nᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ sᴏᴍᴇᴡʜᴇʀᴇ ʙᴇғᴏʀᴇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ..</b>") 
            safari = msg
            await asyncio.sleep(900)
            await safari.delete() 
            await del_msg.edit_text("<b>ʏᴏᴜʀ ғɪʟᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀғᴛᴇʀ 15 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ 📢</b>")
            return 
        else:
            user = message.from_user.id
            if temp.SHORT.get(user)==None:
                await message.reply_text(text="<b><i>Nᴏ Sᴜᴄʜ Fɪʟᴇ Eᴇxɪsᴛ.</b></i>")
            else:
                chat_id = temp.SHORT.get(user)
            settings = await get_settings(chat_id)
            if settings['is_shortlink']:
                files_ = await get_file_details(file_id)
                files = files_[0]
                g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
                k = await client.send_message(chat_id=message.from_user.id,text=f"<b>📕Nᴀᴍᴇ ➠ : <code>{files.file_name}</code> \n\n🔗Sɪᴢᴇ ➠ : {get_size(files.file_size)}\n\n📂Fɪʟᴇ ʟɪɴᴋ ➠ : {g}\n\n<i>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 𝟷5 ᴍɪɴᴜᴛᴇs.</i></b>", 
                reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton('📂 ᴍᴏᴠɪᴇ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📂', url=g)], 
                            [InlineKeyboardButton('🤔 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🤔', url=await get_tutorial(chat_id))
                            ],[
                            InlineKeyboardButton("✨ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs : ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ✨", callback_data='seeplans')
                            ], [
                            InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer2')
                            ]]))
                await asyncio.sleep(900) 
                await k.edit_text("<b>Your message is successfully deleted!!!</b>")
                return
    elif data.startswith("all"):
        files = temp.GETALL.get(file_id)
        if not files:
            return await message.reply('<b><i>Nᴏ Sᴜᴄʜ Fɪʟᴇ Eᴇxɪsᴛ.</b></i>')
        filesarr = []
        non_480p_files = []
        for file in files:
            file_id = file.file_id
            files_ = await get_file_details(file_id)
            files1 = files_[0]
            title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))
            size=get_size(files1.file_size)
            f_caption=files1.caption
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))}"
           
            if not await db.has_premium_access(message.from_user.id) and send_count is not None and send_count >= 3:
                buttons = [[
                            InlineKeyboardButton('✨Bʏ Pʀᴇᴍɪᴜᴍ: Rᴇᴍᴏᴠᴇ Lɪᴍɪᴛᴇ 🚫✨', callback_data=f'seepl')
                          ]]
                reply_markup = InlineKeyboardMarkup(buttons)
                return await message.reply(f"<b>आपने Send All, बटन का 3 बार यूज कर चुके है, अब आप रात्रि 12 बजे के बाद फिर से 3 बार यूज कर सकते है\n\nअगर आप Send All, बटन का अनलिमिटेड यूज करना चाहते है तो\nइस bot का प्रीमियम ले सकते है सिर्फ 20₹ में\n💲By Premium Only 20₹ monthly.\n\nReset Time Count = {hours} hours, {minutes} minutes, and {seconds} seconds.</b>",
                reply_markup=reply_markup)
            if not await check_verification(client, message.from_user.id) and not await db.has_premium_access(message.from_user.id) and IS_VERIFY == True:
                btn = [[
                        InlineKeyboardButton("♻️ Vᴇʀɪғʏ ♻️", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                        InlineKeyboardButton("⚠️ Hᴏᴡ Tᴏ Vᴇʀɪғʏ ⚠️", url=HOW_TO_VERIFY)
                        ],[
                        InlineKeyboardButton("✨ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs : ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ✨", callback_data='seeplans')
                        ], [
                        InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer2')
                        ]]
                await message.reply_text(
                    text="<b>हर दो दिन में 10 सेकंड का वेरिफिकेशन जरूरी हे !\nJust 10second Bro 🥲\nAfter Get Unlimited Movies...✅</b>",
                    protect_content=True if pre == 'filep' else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            if "480p" in files1.file_name or await db.has_premium_access(message.from_user.id):
                await db.update_files(message.from_user.id, "send_all", send_count + 1)
                await db.update_files(message.from_user.id, "lifetime_files", lifetime_files + 10)
                files_count=await db.files_count(message.from_user.id, "send_all")
                if not await db.has_premium_access(message.from_user.id):
                    f_caption += f"<b>\n\nSᴇɴᴅ Bᴜᴛᴛᴏɴ Lɪᴍɪᴛ : {files_count}/3</b>"
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if pre == 'filep' else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                       ],[
                          InlineKeyboardButton('😍 Gʀᴏᴜᴘ 😍', url=GRP_LNK),
                          InlineKeyboardButton('🍀 Cʜᴀɴɴᴇʟ 🍀', url=CHNL_LNK)],
                          [InlineKeyboardButton('✨Bʏ Pʀᴇᴍɪᴜᴍ: Rᴇᴍᴏᴠᴇ Lɪᴍɪᴛᴇ 🚫✨', callback_data=f'seepl')
                         ]
                        ]
                    )
                )
                filesarr.append(msg)
            else:
                non_480p_files.append(files1.file_name)
        if non_480p_files:
            await message.reply(f"File Name: {title}\n\nYou Can Only Access 480p Quality Files !To Get All Quality Files You Need To Take Premium Subscription !\n\nआप केवल 480p Quality वाली फ़ाइलों ही ले सकते हैं! सभी Quality वाली फ़ाइलें प्राप्त करने के लिए आपको Premium लेनी होगी!")
        k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie Files/Videos will be deleted in <b><u>10 mins</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this ALL Files/Videos to your Saved Messages and Start Download there</i></b>")
        for x in filesarr:
            await asyncio.sleep(300)
            await x.delete()
        await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
        return
    elif data.startswith("files"):
        if await db.has_premium_access(message.from_user.id):
            files = await get_file_details(file_id)
            if not files:
                return await message.reply('<b><i>Nᴏ Sᴜᴄʜ Fɪʟᴇ Eᴇxɪsᴛ.</b></i>')
            filesarr = []
            for file in files:
                file_id = file.file_id
                files_ = await get_file_details(file_id)
                files = files_[0]
                title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))
                size=get_size(files.file_size)
                f_caption=files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))}"
                await db.update_files(message.from_user.id, "files_count", files_counts + 1)
                await db.update_files(message.from_user.id, "lifetime_files", lifetime_files + 1)
                if not await db.has_premium_access(message.from_user.id) and files_counts is not None and files_counts >= 15:
                    buttons = [[
                                InlineKeyboardButton('✨Bʏ Pʀᴇᴍɪᴜᴍ: Rᴇᴍᴏᴠᴇ Lɪᴍɪᴛᴇ 🚫✨', callback_data=f'seepl')
                              ]]
                    reply_markup = InlineKeyboardMarkup(buttons)
                    return await message.reply(f"<b>आप इस bot से डेली 15 फाइल ले सकते है\n\nआज आपने 15 फाइल ले चुके हैं\n\nNote: = रात्रि 12 बजे के बाद फिर से 15 फाइल से सकते है\n\nअनलिमिटेड फाइल लेने के लिए प्रिमियम इस bot का खरीदे सिर्फ 20₹ में\n💲By Premium Only 20₹ monthly.\n\nReset Time Count = {hours} hours, {minutes} minutes, {seconds} seconds.</b>",
                    reply_markup=reply_markup)
            
            files_count=await db.files_count(message.from_user.id, "files_count")
            if not await db.has_premium_access(message.from_user.id):
                f_caption += f"<b>\n\nDᴀɪʟʏ Fɪʟᴇ Lɪᴍɪᴛ: {files_count}/15</b>"
            msg=await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup([[
                      InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")],
                      [InlineKeyboardButton('😍 Gʀᴏᴜᴘ 😍', url=GRP_LNK),
                      InlineKeyboardButton('🍀 Cʜᴀɴɴᴇʟ🍀', url=CHNL_LNK)],
                      [InlineKeyboardButton('✨Bʏ Pʀᴇᴍɪᴜᴍ: Rᴇᴍᴏᴠᴇ Lɪᴍɪᴛᴇ 🚫✨', callback_data=f'seepl')]]))
            del_msg=await message.reply("<b>⚠️ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 15 ᴍɪɴᴜᴛᴇs\n\nᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ sᴏᴍᴇᴡʜᴇʀᴇ ʙᴇғᴏʀᴇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ..</b>") 
            safari = msg
            await asyncio.sleep(900)
            await safari.delete() 
            await del_msg.edit_text("<b>ʏᴏᴜʀ ғɪʟᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀғᴛᴇʀ 15 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ 📢</b>")
            return 
        else:
            user = message.from_user.id
            if temp.SHORT.get(user)==None:
                await message.reply_text(text="<b><i>Nᴏ Sᴜᴄʜ Fɪʟᴇ Eᴇxɪsᴛ.</b></i>")
            else:
                chat_id = temp.SHORT.get(user)
                settings = await get_settings(chat_id)
                if settings['is_shortlink']:
                    files_ = await get_file_details(file_id)
                    files = files_[0]
                    g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
                    k = await client.send_message(chat_id=message.from_user.id,text=f"<b>📕Nᴀᴍᴇ ➠ : <code>{files.file_name}</code> \n\n🔗Sɪᴢᴇ ➠ : {get_size(files.file_size)}\n\n📂Fɪʟᴇ ʟɪɴᴋ ➠ : {g}\n\n<i>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 𝟷5 ᴍɪɴᴜᴛᴇs.</i></b>", 
                    reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton('📂 ᴍᴏᴠɪᴇ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📂', url=g)], 
                                [InlineKeyboardButton('🤔 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🤔', url=await get_tutorial(chat_id))
                                ],[
                                InlineKeyboardButton("✨ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs : ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ✨", callback_data='seeplans')
                                ], [
                                InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer2')
                                ]]))
                    await asyncio.sleep(900) 
                    await k.edit_text("<b>Your message is successfully deleted!!!</b>")
                    return
    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            await db.update_files(message.from_user.id, "files_count", files_counts + 1)
            await db.update_files(message.from_user.id, "lifetime_files", lifetime_files + 1)
            if not await db.has_premium_access(message.from_user.id) and files_counts is not None and files_counts >= 15:
                buttons = [[
                            InlineKeyboardButton('✨Bʏ Pʀᴇᴍɪᴜᴍ: Rᴇᴍᴏᴠᴇ Lɪᴍɪᴛᴇ 🚫✨', callback_data=f'seepl')
                          ]]
                reply_markup = InlineKeyboardMarkup(buttons)
                return await message.reply(f"<b>आप इस bot से डेली 15 फाइल ले सकते है\n\nआज आपने 15 फाइल ले चुके हैं\n\nNote: = रात्रि 12 बजे के बाद फिर से 15 फाइल से सकते है\n\nअनलिमिटेड फाइल लेने के लिए प्रिमियम इस bot का खरीदे सिर्फ 20₹ में\n💲By Premium Only 20₹ monthly.\n\nReset Time Count = {hours} hours, {minutes} minutes, {seconds} seconds.</b>",
                reply_markup=reply_markup)
            if IS_VERIFY and not await check_verification(client, message.from_user.id) and not await db.has_premium_access(message.from_user.id):
                btn = [[
                    InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                    InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
                ],[
                    InlineKeyboardButton("✨ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs : ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ✨", callback_data='seeplans')
                ], [
                    InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer2')
                ]]
                await message.reply_text(
                    text="<b>हर दो दिन में 10 सेकंड का वेरिफिकेशन जरूरी हे !\nJust 10second Bro 🥲\nAfter Get Unlimited Movies...✅</b>",
                    protect_content=True if PROTECT_CONTENT else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup(
                    [
                     [
                      InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
              
                   ],[
                      InlineKeyboardButton('😍 Gʀᴏᴜᴘ😍', url=GRP_LNK),
                      InlineKeyboardButton('🍀 Cʜᴀɴɴᴇʟ 🍀', url=CHNL_LNK)],
                      [InlineKeyboardButton('✨Bʏ Pʀᴇᴍɪᴜᴍ: Rᴇᴍᴏᴠᴇ Lɪᴍɪᴛᴇ 🚫✨', callback_data=f'seepl')
                     ]
                    ]
                )
            )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('Linkz') and not x.startswith('{') and not x.startswith('Links') and not x.startswith('@') and not x.startswith('www'), file.file_name.split()))
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            files_count=await db.files_count(message.from_user.id, "files_count")
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                    if not await db.has_premium_access(message.from_user.id):
                        f_caption += f"<b>\n\nDᴀɪʟʏ Fɪʟᴇ Lɪᴍɪᴛ: {files_count}/15</b>"
                except:
                    return
            await msg.edit_caption(f_caption)
            del_msg=await message.reply("<b>⚠️ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 15 ᴍɪɴᴜᴛᴇs\n\nᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ sᴏᴍᴇᴡʜᴇʀᴇ ʙᴇғᴏʀᴇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ..</b>") 
            safari = msg
            await asyncio.sleep(900)
            await safari.delete() 
            await del_msg.edit_text("<b>ʏᴏᴜʀ ғɪʟᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀғᴛᴇʀ 15 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ 📢</b>")
            return
        except:
            pass
        return await message.reply('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
    files = files_[0]
    title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('Linkz') and not x.startswith('{') and not x.startswith('Links') and not x.startswith('@') and not x.startswith('www'), files.file_name.split()))
    size=get_size(files.file_size)
    f_caption=files.caption
    await db.update_files(message.from_user.id, "files_count", files_counts + 1)
    await db.update_files(message.from_user.id, "lifetime_files", lifetime_files + 1)
    files_count=await db.files_count(message.from_user.id, "files_count")
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            if not await db.has_premium_access(message.from_user.id):
                f_caption += f"<b>\n\nDᴀɪʟʏ Fɪʟᴇ Lɪᴍɪᴛ: {files_count}/15</b>"
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('Linkz') and not x.startswith('{') and not x.startswith('Links') and not x.startswith('@') and not x.startswith('www'), files.file_name.split()))}"
    if not await db.has_premium_access(message.from_user.id) and files_counts is not None and files_counts >= 15:
        buttons = [[
                    InlineKeyboardButton('✨Bʏ Pʀᴇᴍɪᴜᴍ: Rᴇᴍᴏᴠᴇ Lɪᴍɪᴛᴇ 🚫✨', callback_data=f'seepl')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(f"<b>आप इस bot से डेली 15 फाइल ले सकते है\n\nआज आपने 15 फाइल ले चुके हैं\n\nNote: = रात्रि 12 बजे के बाद फिर से 15 फाइल से सकते है\n\nअनलिमिटेड फाइल लेने के लिए प्रिमियम इस bot का खरीदे सिर्फ 20₹ में\n💲By Premium Only 20₹ monthly.\n\nReset Time Count = {hours} hours, {minutes} minutes, {seconds} seconds.</b>",
        reply_markup=reply_markup)
    if IS_VERIFY and not await check_verification(client, message.from_user.id) and not await db.has_premium_access(message.from_user.id):
        btn = [[
            InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
            InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
        ],[
            InlineKeyboardButton("✨ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs : ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ✨", callback_data='seeplans')
        ], [
            InlineKeyboardButton('🎁 ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ 🎁', callback_data='reffer2')
        ]]
        await message.reply_text(
            text="<b>हर दो दिन में 10 सेकंड का वेरिफिकेशन जरूरी हे !\nJust 10second Bro 🥲\nAfter Get Unlimited Movies...✅</b>",
            protect_content=True if PROTECT_CONTENT else False,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    msg=await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        reply_markup=InlineKeyboardMarkup(
            [
             [
             InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
              
           ],[
              InlineKeyboardButton('😍 Gʀᴏᴜᴘ 😍', url=GRP_LNK),
              InlineKeyboardButton('🍀 Cʜᴀɴɴᴇʟ🍀 ', url=CHNL_LNK)],
              [InlineKeyboardButton('✨Bʏ Pʀᴇᴍɪᴜᴍ: Rᴇᴍᴏᴠᴇ Lɪᴍɪᴛᴇ 🚫✨', callback_data=f'seepl')
             ]
            ]
        )
    )
    del_msg=await message.reply("<b>⚠️ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 15 ᴍɪɴᴜᴛᴇs\n\nᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ sᴏᴍᴇᴡʜᴇʀᴇ ʙᴇғᴏʀᴇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ..</b>") 
    safari = msg
    await asyncio.sleep(900)
    await safari.delete() 
    await del_msg.edit_text("<b>ʏᴏᴜʀ ғɪʟᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀғᴛᴇʀ 15 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ 📢</b>")


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴛʏᴘᴇ ᴏғ CHANNELS")

    text = '📑 **Iɴᴅᴇxᴇᴅ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.private)
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Pʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Rᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ /delete ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Tʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
            else:
                await msg.edit('Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'Tʜɪs ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ɪɴᴅᴇxᴇᴅ ғɪʟᴇs.\nDᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Yᴇs", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cᴀɴᴄᴇʟ", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer("Eᴠᴇʀʏᴛʜɪɴɢ's Gᴏɴᴇ")
    await message.message.edit('Sᴜᴄᴄᴇsғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ Aʟʟ Tʜᴇ Iɴᴅᴇxᴇᴅ Fɪʟᴇs.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Yᴏᴜ ᴀʀᴇ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ. Usᴇ /connect {message.chat.id} ɪɴ PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴘʀᴇsᴇɴᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ !", quote=True)
                return
        else:
            await message.reply_text("I'ᴍ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs !", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return
    
    settings = await get_settings(grp_id)

    try:
        if settings['max_btn']:
            settings = await get_settings(grp_id)
    except KeyError:
        await save_group_settings(grp_id, 'max_btn', False)
        settings = await get_settings(grp_id)
    if 'is_shortlink' not in settings.keys():
        await save_group_settings(grp_id, 'is_shortlink', False)
    else:
        pass

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Rᴇꜱᴜʟᴛ Pᴀɢᴇ',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Bᴜᴛᴛᴏɴ' if settings["button"] else 'Tᴇxᴛ',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Iᴍᴅʙ',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Wᴇʟᴄᴏᴍᴇ Msɢ',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Mᴀx Bᴜᴛᴛᴏɴs',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10' if settings["max_btn"] else f'{MAX_B_TN}',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'SʜᴏʀᴛLɪɴᴋ',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
            ],
        ]

        btn = [[
                InlineKeyboardButton("Oᴘᴇɴ Hᴇʀᴇ ↓", callback_data=f"opnsetgrp#{grp_id}"),
                InlineKeyboardButton("Oᴘᴇɴ Iɴ PM ⇲", callback_data=f"opnsetpm#{grp_id}")
              ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                text="<b>Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs ʜᴇʀᴇ ?</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Cʜᴇᴄᴋɪɴɢ ᴛᴇᴍᴘʟᴀᴛᴇ...")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Yᴏᴜ ᴀʀᴇ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ. Usᴇ /connect {message.chat.id} ɪɴ PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴘʀᴇsᴇɴᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ!!", quote=True)
                return
        else:
            await message.reply_text("I'ᴍ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("Nᴏ Iɴᴘᴜᴛ!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"Sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴇᴍᴘʟᴀᴛᴇ ғᴏʀ {title} ᴛᴏ:\n\n{template}")


@Client.on_message((filters.command(["request", "Request"]) | filters.regex("#request") | filters.regex("#Request")))
#@Client.on_message(filters.command('request') & filters.incoming & filters.text)
async def requests(client, message):
    search = message.text
    requested_movie = search.replace("/request", "").replace("/Request", "").strip()
    user_id = message.from_user.id
    if not requested_movie:
        await message.reply_text("🙅 (फिल्म रिक्वेस्ट करने के लिए कृपया फिल्म का नाम और साल साथ में लिखें\nकुछ इस तरह 👇\n<code>/request Pushpa 2021</code>")
        return
    await message.reply_text(text=f"✅ आपकी फिल्म <b> {requested_movie} </b> हमारे एडमिन के पास भेज दिया गया है.\n\n🚀 जैसे ही फिल्म अपलोड होती हैं हम आपको मैसेज देंगे.\n\n📌 ध्यान दे - एडमिन अपने काम में व्यस्त हो सकते है इसलिए फिल्म अपलोड होने में टाइम लग सकता हैं")
    await client.send_message(LOG_CHANNEL,f"📝 #REQUESTED_CONTENT 📝\n\nʙᴏᴛ - {temp.B_NAME}\nɴᴀᴍᴇ - {message.from_user.mention} (<code>{message.from_user.id}</code>)\nRᴇǫᴜᴇꜱᴛ - <code>{requested_movie}</code>",
    reply_markup=InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('Not Release📅', callback_data=f"not_release:{user_id}:{requested_movie}"),
        ],[
            InlineKeyboardButton('Already Available🕵️', callback_data=f"already_available:{user_id}:{requested_movie}"),
            InlineKeyboardButton('Not Available🙅', callback_data=f"not_available:{user_id}:{requested_movie}")
        ],[
            InlineKeyboardButton('Uploaded Done✅', callback_data=f"uploaded:{user_id}:{requested_movie}")
        ],[
            InlineKeyboardButton('Series Msg📝', callback_data=f"series:{user_id}:{requested_movie}"),
            InlineKeyboardButton('Spell Msg✍️', callback_data=f"spelling_error:{user_id}:{requested_movie}")
        ],[
            InlineKeyboardButton('⁉️ Close ⁉️', callback_data=f"close_data")]
        ]))

        
@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Usᴇʀs Sᴀᴠᴇᴅ Iɴ DB Aʀᴇ:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Yᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ sᴇɴᴅ ᴛᴏ {user.mention}.</b>")
            else:
                await message.reply_text("<b>Tʜɪs ᴜsᴇʀ ᴅɪᴅɴ'ᴛ sᴛᴀʀᴛᴇᴅ ᴛʜɪs ʙᴏᴛ ʏᴇᴛ!</b>")
        except Exception as e:
            await message.reply_text(f"<b>Eʀʀᴏʀ: {e}</b>")
    else:
        await message.reply_text("<b>Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴜsɪɴɢ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴄʜᴀᴛ ɪᴅ. Fᴏʀ ᴇɢ: /send ᴜsᴇʀɪᴅ</b>")
@Client.on_message(filters.command("ucast") & filters.user(5069888600))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Usᴇʀs Sᴀᴠᴇᴅ Iɴ DB Aʀᴇ:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Yᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ sᴇɴᴅ ᴛᴏ {user.mention}.</b>")
            else:
                await message.reply_text("<b>Tʜɪs ᴜsᴇʀ ᴅɪᴅɴ'ᴛ sᴛᴀʀᴛᴇᴅ ᴛʜɪs ʙᴏᴛ ʏᴇᴛ!</b>")
        except Exception as e:
            await message.reply_text(f"<b>Eʀʀᴏʀ: {e}</b>")
    else:
        await message.reply_text("<b>Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴜsɪɴɢ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴄʜᴀᴛ ɪᴅ. Fᴏʀ ᴇɢ: /send ᴜsᴇʀɪᴅ</b>")
@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘs. Iᴛ ᴏɴʟʏ ᴡᴏʀᴋs ᴏɴ ᴍʏ PM!</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Gɪᴠᴇ ᴍᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs.</b>")
    btn = [[
       InlineKeyboardButton("Yᴇs, Cᴏɴᴛɪɴᴜᴇ !", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("Nᴏ, Aʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ !", callback_data="close_data")
    ]]
    await message.reply_text(
        text="<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ? Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nNᴏᴛᴇ:- Tʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("shortlink"))
async def shortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴛʜɪꜱ ᴀɢᴀɪɴ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>ʜᴇʏ {message.from_user.mention}, ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋꜱ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        pass
    try:
        command, shortlink_url, api = data.split(" ")
    except:
        return await message.reply_text("<b>ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ !\nɢɪᴠᴇ ᴍᴇ ᴄᴏᴍᴍᴀɴᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ꜱʜᴏʀᴛɴᴇʀ ᴡᴇʙꜱɪᴛᴇ ᴀɴᴅ ᴀᴘɪ.\n\nꜰᴏʀᴍᴀᴛ : <code>/shortlink krishnalink.com c8dacdff6e91a8e4b4f093fdb4d8ae31bc273c1a</code>")
    reply = await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
    shortlink_url = re.sub(r"https?://?", "", shortlink_url)
    shortlink_url = re.sub(r"[:/]", "", shortlink_url)
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    await reply.edit_text(f"<b>✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ ꜱʜᴏʀᴛʟɪɴᴋ ꜰᴏʀ <code>{title}</code>.\n\nꜱʜᴏʀᴛʟɪɴᴋ ᴡᴇʙꜱɪᴛᴇ : <code>{shortlink_url}</code>\nꜱʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ : <code>{api}</code></b>")
 
@Client.on_message(filters.command("shortlink_off"))
async def offshortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴛʜɪꜱ ᴀɢᴀɪɴ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋꜱ ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        await save_group_settings(grpid, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
        return await message.reply_text("ꜱʜᴏʀᴛʟɪɴᴋ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅɪꜱᴀʙʟᴇᴅ.")
    
@Client.on_message(filters.command("shortlink_on"))
async def onshortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴛʜɪꜱ ᴀɢᴀɪɴ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋꜱ ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        await save_group_settings(grpid, 'is_shortlink', True)
        ENABLE_SHORTLINK = True
        return await message.reply_text("ꜱʜᴏʀᴛʟɪɴᴋ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴇɴᴀʙʟᴇᴅ.")
    

@Client.on_message(filters.command("shortlink_info"))
async def ginfo(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>{message.from_user.mention},\n\nᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    chat_id=message.chat.id
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        settings = await get_settings(chat_id) #fetching settings for group
        if 'shortlink' in settings.keys() and 'tutorial' in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            st = settings['tutorial']
            return await message.reply_text(f"<b><u>ᴄᴜʀʀᴇɴᴛ  ꜱᴛᴀᴛᴜꜱ<u> 📊\n\nᴡᴇʙꜱɪᴛᴇ : <code>{su}</code>\n\nᴀᴘɪ : <code>{sa}</code>\n\nᴛᴜᴛᴏʀɪᴀʟ : {st}</b>", disable_web_page_preview=True)
        elif 'shortlink' in settings.keys() and 'tutorial' not in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            return await message.reply_text(f"<b><u>ᴄᴜʀʀᴇɴᴛ  ꜱᴛᴀᴛᴜꜱ<u> 📊\n\nᴡᴇʙꜱɪᴛᴇ : <code>{su}</code>\n\nᴀᴘɪ : <code>{sa}</code>\n\nᴜꜱᴇ /set_tutorial ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ꜱᴇᴛ ʏᴏᴜʀ ᴛᴜᴛᴏʀɪᴀʟ.")
        elif 'shortlink' not in settings.keys() and 'tutorial' in settings.keys():
            st = settings['tutorial']
            return await message.reply_text(f"<b>ᴛᴜᴛᴏʀɪᴀʟ : <code>{st}</code>\n\nᴜꜱᴇ  /shortlink  ᴄᴏᴍᴍᴀɴᴅ  ᴛᴏ  ᴄᴏɴɴᴇᴄᴛ  ʏᴏᴜʀ  ꜱʜᴏʀᴛɴᴇʀ</b>")
        else:
            return await message.reply_text("ꜱʜᴏʀᴛɴᴇʀ ᴀɴᴅ ᴛᴜᴛᴏʀɪᴀʟ ᴀʀᴇ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ.\n\nᴄʜᴇᴄᴋ /set_tutorial  ᴀɴᴅ  /shortlink  ᴄᴏᴍᴍᴀɴᴅ.")

@Client.on_message(filters.command("set_tutorial"))
async def settutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋꜱ ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        pass
    if len(message.command) == 1:
        return await message.reply("<b>ɢɪᴠᴇ ᴍᴇ ᴀ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.\n\nᴜꜱᴀɢᴇ : /set_tutorial <code>https://t.me/HowToOpenHP</code></b>")
    elif len(message.command) == 2:
        reply = await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
        tutorial = message.command[1]
        await save_group_settings(grpid, 'tutorial', tutorial)
        await save_group_settings(grpid, 'is_tutorial', True)
        await reply.edit_text(f"<b>✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴜᴛᴏʀɪᴀʟ\n\nʏᴏᴜʀ ɢʀᴏᴜᴘ : {title}\n\nʏᴏᴜʀ ᴛᴜᴛᴏʀɪᴀʟ : <code>{tutorial}</code></b>")
    else:
        return await message.reply("<b>ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ɪɴᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ !\nᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ : /set_tutorial <code>https://t.me/HowToOpenHP</code></b>")

@Client.on_message(filters.command("remove_tutorial"))
async def removetutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋꜱ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        pass
    reply = await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
    await save_group_settings(grpid, 'is_tutorial', False)
    await reply.edit_text(f"<b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ ✅</b>")

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="<b><i>ʙᴏᴛ ɪꜱ ʀᴇꜱᴛᴀʀᴛɪɴɢ</i></b>", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("<b><i><u>ʙᴏᴛ ɪꜱ ʀᴇꜱᴛᴀʀᴛᴇᴅ</u> ✅</i></b>")
    os.execl(sys.executable, sys.executable, *sys.argv)
