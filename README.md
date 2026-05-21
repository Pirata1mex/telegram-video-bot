# 🤖 telegram-video-bot

Bot de Telegram para descargar videos de YouTube, TikTok, Instagram, Twitter/X y más, usando yt-dlp. El video se envía directo al chat de Telegram.

## Plataformas soportadas
- YouTube
- TikTok
- Instagram
- Twitter/X
- Facebook
- Y muchas más (soportadas por yt-dlp)

## Despliegue en Render
1. Fork este repositorio
2. Crea un Background Worker en Render
3. Agrega la variable de entorno `BOT_TOKEN` con el token de @BotFather
4. Deploy!

## Variables de entorno requeridas
| Variable | Descripción |
|---|---|
| `BOT_TOKEN` | Token del bot de Telegram (obtenido con @BotFather) |
