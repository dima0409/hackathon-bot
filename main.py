from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram.constants import ChatAction
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_models import GigaChat
from config import TELEGRAM_TOKEN, GIGACHAT_TOKEN

chat = GigaChat(credentials=GIGACHAT_TOKEN, verify_ssl_certs=False)

history = {}

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("Info", callback_data='info')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Приветствую, искатель приключений!🧙‍\n️ Я - ваш верный помощник в этом хакатоне “Подземелья и Драконы”. Готов помочь вам с любыми задачами, будь то поиск информации, генерация идей или просто поддержка в трудную минуту. Давайте вместе создадим что-то удивительное!', reply_markup=reply_markup)

async def info(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text='Цель бота: Я - ваш верный помощник в этом хакатоне “Подземелья и Драконы”. Готов помочь вам с любыми задачами, будь то поиск информации, генерация идей или просто поддержка в трудную минуту.\n'
                                       ' Команды бота:\n `/start` — Запуск взаимодействия с ботом и получение приветственного сообщения.\n `/clear` — Очистка истории сообщений в группе (доступно только администратору).\n `/ai [промт]` — Использование гигачата для генерации ответов. Пример: `/ai Напиши шаблон для Telegram-бота`.\n'
                                       ' Исходный код этого бота можно найти в [ репозитории на GitHub](https://github.com/dima0409/hackathon-bot)',parse_mode='markdown' )# info

async def clear(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.type == 'group':
        if not update.effective_user.is_bot:
            if update.effective_user.id not in [i.user.id for i in await update.effective_chat.get_administrators()]:
                await update.message.reply_text("Ты не админ этого чата.")
                return

    if update.message.chat.id in history.keys():
        del history[update.message.chat.id]
    await update.message.reply_text("Очищено!")

async def generate_ai_response(update: Update, context: CallbackContext) -> None:
    uid = update.message.chat.id
    if uid not in history.keys():
        history[uid] = [
          SystemMessage(
            content="Ты бот-программист, который отвечает точно и помогает советами и написанием кода."
          )
        ]

    user_input = update.message.text
    history[uid].append(HumanMessage(user_input))
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    res = chat(history[uid])
    history[uid].append(AIMessage(res.content))
    await update.message.reply_text(res.content)

async def cmdai(update: Update, context: CallbackContext) -> None:
    uid = update.message.chat.id
    if uid not in history.keys():
        history[uid] = [
          SystemMessage(
            content="Ты бот-программист, который отвечает точно и помогает советами и написанием кода."
          )
        ]

    user_input = " ".join(context.args)
    history[uid].append(HumanMessage(user_input))
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    res = chat(history[uid])
    history[uid].append(AIMessage(res.content))
    await update.message.reply_text(res.content)

async def post_init(application: Application) -> None:
    print(application.bot.username)

def main() -> None:
    updater = Application.builder().post_init(post_init).token(TELEGRAM_TOKEN).build()

    updater.add_handler(CommandHandler("start", start))
    updater.add_handler(CommandHandler("clear", clear))
    updater.add_handler(CommandHandler("ai", cmdai))
    updater.add_handler(CallbackQueryHandler(info, pattern='^' + 'info' + '$'))
    updater.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_ai_response))

    updater.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
