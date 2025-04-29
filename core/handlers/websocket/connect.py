import logging
import websockets
import asyncio
import json
from aiogram import Bot

from core.handlers.websocket.delete_ticket import ticket_delete
from core.handlers.websocket.ticket_main import ticket_main
from core.middlewares.DeleteMessagesMiddleware import DeleteMessagesMiddleware

from core.models.ticket import Ticket, TicketSerializer
from core.models.ticket_update import TicketUpdateData

from core.settings import settings
from core.utils.redis_client import redis


async def notify_ticket_section_update(bot: Bot, ticket_id: int, section: str, parking_name: str, asana_issue_id: str,
                                       group_chat_id: int, asana_project_id: str):
    ticket_url = f"https://app.asana.com/0/{asana_project_id}/{asana_issue_id}"

    message_text = (
        f"🌀 <b>Обновлён раздел тикета ID: {asana_issue_id}</b>\n"
        f"🏢 <b>Объект:</b> {parking_name}\n"
        f"📌 <b>Статус:</b> {section}\n\n"
        f"🔗 <a href=\"{ticket_url}\">Ссылка на тикет</a>"
    )

    await bot.send_message(
        chat_id=group_chat_id,
        text=message_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


async def connect(bot: Bot, delete_middleware: DeleteMessagesMiddleware):
    serializer = TicketSerializer()

    while True:
        try:
            async with websockets.connect(f"{settings.bots.ws_path}tickets/") as websocket:
                logging.info("websocket started")
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        # print(f"INFO DATA {data}")
                    except Exception as e:
                        logging.error(f"WebSocket not connected to server: {e}")
                        break
                    if (data.get("event") == 'ticket_deleted'):
                        ticket_del = serializer.from_dict(data["data"])
                        # print(f"Ticket info WS deleted: {ticket_del}")
                        await ticket_delete(bot, delete_middleware.chat_handler, ticket_del)
                    elif data.get("event") == 'ticket_updated':
                        ticket_data = data["data"]["full_ticket"]
                        print(f"Ticket_data_update: {data}")
                        changes = data["data"].get("changes", {})
                        ticket_id = data["data"]["id"]
                        serializer = TicketSerializer()
                        print(f"Ticket_data_update: {ticket_data}")

                        GROUP_ID = -1002571604070
                        topic_id = await redis.get(f"ticket:topic_id:{ticket_id}")

                        if not topic_id:
                            logging.warning(f"⚠️ Не найден topic_id для тикета #{ticket_id}")
                            return

                        asana_issue_id = ticket_data.get("asana_issue_id")
                        parking_name = ticket_data.get("parking").get("name")
                                                        # или другое поле, если parking отдельно
                        section = ticket_data.get("section", "Без раздела")
                        asana_project_id = "1209269161730390"  # 👉 сюда вставь реальный Project ID из Asana

                        await notify_ticket_section_update(
                            bot=bot,
                            ticket_id=ticket_id,
                            section=section,
                            parking_name=parking_name,
                            asana_issue_id=asana_issue_id,
                            group_chat_id=GROUP_ID,
                            asana_project_id=asana_project_id
                        )




                    else:
                        ticket_upd = serializer.from_dict(data)
                        print(f"Ticket info WS: {ticket_upd}")
                        try:
                            ticket_upd = serializer.from_dict(data)
                            await ticket_main(bot, delete_middleware.chat_handler, ticket_upd)
                        except Exception as e:
                            logging.error(f"WebSocket error: {e}")
                            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}", exc_info=True)
            await asyncio.sleep(5)
