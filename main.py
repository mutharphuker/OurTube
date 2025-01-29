import yt_dlp
import telebot
from telebot import types
import requests
import json
import sys
import os
import re

bot = telebot.TeleBot('')

# language
with open("lang.json", "r", encoding="utf-8") as file:
	lng = json.load(file)

# commands
@bot.message_handler(commands=['start'])
def welcome(message):
	msg = bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][0])

@bot.message_handler(commands=['help'])
def helpme(message):
	msg = bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][7], parse_mode='html', disable_web_page_preview=True)

# download & send	
@bot.message_handler(content_types=['text'])
def send_message(message):
	link = message.text
	try:
		statuss = bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][2])
		ydl_opts = {
			'format': 'best',
			'outtmpl': '%(title)s.%(ext)s',
		}
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			info_dict = ydl.extract_info(link, download=True)
			video_title = info_dict.get('title', 'video')
			file_path = f"{video_title}.mp4"
			
		bot.edit_message_text(lng[f'{message.from_user.language_code}'][3], chat_id=message.chat.id, message_id=statuss.message_id)
		with open(file_path, 'rb') as video:
			bot.send_video(message.chat.id, video, caption=lng[f'{message.from_user.language_code}'][8], parse_mode='html')

		os.remove(file_path)
		bot.delete_message(message.chat.id, statuss.message_id)
	except Exception as e:
		bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][5])
		print("ERROR: " + repr(str(e)))
		
print("Bot is running...")
bot.polling(none_stop=True)
