import html
import json
import traceback
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bereal_telegram.settings import load_settings, Settings
from bereal_telegram.handlers import Bot
from functools import partial

import logging
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.context, developer_chat_id: int) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=developer_chat_id, text=message, parse_mode=ParseMode.HTML
    )


def main(settings: Settings):

    application = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).read_timeout(30).get_updates_read_timeout(60).build()
    bot = Bot(application.job_queue)

    start_handler = CommandHandler('start_bereal', bot.start)
    application.add_handler(start_handler)

    stop_handler = CommandHandler('stop_bereal', bot.stop)
    application.add_handler(stop_handler)

    add_me_handler = CommandHandler('add_me', bot.add_me)
    application.add_handler(add_me_handler)

    remove_me_handler = CommandHandler('remove_me', bot.remove_me)
    application.add_handler(remove_me_handler)

    list_handler = CommandHandler('list', bot.list)
    application.add_handler(list_handler)

    when_next_handler = CommandHandler('when_next', bot.when_next)
    application.add_handler(when_next_handler)

    application.add_error_handler(
        partial(error_handler, developer_chat_id=settings.DEVELOPER_CHAT_ID)
    )
    application.run_polling()


if __name__ == '__main__':
    main(settings=load_settings())
