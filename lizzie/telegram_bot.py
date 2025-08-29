"""Telegram bot interface for Lizzie.

This bot relays incoming Telegram messages to the Lizzie agent and
returns the resonance response.
"""

import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

import lizzie


async def _handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""

    if not update.message or not update.message.text:
        return

    response = await lizzie.chat(update.message.text)
    await update.message.reply_text(response)


def main() -> None:
    token = os.getenv("LIZZIE_TOKEN")
    if not token:
        raise RuntimeError("LIZZIE_TOKEN environment variable not set")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_message)
    )
    application.run_polling()


if __name__ == "__main__":
    main()
