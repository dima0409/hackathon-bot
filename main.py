from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, error
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram.constants import ChatAction
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, FunctionMessage
from langchain_community.chat_models import GigaChat
from config import TELEGRAM_TOKEN, GIGACHAT_TOKEN
from easygoogletranslate import EasyGoogleTranslate
from googlesearch import search
from langchain.agents import AgentExecutor, create_gigachat_functions_agent
from langchain.tools import tool
from bs4 import BeautifulSoup
import requests, traceback
from typing import Optional, Union
import urllib.parse
import re
from langchain_community.document_loaders import UnstructuredURLLoader
from urllib3.exceptions import InsecureRequestWarning
import contextlib, warnings

old_merge_environment_settings = requests.Session.merge_environment_settings

@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except:
                pass

@tool
def url_loader(url: str) -> str:
  """
  Извлекает содержимое указанного URL и извлекает из него весь текст.

  Args:
    url: URL веб-страницы для получения.

  Returns:
    Строка, содержащая весь текст с веб-страницы.
  """
  try:
    with no_ssl_verification():
        loader = UnstructuredURLLoader(urls=[url])
        data = loader.load()
        print(data)
        return data[0].page_content

  except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
    return None



@tool
def translate_function(query: str, from_lang: str = None, to_lang: str = "ru") -> str:
    """
    Переводит текст с помощью Google Translate.

    Args:
        query (str): Текст для перевода.
        from_lang (str, optional): Язык исходного текста.
            Если не указан, язык определяется автоматически.
        to_lang (str, optional): Язык перевода.
            По умолчанию используется русский язык ("ru").

    Returns:
        str: Переведенный текст.

    Raises:
        ValueError: Если не удается определить язык исходного текста.

    Examples:
        >>> translate_function("Hello world", from_lang="en", to_lang="es")
        'Hola mundo'
        >>> translate_function("Bonjour le monde", to_lang="en")
        'Hello world'
    """
    return EasyGoogleTranslate(
        source_language=from_lang,
        target_language=to_lang,
        timeout=10
    ).translate(query)

@tool
def search_tool(query: str, lang: str = "ru") -> str:
    """
    Выполняет поиск в Google и возвращает результаты в виде форматированного текста.

    Args:
        query (str): Поисковый запрос.
        lang (str, optional): Язык поиска. По умолчанию используется русский язык ("ru").

    Returns:
        str: Форматированный текст с результатами поиска.
            Каждый результат содержит заголовок, описание и ссылку.

    Examples:
        >>> search_tool("python programming")
        'Python Programming: Learn Python Programming - Free Interactive Python Tutorial: ... (https://www.programiz.com/python-programming)'
        'Python Programming: Learn Python Programming - Free Interactive Python Tutorial: ... (https://www.programiz.com/python-programming)'
        'Python Programming: Python Tutorial - Learn Python Programming ... (https://www.w3schools.com/python/)'
        'Python Programming: Learn Python | Codecademy: ... (https://www.codecademy.com/learn/learn-python)'
        'Python Programming: Python Tutorial - Learn Python for Beginners ... (https://www.guru99.com/python-tutorial.html)'
    """
    results = []

    for i in search(query, advanced=True, num_results=5, lang=lang):
        results.append(f"{i.title}: {i.description} ({urllib.parse.unquote(i.url)})")

    return "\n".join(results)

tools = [translate_function, search_tool, url_loader]

prompt = open("prompt.txt",'r').read()

chat = GigaChat(credentials=GIGACHAT_TOKEN, verify_ssl_certs=False)

agent = create_gigachat_functions_agent(chat, tools)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

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

def genai(uid, uname, user_input):
    if uid not in history.keys():
        history[uid] = [
          SystemMessage(
            content=prompt #"Ты бот-программист, который отвечает точно и помогает советами и написанием кода."
          )
        ]
    form = f"{uname}: {user_input}"

    res = agent_executor.invoke(
    {
        "chat_history": history[uid],
        "input": form,
    }
    )['output']
    history[uid].append(HumanMessage(form))
    history[uid].append(AIMessage(res))
    print(user_input, res)

    return res

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
    uname = f"{update.effective_user.first_name} {update.effective_user.last_name} (Никнейм)" if update.effective_chat.type == 'group' else "Пользователь"
    user_input = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    res = genai(uid,uname,user_input)
    if len(res) == 0:
        await update.message.reply_text("GigaChat ответил СЛИШКОМ лаконично")
        return
    try:
        await update.message.reply_text(res,parse_mode='html')
    except error.BadRequest as e:
        traceback.print_exception(e)
        await update.message.reply_text(res)
    except Exception as e:
        traceback.print_exception(e)
        await update.message.reply_text("серьезная ошибка")

async def cmdai(update: Update, context: CallbackContext) -> None:
    uid = update.message.chat.id
    uname = f"{update.effective_user.first_name} {update.effective_user.last_name} (Никнейм)" if update.effective_chat.type == 'group' else "Пользователь"
    user_input = " ".join(context.args)

    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    res = genai(uid,uname,user_input)
    if len(res) == 0:
        await update.message.reply_text("GigaChat ответил СЛИШКОМ лаконично")
        return
    try:
        await update.message.reply_text(res,parse_mode='html')
    except error.BadRequest as e:
        await update.message.reply_text(res)
    except Exception as e:
        await update.message.reply_text("серьезная ошибка")

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
