import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import threading
import json

# Configuration file loading
with open('config.json', 'r') as f:
    DATA = json.load(f)

def getenv(var):
    return os.environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN")
api_hash = getenv("HASH")
api_id = getenv("ID")
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define Owner ID
OWNER_ID = int(getenv("OWNER_ID"))  # Add your Telegram user ID in the config.json or environment variables

# Authorized Users and Channels (Tracking users and channels)
AUTHORIZED_USERS = set(DATA.get("AUTHORIZED_USERS", []))  # Load from config.json as a set
AUTHORIZED_CHANNELS = set(DATA.get("AUTHORIZED_CHANNELS", []))  # Load from config.json as a set
TRACKING_CHANNEL = int(getenv("TRACKING_CHANNEL"))  # Load tracking channel ID dynamically

# Download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
    time.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# Upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
    time.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# Progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# Add authorized user dynamically
@bot.on_message(filters.command(["add_user"]))
def add_user(client, message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Only the bot owner can add new users.", reply_to_message_id=message.id)
        return

    try:
        user_id = int(message.command[1])
        AUTHORIZED_USERS.add(user_id)
        bot.send_message(message.chat.id, f"✅ User {user_id} has been successfully added to the authorized list.", reply_to_message_id=message.id)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Please provide a valid user ID. Use: /add_user <user_id>", reply_to_message_id=message.id)

# Remove authorized user dynamically
@bot.on_message(filters.command(["remove_user"]))
def remove_user(client, message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Only the bot owner can remove users.", reply_to_message_id=message.id)
        return

    try:
        user_id = int(message.command[1])
        if user_id in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(user_id)
            bot.send_message(message.chat.id, f"✅ User {user_id} has been removed from the authorized list.", reply_to_message_id=message.id)
        else:
            bot.send_message(message.chat.id, "❌ This user is not in the authorized list.", reply_to_message_id=message.id)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Please provide a valid user ID. Use: /remove_user <user_id>", reply_to_message_id=message.id)

# List all authorized users
@bot.on_message(filters.command(["list_users"]))
def list_users(client, message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Only the bot owner can view the authorized users list.", reply_to_message_id=message.id)
        return

    if not AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "ℹ️ No users are currently authorized.", reply_to_message_id=message.id)
    else:
        user_list = "\n".join(map(str, AUTHORIZED_USERS))
        bot.send_message(message.chat.id, f"✅ **Authorized Users:**\n{user_list}", reply_to_message_id=message.id)

# Check if user is authorized
def is_authorized(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "Sorry, you are not authorized to use this bot.")
        return False
    return True

# Check if channel is authorized
def is_channel_authorized(channel_id):
    if channel_id not in AUTHORIZED_CHANNELS:
        return False
    return True

# Start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if not is_authorized(message):
        return
    bot.send_message(
        message.chat.id,
        f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by its post link__\n\n{USAGE}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Source Code", url="https://t.me/tgbin07")]]),
        reply_to_message_id=message.id
    )

@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if not is_authorized(message):
        return

    print(message.text)

    # Joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
        return

    # Getting message
    elif "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            username = datas[3]

            try:
                # Fetch channel info to get channel ID
                channel = bot.get_chat(username)
                channel_id = channel.id

                # Check if the channel is authorized
                if not is_channel_authorized(channel_id):
                    bot.send_message(message.chat.id, f"**Unauthorized channel**: {channel_id}", reply_to_message_id=message.id)
                    return

                # Fetch the message
                msg = bot.get_messages(channel_id, msgid)

                # Tracking who forwarded the message in your tracking channel
                bot.send_message(
                    TRACKING_CHANNEL,
                    f"**{message.from_user.mention}** forwarded a message from channel **{channel_id}**",
                    reply_to_message_id=message.id
                )

                if '?single' not in message.text:
                    bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                else:
                    bot.copy_media_group(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)

            except:
                bot.send_message(message.chat.id, f"**Error** : __Unable to fetch the message__.", reply_to_message_id=message.id)

            # Wait time
            time.sleep(3)
# handle private
def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int):
		msg: pyrogram.types.messages_and_media.message.Message = acc.get_messages(chatid,msgid)
		msg_type = get_message_type(msg)

		if "Text" == msg_type:
			bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
			return

		smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
		dosta = threading.Thread(target=lambda:downstatus(f'{message.id}downstatus.txt',smsg),daemon=True)
		dosta.start()
		file = acc.download_media(msg, progress=progress, progress_args=[message,"down"])
		os.remove(f'{message.id}downstatus.txt')

		upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',smsg),daemon=True)
		upsta.start()
		
		if "Document" == msg_type:
			try:
				thumb = acc.download_media(msg.document.thumbs[0].file_id)
			except: thumb = None
			
			bot.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
			if thumb != None: os.remove(thumb)

		elif "Video" == msg_type:
			try: 
				thumb = acc.download_media(msg.video.thumbs[0].file_id)
			except: thumb = None

			bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
			if thumb != None: os.remove(thumb)

		elif "Animation" == msg_type:
			bot.send_animation(message.chat.id, file, reply_to_message_id=message.id)
			   
		elif "Sticker" == msg_type:
			bot.send_sticker(message.chat.id, file, reply_to_message_id=message.id)

		elif "Voice" == msg_type:
			bot.send_voice(message.chat.id, file, caption=msg.caption, thumb=thumb, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])

		elif "Audio" == msg_type:
			try:
				thumb = acc.download_media(msg.audio.thumbs[0].file_id)
			except: thumb = None
				
			bot.send_audio(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])   
			if thumb != None: os.remove(thumb)

		elif "Photo" == msg_type:
			bot.send_photo(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)

		os.remove(file)
		if os.path.exists(f'{message.id}upstatus.txt'): os.remove(f'{message.id}upstatus.txt')
		bot.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
	try:
		msg.document.file_id
		return "Document"
	except: pass

	try:
		msg.video.file_id
		return "Video"
	except: pass

	try:
		msg.animation.file_id
		return "Animation"
	except: pass

	try:
		msg.sticker.file_id
		return "Sticker"
	except: pass

	try:
		msg.voice.file_id
		return "Voice"
	except: pass

	try:
		msg.audio.file_id
		return "Audio"
	except: pass

	try:
		msg.photo.file_id
		return "Photo"
	except: pass

	try:
		msg.text
		return "Text"
	except: pass

# USAGE instructions
USAGE = """**FOR PUBLIC CHATS**

__just send post/s link__

**FOR PRIVATE CHATS**

__first send invite link of the chat (unnecessary if the account of string session already member of the chat)
then send post/s link__

**FOR BOT CHATS**

__send link with '/b/', bot's username and message id, you might want to install some unofficial client to get the id like below__

```
https://t.me/b/botusername/4321
```

**MULTI POSTS**

__send public/private posts link as explained above with formate "from - to" to send multiple messages like below__

```
https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120
```

__note that space in between doesn't matter__
"""

# Infinitely polling
bot.run()
