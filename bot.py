from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler

ASK_DAYS, ASK_SUBJECTS = range(2)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравствуйте! Этот Телеграмм бот поможет составить вам расписание.\nДля вызова доступных команд введите /help")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Список доступных команд:\n/timetable - Составить расписание\n/start - Запуск бота\n/help - Помощь\n/info - Информация\n/stop - Остановить бота\n/cancel - Закончить диалог")

# Обработчик команды /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Этот бот создан студентами группы AIN-1-24 Кыргызско-Германского института прикладной информатики Аймурок, Ангелиной и Яной в качестве курсовой работы, на тему:\n 'Приложение для генерации расписания занятий'")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот остановлен.")

async def timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите количество учебных дней")
    return ASK_DAYS

async def get_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text)
        if days <= 0:
            raise ValueError('Количество дней должно быть больше нуля')

        context.user_data['days'] = days
        await update.message.reply_text(f'Вы указали {days} дней. Теперь введите список предметов через запятую:')
        return ASK_SUBJECTS
    except ValueError:
        await update.message.reply_text('Пожалуйста, введите положительное целое число.')
        return ASK_DAYS

async def get_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        subjects = [subject.strip() for subject in update.message.text.split(',')]
        if not subjects or any(not s for s in subjects):
            await update.message.reply_text('Список предметов содержит пустые значения. Введите предметы через запятую.')
            return ASK_SUBJECTS

        context.user_data['subjects'] = subjects
        await update.message.reply_text(f'Вы указали следующие предметы:\n{", ".join(subjects)}\nСейчас я сгенерирую расписание...')

        days = context.user_data['days']
        schedule = {f'День {i + 1}': [] for i in range(days)}

        for i, subject in enumerate(subjects):
            day_index = i % days
            schedule[f'День {day_index + 1}'].append(subject)

        context.user_data['schedule'] = schedule

        schedule_text = '\n'.join([f'{day}: {", ".join(items) if items else "пусто"}' for day, items in schedule.items()])
        await update.message.reply_text(f'Ваше расписание:\n{schedule_text}')
        return ConversationHandler.END
    except ValueError as e:
        await update.message.reply_text(str(e))
        return ASK_SUBJECTS

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Диалог  завершён.')
    return ConversationHandler.END

# Основной код
def main():

    app = Application.builder().token("8123562078:AAGzcKg_pQHRp-fFAtFxv2MPSxTvKGUwcoE").build()


    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("stop", stop))
    conv_handler = ConversationHandler(
        entry_points = [CommandHandler("timetable", timetable)],
        states = {
            ASK_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_days)],
            ASK_SUBJECTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sub)],
        },
        fallbacks = [CommandHandler("cancel", cancel)],
    )

    # Запуск бота
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()