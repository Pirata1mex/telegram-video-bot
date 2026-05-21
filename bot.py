import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DOWNLOAD_DIR = '/tmp/videos'

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MAX_SIZE_MB = 50

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Hola! Soy un bot descargador de videos.\n\n'
        'Envíame un enlace de YouTube, TikTok, Instagram, Twitter/X, Facebook u otras plataformas '
        'y te enviaré el video directamente aquí.\n\n'
        'Compatible con más de 1000 sitios gracias a yt-dlp.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Uso:\n'
        '1. Envía un link de video\n'
        '2. Espera unos segundos\n'
        '3. Recibirás el video aquí mismo\n\n'
        'Plataformas soportadas: YouTube, TikTok, Instagram, Twitter/X, Facebook y más.'
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not url.startswith('http'):
        await update.message.reply_text('Por favor envía un enlace válido (debe comenzar con http)')
        return
    
    msg = await update.message.reply_text('⏳ Descargando video, por favor espera...')
    
    output_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo[ext=mp4][filesize<45M]+bestaudio[ext=m4a]/best[ext=mp4][filesize<45M]/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not filename.endswith('.mp4'):
                filename = os.path.splitext(filename)[0] + '.mp4'
        
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        if file_size > MAX_SIZE_MB:
            await msg.edit_text(f'El video es muy grande ({file_size:.1f} MB). El límite de Telegram es {MAX_SIZE_MB} MB.')
            os.remove(filename)
            return
        
        await msg.edit_text('✅ Video descargado! Enviando...')
        
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=f'🎬 {info.get("title", "Video")}'
            )
        
        await msg.delete()
        os.remove(filename)
        
    except yt_dlp.utils.DownloadError as e:
        logger.error(f'Error descargando: {e}')
        await msg.edit_text('❌ No pude descargar ese video. Verifica que el enlace sea válido y público.')
    except Exception as e:
        logger.error(f'Error inesperado: {e}')
        await msg.edit_text('❌ Ocurrió un error inesperado. Intenta con otro enlace.')

def main():
    if not BOT_TOKEN:
        raise ValueError('No se encontró BOT_TOKEN en las variables de entorno')
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    logger.info('Bot iniciado y corriendo...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
