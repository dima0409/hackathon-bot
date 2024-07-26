# hackathon-bot
Итоговая работа по буткемпу "AI-ARROW" трек senior

![Image alt](https://github.com/dima0409/hackathon-bot/blob/main/other/1.jpg)
## Цель:
Разработать Telegram бот, который будет ассистентом команды для хакатона. Бот должен с помощью LLM помогать команде формировать продукт, описывать задачи, подсказывать варианты решений, изучать неизвестные темы, помогать писать код, помогать готовиться к защите проект.
## Структура:
main.py - сам бот.

config.py - апи тг-бота и гигачата
```
TELEGRAM_TOKEN = 'token'

GIGACHAT_TOKEN = 'token(base64)'
```
## Команды бота:
`/start` — Запуск взаимодействия с ботом и получение приветственного сообщения.

`/clear` — Очистка истории сообщений в группе (доступно только администратору).

`/ai [промт]` — Использование гигачата для генерации ответов. Пример: `/ai Напиши шаблон для Telegram-бота`.
## Почему гигачат
1. Поддержка мультимодальных запросов: Гигачат может работать не только с текстом, но и с изображениями и голосовыми сообщениями. Это делает его более универсальным и удобным для пользователей.
2. Интерактивность и контекстуальность: Гигачат способен поддерживать длительные диалоги, сохраняя контекст беседы. Это особенно полезно для сложных задач, требующих последовательного общения.
3. Поддержка русского языка: Гигачат отлично понимает и отвечает на русском языке, что делает его идеальным выбором для русскоязычных пользователей.
4. Безопасность и конфиденциальность: Все данные пользователей защищены, и Гигачат соблюдает высокие стандарты конфиденциальности.

Метрика SBS

![Image alt](https://github.com/dima0409/hackathon-bot/blob/main/other/SBS.png)

Чтобы посчитать эту метрику, мы выбираем заранее фиксированный набор вопросов и генерируем на них ответы двумя моделями. После этого наши сотрудники выбирают, какая модель ответила лучше на каждый вопрос. Результатов у каждого сравнения может быть 4:

* Лучше ответила 1-ая модель (всего таких ответов good_a);
* Лучше ответила 2-ая модель (всего таких ответов good_b);
* Обе модели ответили хорошо (всего таких ответов both);
* Обе модели ответили плохо (всего таких ответов none).
> Информация была взята с [Habr SberDevices](https://habr.com/ru/companies/sberdevices/articles/790470/)
