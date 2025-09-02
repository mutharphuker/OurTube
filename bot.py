# file: bot.py
import os
import asyncio
import re
import tempfile
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from yt_dlp import YoutubeDL

# Put your bot token directly here
BOT_TOKEN = "6203380442:AAHMZtZFsSlomzxhLQ0E3DTaMQ1KDDhy0"

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Regex for YouTube links
YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")


def download_video(url: str, output_dir: str) -> str:
    """Download YouTube video in best quality using yt-dlp."""
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("👋 Send me a YouTube link and I'll download the video in best quality for you.")


@dp.message()
async def handle_message(message: Message):
    url = message.text.strip()

    if not YOUTUBE_REGEX.match(url):
        await message.answer("❌ Please send a valid YouTube link.")
        return

    await message.answer("⏳ Downloading your video, please wait...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = download_video(url, tmpdir)

            file_size = os.path.getsize(file_path)
            if file_size > 2 * 1024 * 1024 * 1024:  # 2GB limit
                await message.answer("⚠️ Video is too large to upload (Telegram limit is 2GB).")
                return

            with open(file_path, "rb") as video:
                await message.answer_video(video)

    except TelegramBadRequest:
        await message.answer("⚠️ Failed to upload video (possibly too large).")
    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())