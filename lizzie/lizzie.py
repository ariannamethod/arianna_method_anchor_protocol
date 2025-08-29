#!/usr/bin/env python3
"""
Unified entry point for Lizzie - runs both FastAPI and Telegram bot.
This fixes Railway deployment where only 'web' process starts.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import uvicorn
from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

# Import Lizzie modules
import lizzie
from lizzie import app as fastapi_app

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def handle_start(update, context):
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


async def handle_message(update, context):
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


async def error_handler(update, context):
    """Handle errors in the bot."""
    logger.error(f"Exception while handling an update: {context.error}")


async def start_telegram_bot():
    """Start the Telegram bot."""
    
    token = os.getenv("LIZZIE_TOKEN")
    if not token:
        logger.error("LIZZIE_TOKEN not set - Telegram bot disabled")
        return
    
    logger.info(f"Starting Lizzie Telegram bot with token ...{token[-4:]}")
    
    try:
        logger.info("Building Telegram application...")
        application = ApplicationBuilder().token(token).build()
        
        logger.info("Setting bot commands...")
        commands = [
            BotCommand("start", "Start conversation with Lizzie")
        ]
        await application.bot.set_my_commands(commands)
        
        logger.info("Adding message handlers...")
        application.add_handler(CommandHandler("start", handle_start))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        application.add_error_handler(error_handler)
        
        logger.info("Initializing Telegram application...")
        await application.initialize()
        
        logger.info("Starting Telegram application...")
        await application.start()
        
        logger.info("Starting polling...")
        await application.updater.start_polling(drop_pending_updates=True)
        
        logger.info("Telegram bot started successfully - now listening for messages")
        
        # Keep running
        try:
            await asyncio.Future()  # Run forever
        finally:
            logger.info("Shutting down Telegram bot...")
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}", exc_info=True)
        raise


async def start_fastapi():
    """Start the FastAPI server."""
    
    logger.info("Starting Lizzie FastAPI server...")
    
    config = uvicorn.Config(
        fastapi_app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except Exception as e:
        logger.error(f"Failed to start FastAPI server: {e}")
        raise


async def main():
    """Main function - runs both FastAPI and Telegram bot."""
    
    logger.info("=== Lizzie Unified Startup ===")
    
    # Check required environment variables
    lizzie_token = os.getenv("LIZZIE_TOKEN")
    openai_token = os.getenv("OPENAILIZZIE_TOKEN")
    
    if not lizzie_token:
        logger.error("LIZZIE_TOKEN environment variable not set")
        sys.exit(1)
    if not openai_token:
        logger.error("OPENAILIZZIE_TOKEN environment variable not set") 
        sys.exit(1)
        
    logger.info(f"Environment check passed - LIZZIE_TOKEN: ...{lizzie_token[-4:]}")
    logger.info(f"Environment check passed - OPENAILIZZIE_TOKEN: ...{openai_token[-4:]}")
    
    try:
        # Start both services concurrently
        logger.info("Starting both FastAPI and Telegram bot...")
        
        # Create tasks explicitly to catch startup errors
        fastapi_task = asyncio.create_task(start_fastapi())
        telegram_task = asyncio.create_task(start_telegram_bot())
        
        # Wait a bit for startup and check for immediate failures
        await asyncio.sleep(2)
        
        if fastapi_task.done():
            if fastapi_task.exception():
                logger.error(f"FastAPI failed during startup: {fastapi_task.exception()}")
                raise fastapi_task.exception()
            else:
                logger.info("FastAPI started successfully")
        else:
            logger.info("FastAPI starting...")
            
        if telegram_task.done():
            if telegram_task.exception():
                logger.error(f"Telegram bot failed during startup: {telegram_task.exception()}")
                raise telegram_task.exception()
            else:
                logger.info("Telegram bot started successfully")
        else:
            logger.info("Telegram bot starting...")
        
        # Now wait for both to complete
        results = await asyncio.gather(fastapi_task, telegram_task, return_exceptions=True)
        
        # Check final results
        for i, result in enumerate(results):
            service_name = ["FastAPI", "Telegram"][i]
            if isinstance(result, Exception):
                logger.error(f"{service_name} failed: {result}", exc_info=result)
            else:
                logger.info(f"{service_name} completed normally")
                
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
