import os
import logging
import threading
import re
import asyncio
from telegram import Update
from telegram.error import Conflict, TimedOut, NetworkError
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN, DOWNLOAD_DIR

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionary to track active downloads
active_downloads = {}

# Regex pattern for YouTube URLs
YOUTUBE_URL_PATTERN = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to YouTube Downloader Bot!\n\n"
        "Send me a YouTube link to download audio or video!\n\n"
        "Commands:\n"
        "/audio <url> - Download audio\n" 
        "/video <url> - Download video\n"
        "/stop - Cancel download"
    )

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /audio <YouTube URL>")
        return
    
    user_id = update.effective_user.id
    url = context.args[0]
    await process_audio(update, context, url, user_id)

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /video <YouTube URL>")
        return
    
    user_id = update.effective_user.id
    url = context.args[0]
    await process_video(update, context, url, user_id)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if YOUTUBE_URL_PATTERN.search(text):
        await process_audio(update, context, text, user_id)
    else:
        await update.message.reply_text("Please send a valid YouTube link.")

async def process_audio(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, user_id: int):
    await update.message.reply_text("⏳ Downloading audio...")
    cancel_flag = threading.Event()
    active_downloads[user_id] = cancel_flag
    
    try:
        from downloader import download_audio
        audio_file, title, elapsed_time = download_audio(url, cancel_flag)

        if os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file) / (1024 * 1024)
            if file_size > 50:
                await update.message.reply_text(f"❌ File too large ({file_size:.1f}MB). Max 50MB.")
                os.remove(audio_file)
            else:
                with open(audio_file, 'rb') as audio_f:
                    await update.message.reply_audio(
                        audio=audio_f,
                        caption=f"🎧 {title}"
                    )
                os.remove(audio_file)
                await update.message.reply_text(f"✅ Done in {elapsed_time:.1f}s")
        else:
            await update.message.reply_text("❌ Failed to download audio")
                
    except Exception as e:
        logger.error(f"Audio error: {e}")
        await update.message.reply_text("❌ Download failed")
    finally:
        active_downloads.pop(user_id, None)

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, user_id: int):
    await update.message.reply_text("⏳ Downloading video...")
    cancel_flag = threading.Event()
    active_downloads[user_id] = cancel_flag
    
    try:
        from downloader import download_video
        video_file, title, elapsed_time = download_video(url, cancel_flag)

        if os.path.exists(video_file):
            file_size = os.path.getsize(video_file) / (1024 * 1024)
            if file_size > 50:
                await update.message.reply_text(f"❌ File too large ({file_size:.1f}MB). Max 50MB.")
                os.remove(video_file)
            else:
                with open(video_file, 'rb') as video_f:
                    await update.message.reply_video(
                        video=video_f,
                        caption=f"🎥 {title}"
                    )
                os.remove(video_file)
                await update.message.reply_text(f"✅ Done in {elapsed_time:.1f}s")
        else:
            await update.message.reply_text("❌ Failed to download video")
                
    except Exception as e:
        logger.error(f"Video error: {e}")
        await update.message.reply_text("❌ Download failed")
    finally:
        active_downloads.pop(user_id, None)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cancel_flag = active_downloads.get(user_id)
    if cancel_flag:
        cancel_flag.set()
        await update.message.reply_text("⏹️ Download stopped")
    else:
        await update.message.reply_text("No active download to stop")

def main():
    # Create download directory
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Create bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio_command))
    app.add_handler(CommandHandler("video", video_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Start bot with POLLING (not webhook)
    print("✅ Bot is running with polling...")
    try:
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    except Conflict as e:
        print(f"❌ Conflict error: {e}")
        print("Please make sure only one bot instance is running")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    main()
