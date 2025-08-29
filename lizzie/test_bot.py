#!/usr/bin/env python3
"""
Простейший тестовый бот для диагностики Лиззи.
Если этот бот не работает - проблема в токене или окружении.
Если работает - проблема в main.py или lizzie.py
"""

import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Enable detailed logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple start handler."""
    logger.info(f"Start command from user {update.effective_user.id}")
    await update.message.reply_text("🔥 Test bot alive! Lizzie's token works!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple message handler."""
    user_id = update.effective_user.id
    text = update.message.text
    
    logger.info(f"Message from {user_id}: {text}")
    
    response = f"Echo: {text}\n\nBot is working! Time to debug main.py..."
    await update.message.reply_text(response)


def main():
    """Test bot main function."""
    
    token = os.getenv("LIZZIE_TOKEN")
    if not token:
        print("ERROR: LIZZIE_TOKEN not set")
        return
    
    openai_token = os.getenv("OPENAILIZZIE_TOKEN") 
    if not openai_token:
        print("ERROR: OPENAILIZZIE_TOKEN not set")
        return
        
    print(f"Testing with LIZZIE_TOKEN: ...{token[-4:]}")
    print(f"Testing with OPENAILIZZIE_TOKEN: ...{openai_token[-4:]}")
    
    try:
        app = ApplicationBuilder().token(token).build()
        
        app.add_handler(CommandHandler("start", handle_start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Starting test bot...")
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"Test bot failed: {e}")
        logger.error(f"Test bot failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
