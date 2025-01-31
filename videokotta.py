import os 
import yt_dlp 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes 

BOT_TOKEN = "7849598490:AAGRurLhCpryCfQX46IEW8X2YptHoOLvTBA" 

def sanitize_filename(title):
    return "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip()

async def fetch_formats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    url = update.message.text 
    context.user_data["url"] = url 

    await update.message.reply_text("Checking formats...") 

    try: 
        ydl_opts = { 
            'quiet': True, 
            'nocheckcertificate': True,  # Bypass SSL 
            'http_headers': { 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', 
                'Accept-Language': 'en-US,en;q=0.9', 
            }, 
            'cookies': 'cookies.txt'  # Bypass restrictions 
        } 
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: 
            info = ydl.extract_info(url, download=False) 

            if 'formats' not in info: 
                await update.message.reply_text("No formats available.") 
                return 

        keyboard = [[InlineKeyboardButton("1080p", callback_data="1080p"), 
                     InlineKeyboardButton("720p", callback_data="720p"), 
                     InlineKeyboardButton("360p", callback_data="360p"), 
                     InlineKeyboardButton("MP3", callback_data="audio")]] 
        reply_markup = InlineKeyboardMarkup(keyboard) 

        await update.message.reply_text("Choose format:", reply_markup=reply_markup) 

    except yt_dlp.utils.DownloadError as e: 
        await update.message.reply_text(f"Error: {str(e)}") 

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    query = update.callback_query 
    await query.answer() 

    format_choice = query.data 
    url = context.user_data.get("url") 

    if not url: 
        await query.message.reply_text("No URL found.") 
        return 

    await query.message.reply_text(f"Downloading {format_choice}...") 

    download_options = { 
        'format': 'bestaudio' if format_choice == "audio" else f"bestvideo[height={format_choice[:-1]}]+bestaudio/best", 
        'outtmpl': f"downloads/%(title)s.mp4", 
        'merge_output_format': 'mp4',  # Ensure MP4 format 
        'quiet': True, 
        'nocheckcertificate': True, 
        'http_headers': { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', 
            'Accept-Language': 'en-US,en;q=0.9', 
            'Accept': '*/*', 
            'Connection': 'keep-alive', 
        }, 
        'cookies': 'cookies.txt'  # Use cookies for restricted videos 
    } 

    try: 
        with yt_dlp.YoutubeDL(download_options) as ydl: 
            info = ydl.extract_info(url, download=True) 
            file_path = ydl.prepare_filename(info).replace(".webm", ".mp4") 

        await query.message.reply_text("Download complete! Sending...") 
        await query.message.reply_document(document=open(file_path, 'rb')) 
        os.remove(file_path) 

    except yt_dlp.utils.DownloadError as e: 
        await query.message.reply_text(f"Download failed: {str(e)}") 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    await update.message.reply_text("Send a YouTube link to get format options.") 

def main(): 
    app = Application.builder().token(BOT_TOKEN).build() 

    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_formats)) 
    app.add_handler(CallbackQueryHandler(download_video)) 
    print("Bot is running...") 
    app.run_polling() 

if __name__ == "__main__": 
    main()
