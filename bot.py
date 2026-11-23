import os
import io
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Using Pollinations (free, no key) — swap for HF if preferred
def generate_image(prompt: str) -> bytes:
    # Pollinations: returns an image directly from URL
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
    params = {"width": 1024, "height": 1024, "nologo": "true"}
    resp = requests.get(url, params=params, timeout=120)
    resp.raise_for_status()
    return resp.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a text prompt and I'll generate an image!\n"
        "Example: `a cyberpunk cat riding a neon motorcycle`",
        parse_mode="Markdown",
    )

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    if not prompt:
        return

    status = await update.message.reply_text("🎨 Generating image, please wait...")

    try:
        image_bytes = generate_image(prompt)
        await update.message.reply_photo(photo=io.BytesIO(image_bytes), caption=f"Prompt: {prompt}")
        await status.delete()
    except Exception as e:
        logger.exception("Image generation failed")
        await status.edit_text(f"❌ Failed to generate image: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))
    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
