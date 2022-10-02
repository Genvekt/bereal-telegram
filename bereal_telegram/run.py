from telegram.ext import ApplicationBuilder, CommandHandler
from bereal_telegram.settings import load_settings, Settings
from bereal_telegram.handlers import Bot


def main(settings: Settings):

    application = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()
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

    application.run_polling()


if __name__ == '__main__':
    main(settings=load_settings())
