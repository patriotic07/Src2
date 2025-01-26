
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

# Authorized Users (Tracking users)
AUTHORIZED_USERS = set(DATA.get("AUTHORIZED_USERS", []))  # Load from config.json as a set
TRACKING_CHANNEL = int(getenv("TRACKING_CHANNEL"))  # Load tracking channel ID dynamically

# Required Channel to Join
REQUIRED_CHANNEL = int(getenv("REQUIRED_CHANNEL"))  # Add your channel ID in config.json

# Registered Users (For total user count)
REGISTERED_USERS = set()

@bot.on_message(filters.private)
def register_user(client, message):
    if message.from_user.id not in REGISTERED_USERS:
        REGISTERED_USERS.add(message.from_user.id)

# Check if user has joined the required channel
def is_joined_channel(user_id):
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# Check if user is authorized
def is_authorized(message):
    if not is_joined_channel(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ You must join our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Join Channel", url=f"https://t.me/c/{REQUIRED_CHANNEL}")]]
            ),
            reply_to_message_id=message.id
        )
        return False

    if message.from_user.id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "Sorry, you are not authorized to use this bot.")
        return False
    return True

# Broadcast messages
@bot.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
def broadcast_message(client, message):
    if len(message.command) < 2:
        bot.send_message(message.chat.id, "❌ Please provide a message to broadcast.")
        return

    broadcast_text = message.text.split(" ", 1)[1]
    sent, failed = 0, 0

    for user_id in REGISTERED_USERS:
        try:
            bot.send_message(user_id, broadcast_text)
            sent += 1
        except Exception:
            failed += 1

    bot.send_message(
        message.chat.id,
        f"✅ Broadcast completed.

📤 Sent: {sent}
❌ Failed: {failed}"
    )

# Get total user count
@bot.on_message(filters.command("total_users") & filters.user(OWNER_ID))
def total_users(client, message):
    total = len(REGISTERED_USERS)
    bot.send_message(message.chat.id, f"👥 Total registered users: {total}")

# Start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if not is_joined_channel(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "If you want to use me, you need to join our channel first.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Join Channel", url=f"https://t.me/tgberlin07")]]
            ),
            reply_to_message_id=message.id
        )
        return

    REGISTERED_USERS.add(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by its post link__",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Source Code", url="https://t.me/tgberlin07")]])
    )
@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
	print(message.text)

	# joining chats
	if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

		if acc is None:
			bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
			return

		try:
			try: acc.join_chat(message.text)
			except Exception as e: 
				bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)
				return
			bot.send_message(message.chat.id,"**Chat Joined**", reply_to_message_id=message.id)
		except UserAlreadyParticipant:
			bot.send_message(message.chat.id,"**Chat alredy Joined**", reply_to_message_id=message.id)
		except InviteHashExpired:
			bot.send_message(message.chat.id,"**Invalid Link**", reply_to_message_id=message.id)

	# getting message
	elif "https://t.me/" in message.text:

		datas = message.text.split("/")
		temp = datas[-1].replace("?single","").split("-")
		fromID = int(temp[0].strip())
		try: toID = int(temp[1].strip())
		except: toID = fromID

		for msgid in range(fromID, toID+1):

			# private
			if "https://t.me/c/" in message.text:
				chatid = int("-100" + datas[4])
				
				if acc is None:
					bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
					return
				
				handle_private(message,chatid,msgid)
				# try: handle_private(message,chatid,msgid)
				# except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)
			
			# bot
			elif "https://t.me/b/" in message.text:
				username = datas[4]
				
				if acc is None:
					bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
					return
				try: handle_private(message,username,msgid)
				except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)

			# public
			else:
				username = datas[3]

				try: msg  = bot.get_messages(username,msgid)
				except UsernameNotOccupied: 
					bot.send_message(message.chat.id,f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
					return
				try:
					if '?single' not in message.text:
						bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
					else:
						bot.copy_media_group(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
				except:
					if acc is None:
						bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
						return
					try: handle_private(message,username,msgid)
					except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)

			# wait time
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


# infinty polling
bot.run()
