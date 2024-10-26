from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'main'
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓'
        # Добавить команду в меню можно так:
        # 'command': 'button text'

    })


dialog = Dialog()
dialog.mode = None
# Переменные можно определить, как атрибуты dialog

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(
    "7638121545:AAEkEnYr2HNESmDuW1dMdTgSuDJOOefS-g0").build()

app.add_handler(CommandHandler('start', start))
# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
