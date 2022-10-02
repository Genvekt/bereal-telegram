from typing import Dict

from telegram import Update
from telegram.ext import ContextTypes, JobQueue, Job
import random
from functools import partial
from datetime import timedelta, datetime, timezone

class Bot:
    def __init__(self, job_queue: JobQueue):
        self.job_queue = job_queue
        self.users = dict()
        self.running_jobs: Dict[str, Job] = dict()

    async def broadcast_reminder(self, context: ContextTypes.context, chat_id: int):
        # Не запускаться вне промежутка 10:00 - 20:00 МСК
        now = datetime.now(timezone.utc)
        if now.hour < 7 or now.hour > 17:
            return
        must_send = random.random() > 0.5
        if must_send and chat_id in self.users:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{' '.join(self.users[chat_id])}, как дела?"
            )

    async def when_next(self, update: Update, context: ContextTypes.context):
        chat_id = update.effective_chat.id
        if chat_id not in self.running_jobs:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Bereal бот еще не запущен. "
                     "Отправь /start_bereal, чтобы запуcтить."
            )
        else:
            job = self.running_jobs[chat_id]
            next_time = job.next_t + timedelta(hours=3)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Подброшу монетку {next_time.strftime('%H:%M:%S %d.%m.%y')}."
            )

    async def start(self, update: Update, context: ContextTypes.context):
        chat_id = update.effective_chat.id
        if chat_id in self.running_jobs:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Bereal бот уже запущен. "
                     "Для остановки используй /stop_bereal."
            )
        else:
            try:
                interval = int(context.args[0]) if len(context.args) > 0 else 60
            except ValueError:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Интервал должен быть указан в целых минутах. "
                         "Например чтобы подкидывать монетку каждый час, "
                         "отправть `/start_bereal 60`"
                )
                return
            job = self.job_queue.run_repeating(
                name=str(chat_id),
                callback=partial(self.broadcast_reminder, chat_id=chat_id),
                interval=interval*60,
                first=0
            )
            self.running_jobs[chat_id] = job
            await context.bot.send_message(
                chat_id=chat_id,
                text="Bereal бот запущен! Жди команды и делись моментом. "
                     f"Буду подкидывать монетку каждые {interval} минут."
            )

    async def stop(self, update: Update, context: ContextTypes.context):
        chat_id = update.effective_chat.id
        if chat_id in self.running_jobs:
            job = self.running_jobs.pop(chat_id)
            job.schedule_removal()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Bereal бот остановлен. Отправь /start_bereal, чтобы запустить снова."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Bereal бот еще не запущен. Отправь /start_bereal, чтобы запуcтить."
            )

    async def add_me(self, update: Update, context: ContextTypes.context):
        user = update.effective_user.name
        chat_id = update.effective_chat.id
        if chat_id not in self.users:
            self.users[chat_id] = set()
        if not user in self.users[chat_id]:
            self.users[chat_id].add(user)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Добавил {user} к участникам."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{user} уже участвует."
            )

    async def remove_me(self, update: Update, context: ContextTypes.context):
        user = update.effective_user.name
        chat_id = update.effective_chat.id
        if chat_id in self.users and user in self.users[chat_id]:
            self.users[chat_id].remove(user)
            if len(self.users[chat_id]) == 0:
                self.users.pop(chat_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Удалил {user} из участников."
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{user} и так не участвует."
            )

    async def list(self, update: Update, context: ContextTypes.context):
        chat_id = update.effective_chat.id
        if chat_id in self.users:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Все участники в этом чате: {', '.join(self.users[chat_id])}"
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"В этом чате пока никто не добавился ко мне. Каждый "
                     f"участник должен отправить команду /add_me для участия."
            )
