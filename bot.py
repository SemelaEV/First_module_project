from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes

from credentials import ChatGPT_TOKEN, BOT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'ranslate': 'Русско-рандомный словарь 📝'   #это не описка, это RANDOM TRANSLATE
        # Добавить команду в меню можно так:
        # 'command': 'button text'

    })

### 1. *Эхо-бот*

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)


### 2. *"Рандомный факт"*
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('random')
    message = load_message('random')
    await send_image(update, context, 'random')
    message = await send_text(update, context, message)
    answer = await chat_gpt.send_question(prompt, "")
    await send_text_buttons(update, context, answer, {
        'random_more': 'Хочу еще интересный факт',
        'random_end': 'Больше не надо фактов'
    })


async def random_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'random'
    await update.callback_query.answer()
    cb = update.callback_query.data
    if cb == 'random_more':
        await random(update, context)
        # await send_text(update, context, 'Нажмите /random')
    else:
        await send_text(update, context, 'Нажмите /start')


### 3. *ChatGPT интерфейс*
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'gpt'
    prompt = load_prompt('gpt')
    message = load_message('gpt')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'gpt')
    await send_text(update, context, message)


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    message = await send_text(update, context, "Думаю над вопросом...")
    answer = await chat_gpt.add_message(text)
    # await message.edit_text(answer)
    await send_text_buttons(update, context, answer, {'stop': 'Закончить беседу'})


### 4. *"Диалог с известной личностью"*
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'talk'
    message = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, message, {
        'talk_cobain': 'Курт Кобейн',
        'talk_queen': 'Елизавета II',
        'talk_tolkien': 'Джон Толкиен',
        'talk_nietzsche': 'Фридрих Ницше',
        'talk_hawking': 'Стивен Хокинг'
    })


async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'talk'
    await update.callback_query.answer()
    cb = update.callback_query.data
    if cb == 'talk_cobain':
        person_info = 'talk_cobain'
        person_message = load_message('talk_cobain')
    elif cb == 'talk_queen':
        person_info = 'talk_queen'
        person_message = load_message('talk_queen')
    elif cb == 'talk_tolkien':
        person_info = 'talk_tolkien'
        person_message = load_message('talk_tolkien')
    elif cb == 'talk_nietzsche':
        person_info = 'talk_nietzsche'
        person_message = load_message('talk_nietzsche')
    elif cb == 'talk_hawking':
        person_info = 'talk_hawking'
        person_message = load_message('talk_hawking')

    global talk_prompt
    talk_prompt = load_prompt(person_info)
    chat_gpt.set_prompt(talk_prompt)
    await send_image(update, context, person_info)
    await send_text(update, context, person_message)


async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.send_question(talk_prompt, text)
    await send_text_buttons(update, context, answer, {'stop': 'Закончить беседу'})


### 5. *"Квиз"*
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('quiz')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'quiz')
    text = load_message('quiz')
    context.user_data['count'] = 0
    context.user_data['good'] = 0
    await send_text_buttons(update, context, text, {
        'quiz_prog': 'Программирование на языке Python',
        'quiz_math': 'Математические теории - теории алгоритмов, теории множеств и матанализа',
        'quiz_biology': 'Биология'
    })


async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'quiz'
    await update.callback_query.answer()
    cb = update.callback_query.data
    question = await chat_gpt.add_message(cb)
    await send_text(update, context, question)


async def quiz_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    result = await chat_gpt.add_message(answer)
    if result.startswith('Правильн'):
        context.user_data['good'] += 1
    context.user_data['count'] += 1

    count = context.user_data['count']
    good = context.user_data['good']

    result = f'{result}\n Количество попыток: {count}\n Правильных ответов: {good}'
    await send_text_buttons(update, context, result, {
        'q_next_question': 'Следующий вопрос',
        'q_change_theme': 'Сменить тему',
        'stop': 'Закончить'
    })


async def quiz_any_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    cb = update.callback_query.data
    if cb == 'q_next_question':
        message = await chat_gpt.add_message('quiz_more')
        await send_text(update, context, message)
    else:
        await send_text_buttons(update, context, 'На какую тему будем проверять знания:',
                                {'quiz_prog': 'Программирование на Python',
                                 'quiz_math': 'Математические теории',
                                 'quiz_biology': 'Биология',
                                 })


### 6. **Вот такой вот переводчик**
async def ranslate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'ranslate'
    prompt = load_prompt('ranslate')
    message = load_message('ranslate')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'ranslate')
    await send_text(update, context, message)


async def ranslate_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    message = await send_text(update, context, "Выбираю язык для перевода...")
    answer = await chat_gpt.add_message(text)
    await send_text_buttons(update, context, answer, {'stop': 'Закончить беседу'})


async def stop_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'talk':
        await talk_dialog(update, context)
    elif dialog.mode == 'quiz':
        await quiz_dialog(update, context)
    elif dialog.mode == 'ranslate':
        await ranslate_dialog(update, context)
    else:
        await echo(update, context)


dialog = Dialog()
dialog.mode = None
# Переменные можно определить, как атрибуты dialog

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('ranslate', ranslate))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(random_button, pattern='^random.*'))
app.add_handler(CallbackQueryHandler(talk_button, pattern='^talk.*'))
app.add_handler(CallbackQueryHandler(quiz_button, pattern='^quiz.*'))
app.add_handler(CallbackQueryHandler(quiz_any_buttons, pattern='^q_.*'))
app.add_handler(CallbackQueryHandler(stop_button, pattern='^stop.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
