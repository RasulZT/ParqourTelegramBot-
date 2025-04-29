import asyncio
import logging

from aiogram import Bot, Dispatcher

from core.settings import settings
from core.handlers.basic import router
from core.handlers import user, basic, admin, support, contacts, my_data,message_handler
from core.handlers.support import sessions, answer
from aiogram.client.default import DefaultBotProperties
from core.middlewares.RestMiddleware import RestMiddleware
from core.middlewares.DeleteMessagesMiddleware import DeleteMessagesMiddleware
from core.utils.set_commands import set_commands
from core.handlers.websocket import connect as websockets_connect
bot = Bot(settings.bots.bot_token, default=DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher()


async def main():
    # Здесь MIDLEWARES
    rest_middleware = RestMiddleware(bot)
    chat_middleware = DeleteMessagesMiddleware(bot)

    # ТУТ КОРОЧЕ РЕГИСТРАЦИЯ ИХ
    dp.callback_query.middleware.register(rest_middleware)
    dp.callback_query.middleware.register(chat_middleware)
    dp.message.middleware.register(rest_middleware)
    dp.message.middleware.register(chat_middleware)

    # Мой обработчик комманд, сюда поступают команды
    dp.include_routers(basic.router, contacts.router, my_data.router,sessions.router,answer.router)

    await set_commands(bot)
    try:
        ws_task = asyncio.create_task(websockets_connect.connect(bot,chat_middleware))
        dp_task = asyncio.create_task(dp.start_polling(bot))
        await asyncio.gather(ws_task, dp_task)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"Exit")
