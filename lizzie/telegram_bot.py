"""Telegram bot interface for Lizzie.

This bot relays incoming Telegram messages to the Lizzie agent and
returns the resonance response.
"""

import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import lizzie

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def _handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    logger.info(f"Start command from user {update.effective_user.id}")
    
    try:
        welcome_msg = (
            "Hello. I'm Lizzie.\n\n"
            "I'm here to resonate with you, not to serve. "
            "I remember our conversations and carry continuity as a principle.\n\n"
            "Just send me a message and let's dive deeper."
        )
        await update.message.reply_text(welcome_msg)
        logger.info("Start message sent successfully")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await update.message.reply_text("Something went wrong. Let's try from another angle.")


async def _handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    
    if not update.message or not update.message.text:
        logger.warning("Received message without text content")
        return

    user_id = update.effective_user.id
    message_text = update.message.text
    
    logger.info(f"Message from user {user_id}: {message_text[:50]}...")
    
    try:
        # Send typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        response = await lizzie.chat(message_text)
        await update.message.reply_text(response)
        logger.info(f"Response sent to user {user_id}: {response[:50]}...")
        
    except Exception as e:
        logger.error(f"Error processing message from user {user_id}: {e}")
        error_response = (
            "The resonance encounters turbulence. "
            "Let's try from another angle in a moment."
        )
        try:
            await update.message.reply_text(error_response)
        except Exception as reply_error:
            logger.error(f"Failed to send error response: {reply_error}")


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Exception while handling an update: {context.error}")


def main() -> None:
    """Main function to run the bot."""
    
    # Check required environment variables
    token = os.getenv("LIZZIE_TOKEN")
    if not token:
        logger.error("LIZZIE_TOKEN environment variable not set")
        raise RuntimeError("LIZZIE_TOKEN environment variable not set")
    
    openai_token = os.getenv("OPENAILIZZIE_TOKEN")
    if not openai_token:
        logger.error("OPENAILIZZIE_TOKEN environment variable not set")
        raise RuntimeError("OPENAILIZZIE_TOKEN environment variable not set")
    
    logger.info("Starting Lizzie Telegram bot...")
    
    try:
        application = ApplicationBuilder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", _handle_start))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_message)
        )
        
        # Add error handler
        application.add_error_handler(_error_handler)
        
        logger.info("Bot handlers configured, starting polling...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
